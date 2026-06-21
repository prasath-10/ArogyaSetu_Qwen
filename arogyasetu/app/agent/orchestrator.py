"""Core agent loop: takes a patient message, talks to Qwen, executes any tool calls,
and returns the final reply text."""

import json
from app.agent.qwen_client import chat
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.schemas import TOOLS
from app.tools.implementations import TOOL_REGISTRY


def run_agent(patient_message: str, conversation_history: list[dict] | None = None) -> str:
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
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
        reply = chat(messages, tools=TOOLS)

    return reply.content
