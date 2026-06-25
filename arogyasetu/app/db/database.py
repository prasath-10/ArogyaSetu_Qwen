from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

_db_url = settings.database_url

# Fall back to SQLite for local dev / CI when Postgres is not configured
try:
    engine = create_engine(_db_url)
    # Quick connection test
    with engine.connect() as conn:
        pass
except Exception:
    _db_url = "sqlite:///./arogya_dev.db"
    engine = create_engine(_db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency/helper to get db session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

