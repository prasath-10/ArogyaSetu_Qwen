from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from app.agent.orchestrator import run_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    reply_text = run_agent(request.message, session_id=session_id)
    
    reply_upper = reply_text.upper()
    severity = "LOW" # Default
    if "CRITICAL" in reply_upper:
        severity = "CRITICAL"
    elif "MODERATE" in reply_upper:
        severity = "MODERATE"
    elif "LOW" in reply_upper:
        severity = "LOW"
        
    return {
        "reply": reply_text,
        "severity": severity,
        "session_id": session_id
    }
