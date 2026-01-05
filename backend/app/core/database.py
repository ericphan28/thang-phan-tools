from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# Create database engine with SQLite support
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,          # Check connection before use
        pool_size=20,                 # Increased from 10 for large OCR workloads
        max_overflow=40,              # Total 60 connections max
        pool_timeout=30,              # Wait max 30s for available connection
        pool_recycle=3600,            # Recycle connections after 1 hour
        connect_args={
            "connect_timeout": 10     # DB connection timeout 10s
        }
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import all models to register them with SQLAlchemy
    from app.models import auth_models  # noqa: F401
    from app.models import models  # noqa: F401 - AI provider keys, usage logs
    from app.models import deployment  # noqa: F401 - Deployment tracking
    Base.metadata.create_all(bind=engine)
