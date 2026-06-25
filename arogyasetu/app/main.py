from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.whatsapp import router as whatsapp_router
from app.api.chat import router as chat_router
from app.db.database import engine
from app.db.models import Base
from app.db.seed import seed_data
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed data on startup
    try:
        Base.metadata.create_all(bind=engine)
        seed_data()
    except Exception as e:
        print(f"Database initialization failed: {e}")
    yield


app = FastAPI(
    title="Arogya Agent — AI Rural Healthcare Access", lifespan=lifespan
)

app.include_router(whatsapp_router, prefix="/api")
app.include_router(chat_router, prefix="/api")




@app.get("/health")
def health_check():
    return {"status": "ok", "service": "arogya-agent"}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
