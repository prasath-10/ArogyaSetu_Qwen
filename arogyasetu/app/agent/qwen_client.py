"""Thin wrapper around Qwen Cloud's OpenAI-compatible chat completion API."""

from openai import OpenAI
from app.config import settings

client = OpenAI(
    api_key=settings.qwen_api_key,
    base_url=settings.qwen_base_url,
)


def chat(messages: list[dict], tools: list[dict] | None = None, tool_choice: str = "auto"):
    """Send a chat completion request to Qwen Cloud, optionally with tool definitions."""
    kwargs = {
        "model": settings.qwen_model,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message
