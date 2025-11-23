"""Database session management."""

from .base import engine, SessionLocal, Base, import_models


def init_db():
    """Initialize database by creating all tables."""
    # Import models first to register them with Base
    import_models()
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (dependency for FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

