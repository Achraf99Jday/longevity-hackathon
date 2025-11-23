"""Enable WAL mode on SQLite database (run when API server is stopped)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.database.base import engine, DATABASE_URL
from sqlalchemy import text

if "sqlite" in DATABASE_URL:
    print("Enabling WAL mode on SQLite database...")
    try:
        with engine.connect() as conn:
            # Enable WAL mode
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.commit()
            
            # Verify
            result = conn.execute(text("PRAGMA journal_mode"))
            mode = result.fetchone()[0]
            print(f"✅ Journal mode set to: {mode}")
            
            # Set other optimizations
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA busy_timeout=60000"))
            conn.execute(text("PRAGMA wal_autocheckpoint=1000"))
            conn.commit()
            
            print("✅ WAL mode enabled successfully!")
            print("   The database can now handle concurrent reads and writes.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the API server is stopped.")
else:
    print("Not using SQLite, WAL mode not applicable.")


