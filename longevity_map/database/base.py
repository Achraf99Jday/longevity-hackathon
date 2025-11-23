"""Base database configuration."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
import yaml

# Load configuration
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
if not config_path.exists():
    config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

db_config = config.get("database", {})

# Create base for models
Base = declarative_base()

# Database URL
if db_config.get("type") == "postgresql":
    pg_config = db_config.get("postgresql", {})
    DATABASE_URL = (
        f"postgresql://{pg_config.get('user')}:{pg_config.get('password')}"
        f"@{pg_config.get('host')}:{pg_config.get('port')}/{pg_config.get('database')}"
    )
else:
    # SQLite default
    db_path = db_config.get("sqlite_path", "data/longevity_map.db")
    # For Vercel/serverless, use /tmp directory
    if os.environ.get("VERCEL") or "/tmp" in str(db_path):
        db_path = "/tmp/longevity_map.db"
    else:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path}"

# SQLite connection args for better concurrency
if "sqlite" in DATABASE_URL:
    connect_args = {
        "check_same_thread": False,
        "timeout": 60.0,  # Wait up to 60 seconds for lock
    }
    # Enable WAL mode for better concurrency (allows concurrent reads and writes)
    # Use NullPool to avoid connection pool issues with SQLite
    from sqlalchemy.pool import NullPool
    engine = create_engine(
        DATABASE_URL, 
        connect_args=connect_args, 
        poolclass=NullPool,  # No connection pooling for SQLite - each request gets new connection
        pool_pre_ping=False
    )
    
    # Enable WAL mode after engine creation - this allows concurrent reads/writes
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        try:
            cursor = dbapi_conn.cursor()
            # WAL mode allows multiple readers and one writer simultaneously
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
            cursor.execute("PRAGMA busy_timeout=60000")  # 60 second timeout
            cursor.execute("PRAGMA wal_autocheckpoint=1000")  # Auto-checkpoint
            cursor.close()
        except Exception:
            # If database is locked, these pragmas will fail
            # That's okay - the connection will still work with retries
            pass
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def import_models():
    """Import all models to register them with Base. Call this after Base is created."""
    # Import all models to register them with Base
    from longevity_map.models.problem import Problem  # noqa: F401
    from longevity_map.models.capability import Capability  # noqa: F401
    from longevity_map.models.resource import Resource  # noqa: F401
    from longevity_map.models.gap import Gap  # noqa: F401
    from longevity_map.models.mapping import ProblemCapabilityMapping, CapabilityResourceMapping  # noqa: F401

