"""Script to update data from all sources."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.agents.updater import Updater
from longevity_map.database.session import SessionLocal, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run data update."""
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Starting data update...")
    updater = Updater()
    
    db = SessionLocal()
    try:
        results = updater.update_all(db, days_back=30)
        logger.info(f"Update complete! Results: {results}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

