"""Core agent loop: takes a patient message, talks to Qwen, executes any tool calls,
and returns the final reply text."""

import json
import re
from app.agent.qwen_client import chat
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.schemas import TOOLS
from app.tools.implementations import TOOL_REGISTRY
from app.agent.memory import session_memory
from app.db.database import SessionLocal
from app.db.models import DoctorCase

# Severity tag pattern emitted by the model (see SYSTEM_PROMPT)
_SEVERITY_RE = re.compile(r"\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]", re.IGNORECASE)

EMERGENCY_ALERT_MSG = (
    "\n\n🚨 Doctor has been alerted and emergency services are on the way. "
    "Please stay calm and follow the safety instructions above."
)


def _extract_severity(text: str) -> str:
    """Return the severity string found in the agent reply, defaulting to LOW."""
    match = _SEVERITY_RE.search(text)
    if match:
        return match.group(1).upper()
    upper = text.upper()
    if "CRITICAL" in upper:
        return "CRITICAL"
    if "MODERATE" in upper:
        return "MODERATE"
    return "LOW"


def alert_emergency(patient_phone: str, symptoms: str) -> dict:
    """Create a DoctorCase entry for a critical case and return its details."""
    db = SessionLocal()
    try:
        case = DoctorCase(
            patient_phone=patient_phone,
            symptoms=symptoms,
            severity="critical",
            status="pending",
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return {
            "case_id": case.id,
            "patient_phone": case.patient_phone,
            "severity": case.severity,
            "status": case.status,
        }
    finally:
        db.close()


def run_agent(
    patient_message: str,
    session_id: str | None = None,
    conversation_history: list[dict] | None = None,
    patient_phone: str | None = None,
) -> str:
    """Run the Qwen agent loop.

    If session_id is specified, chat history is loaded from and persisted to Redis.
    """
    if session_id and conversation_history is None:
        conversation_history = session_memory.get_history(session_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": patient_message})

    reply = chat(messages, tools=TOOLS)

    # Tool-calling loop: keep executing tools until the model returns plain text
    while reply.tool_calls:
        messages.append(reply)
        for call in reply.tool_calls:
            fn_name = call.function.name
            fn_args = json.loads(call.function.arguments)
            result = TOOL_REGISTRY[fn_name](**fn_args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                }
            )
        reply = chat(messages, tools=TOOLS)

    reply_text: str = reply.content

    # ── Critical-case handling ───────────────────────────────────────
    severity = _extract_severity(reply_text)
    if severity == "CRITICAL":
        phone = patient_phone or session_id or "unknown"
        try:
            alert_emergency(patient_phone=phone, symptoms=patient_message)
        except Exception as exc:
            # Log but don't let DB errors block the patient reply
            print(f"[alert_emergency] failed to log case: {exc}")
        reply_text += EMERGENCY_ALERT_MSG

    if session_id:
        session_memory.add_message(session_id, "user", patient_message)
        session_memory.add_message(session_id, "assistant", reply_text)

    return reply_text

