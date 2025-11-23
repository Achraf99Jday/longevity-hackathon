"""Fetch real data from PubMed and other sources."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.database.session import SessionLocal, init_db
from longevity_map.agents.updater import Updater
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_real_data():
    """Fetch real data from all enabled sources."""
    init_db()
    db = SessionLocal()
    
    try:
        logger.info("Starting real data fetch from PubMed and other sources...")
        logger.info("This may take a few minutes...")
        
        updater = Updater()
        results = updater.update_all(db, days_back=90)  # Last 90 days
        
        logger.info("\n" + "="*50)
        logger.info("Data Fetch Results:")
        logger.info("="*50)
        for source, count in results.items():
            logger.info(f"  {source}: {count} items added")
        
        total = sum(results.values())
        logger.info(f"\nTotal: {total} items added")
        logger.info("="*50)
        
        if total > 0:
            logger.info("\n✅ Real data fetched successfully!")
            logger.info("   Refresh your browser to see the new data.")
        else:
            logger.warning("\n⚠️  No new data fetched. This could mean:")
            logger.warning("   - Sources are not configured (check config.yaml)")
            logger.warning("   - No new papers in the date range")
            logger.warning("   - API rate limits reached")
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_real_data()


