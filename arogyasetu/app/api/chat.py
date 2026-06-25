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
    
    import re
    
    reply_upper = reply_text.upper()
    severity = "LOW" # Default
    
    # Try explicit tags first
    match = re.search(r'\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]', reply_upper)
    if match:
        severity = match.group(1)
        # Strip the tag from the original reply text
        reply_text = re.sub(r'(?i)\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]', '', reply_text).strip()
    else:
        # Fallback to simple substring
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
