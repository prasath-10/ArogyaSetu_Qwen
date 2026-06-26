import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.whatsapp import router as whatsapp_router
from app.api.chat import router as chat_router
from app.api.cases import router as cases_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "arogya-agent"}


app.include_router(whatsapp_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(cases_router, prefix="/api")

# Mount static files LAST — the catch-all "/" mount must come after all API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
