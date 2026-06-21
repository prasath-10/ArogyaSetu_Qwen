from fastapi import FastAPI
from app.api.whatsapp import router as whatsapp_router

app = FastAPI(title="Arogya Agent — AI Rural Healthcare Access")

app.include_router(whatsapp_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "arogya-agent"}
