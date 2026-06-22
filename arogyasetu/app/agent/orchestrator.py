"""Core agent loop: takes a patient message, talks to Qwen, executes any tool calls,
and returns the final reply text."""

import json
from app.agent.qwen_client import chat
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.schemas import TOOLS
from app.tools.implementations import TOOL_REGISTRY
from app.agent.memory import session_memory


def run_agent(
    patient_message: str,
    session_id: str | None = None,
    conversation_history: list[dict] | None = None,
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

    if session_id:
        session_memory.add_message(session_id, "user", patient_message)
        session_memory.add_message(session_id, "assistant", reply.content)

    return reply.content
