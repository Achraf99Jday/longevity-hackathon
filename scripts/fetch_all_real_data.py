"""Fetch REAL data from ALL sources - this is the main script for hackathon."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.database.session import SessionLocal, init_db
from longevity_map.agents.updater import Updater
from longevity_map.data_sources import pubmed, clinical_trials, preprints
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_data_sources():
    """Test that all data sources can fetch real data."""
    logger.info("Testing data sources...")
    
    results = {}
    cutoff = datetime.now() - timedelta(days=90)
    
    # Test PubMed
    try:
        logger.info("Testing PubMed...")
        papers = pubmed.fetch_recent(cutoff, max_results=10)
        results['pubmed'] = len(papers)
        if papers:
            logger.info(f"  [OK] PubMed: {len(papers)} papers fetched")
            logger.info(f"  Example: {papers[0]['title'][:60]}... (PMID: {papers[0]['id']})")
        else:
            logger.warning("  [WARNING] PubMed: No papers fetched (check config)")
    except Exception as e:
        logger.error(f"  [ERROR] PubMed: {e}")
        results['pubmed'] = 0
    
    # Test ClinicalTrials
    try:
        logger.info("Testing ClinicalTrials.gov...")
        trials = clinical_trials.fetch_recent(cutoff, max_results=10)
        results['clinical_trials'] = len(trials)
        if trials:
            logger.info(f"  [OK] ClinicalTrials: {len(trials)} trials fetched")
            logger.info(f"  Example: {trials[0]['title'][:60]}... (NCT: {trials[0]['id']})")
        else:
            logger.warning("  [WARNING] ClinicalTrials: No trials fetched")
    except Exception as e:
        logger.error(f"  [ERROR] ClinicalTrials: {e}")
        results['clinical_trials'] = 0
    
    # Test Preprints
    try:
        logger.info("Testing Preprints (bioRxiv/medRxiv)...")
        preprints_data = preprints.fetch_recent(cutoff, max_results=10)
        results['preprints'] = len(preprints_data)
        if preprints_data:
            logger.info(f"  [OK] Preprints: {len(preprints_data)} preprints fetched")
            logger.info(f"  Example: {preprints_data[0]['title'][:60]}...")
        else:
            logger.warning("  [WARNING] Preprints: No preprints fetched")
    except Exception as e:
        logger.error(f"  [ERROR] Preprints: {e}")
        results['preprints'] = 0
    
    return results


def fetch_and_process_real_data():
    """Fetch real data from all sources and process it."""
    init_db()
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("FETCHING REAL DATA FROM ALL SOURCES")
        logger.info("=" * 60)
        
        # First, test that sources work
        test_results = test_data_sources()
        
        logger.info("\n" + "=" * 60)
        logger.info("PROCESSING DATA WITH GPT-4o")
        logger.info("=" * 60)
        logger.info("This will:")
        logger.info("  1. Fetch real papers/trials/preprints")
        logger.info("  2. Extract problems using GPT-4o")
        logger.info("  3. Identify capabilities using GPT-4o")
        logger.info("  4. Map to resources and identify gaps")
        logger.info("  5. Store everything in database")
        logger.info("\nThis may take 10-30 minutes depending on data volume...")
        
        updater = Updater()
        results = updater.update_all(db, days_back=90)
        
        logger.info("\n" + "=" * 60)
        logger.info("RESULTS:")
        logger.info("=" * 60)
        
        total = 0
        for source, count in results.items():
            logger.info(f"  {source}: {count} items processed")
            total += count
        
        logger.info(f"\nTotal: {total} items added to database")
        
        if total > 0:
            logger.info("\n[SUCCESS] Real data fetched and processed!")
            logger.info("  - Refresh your browser to see the new data")
            logger.info("  - All problems link to real sources (PubMed, etc.)")
        else:
            logger.warning("\n[WARNING] No data was added. Possible reasons:")
            logger.warning("  - All items already exist in database")
            logger.warning("  - Data sources not configured properly")
            logger.warning("  - API rate limits reached")
            logger.warning("  - Check config/config.yaml for data source settings")
        
        # Show some stats
        from longevity_map.models.problem import Problem
        from sqlalchemy import func
        
        total_problems = db.query(func.count(Problem.id)).scalar()
        pubmed_problems = db.query(func.count(Problem.id)).filter(Problem.source == 'pubmed').scalar()
        clinical_problems = db.query(func.count(Problem.id)).filter(Problem.source == 'clinical_trials').scalar()
        
        logger.info("\n" + "=" * 60)
        logger.info("DATABASE STATS:")
        logger.info("=" * 60)
        logger.info(f"  Total problems: {total_problems}")
        logger.info(f"  From PubMed: {pubmed_problems}")
        logger.info(f"  From ClinicalTrials: {clinical_problems}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_process_real_data()


