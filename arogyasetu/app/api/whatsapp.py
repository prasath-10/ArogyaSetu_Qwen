from fastapi import APIRouter, Request, Query, HTTPException
from app.config import settings
from app.agent.orchestrator import run_agent
import httpx

router = APIRouter()


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
):
    if hub_verify_token == settings.whatsapp_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    try:
        entry = body["entry"][0]["changes"][0]["value"]
        message = entry["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]
    except (KeyError, IndexError):
        return {"status": "ignored"}

    reply_text = run_agent(text, session_id=from_number)
    await send_whatsapp_message(from_number, reply_text)

    return {"status": "ok"}


async def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{settings.whatsapp_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)
