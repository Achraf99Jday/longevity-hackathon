"""Database session management."""

from .base import engine, SessionLocal, Base, import_models


def init_db():
    """Initialize database by creating all tables (with error handling)."""
    try:
        # Import models first to register them with Base
        import_models()
        # Create all tables (will fail gracefully if database is locked or unavailable)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Don't raise - database will be created on first use
        import logging
        logging.warning(f"Database initialization deferred: {e}")
        # Re-raise only if it's a critical error (not just a lock or missing file)
        error_str = str(e).lower()
        if "locked" not in error_str and "unable to open" not in error_str and "no such file" not in error_str:
            raise


def get_db():
    """Get database session (dependency for FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

