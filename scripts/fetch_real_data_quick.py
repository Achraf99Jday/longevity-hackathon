"""Quick test: Fetch 5 real papers from PubMed and process them."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.database.session import SessionLocal, init_db
from longevity_map.agents.problem_parser import ProblemParser
from longevity_map.agents.capability_extractor import CapabilityExtractor
from longevity_map.models.problem import Problem
from longevity_map.models.capability import Capability
from longevity_map.models.mapping import ProblemCapabilityMapping
from longevity_map.data_sources import pubmed
from datetime import datetime, timedelta
import logging
import time
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_database_available():
    """Check if database is available (not locked by another process)."""
    try:
        db = SessionLocal()
        # Try a simple query to check if database is accessible
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        if "locked" in str(e).lower():
            logger.error("\n" + "=" * 60)
            logger.error("DATABASE IS LOCKED!")
            logger.error("=" * 60)
            logger.error("The API server is likely running and has the database open.")
            logger.error("\nSOLUTION:")
            logger.error("  1. Stop the API server (Ctrl+C in the terminal running 'npm start')")
            logger.error("  2. Wait a few seconds")
            logger.error("  3. Run this script again")
            logger.error("\nOr run this script BEFORE starting the API server.")
            logger.error("=" * 60)
            return False
        raise


def fetch_and_process_quick():
    """Fetch 5 real papers and process them quickly."""
    # Check if API server is running
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            logger.error("\n" + "=" * 60)
            logger.error("API SERVER IS RUNNING!")
            logger.error("=" * 60)
            logger.error("The API server on port 8000 is running and has the database locked.")
            logger.error("\nSOLUTION:")
            logger.error("  1. Stop the API server (Ctrl+C in terminal running 'npm start')")
            logger.error("  2. Wait 2-3 seconds for database to unlock")
            logger.error("  3. Run this script again")
            logger.error("=" * 60)
            return
    except Exception:
        pass  # Port check failed, continue anyway
    
    # Check if database is available first
    if not check_database_available():
        return
    
    init_db()
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("QUICK TEST: Fetching 5 real papers from PubMed")
        logger.info("=" * 60)
        
        # Fetch 5 real papers
        cutoff = datetime.now() - timedelta(days=30)
        papers = pubmed.fetch_recent(cutoff, max_results=5)
        
        if not papers:
            logger.error("No papers fetched! Check PubMed configuration.")
            return
        
        logger.info(f"Fetched {len(papers)} real papers from PubMed")
        
        parser = ProblemParser()
        extractor = CapabilityExtractor()
        
        problems_added = 0
        capabilities_added = 0
        
        for i, paper in enumerate(papers, 1):
            try:
                logger.info(f"\nProcessing paper {i}/{len(papers)}: {paper['title'][:60]}...")
                logger.info(f"  PMID: {paper['id']}")
                logger.info(f"  URL: https://pubmed.ncbi.nlm.nih.gov/{paper['id']}")
                
                # Check if already exists
                existing = db.query(Problem).filter(
                    Problem.source == "pubmed",
                    Problem.source_id == paper['id']
                ).first()
                
                if existing:
                    logger.info("  [SKIP] Already exists in database")
                    continue
                
                # Parse problem using GPT-4o
                logger.info("  [1/3] Extracting problem using GPT-4o...")
                problem = parser.process(
                    paper.get("text", paper.get("abstract", "")),
                    source="pubmed",
                    source_id=paper['id']
                )
                
                problem.source_url = f"https://pubmed.ncbi.nlm.nih.gov/{paper['id']}"
                if paper.get('doi'):
                    problem.source_url = f"https://doi.org/{paper['doi']}"
                
                # Retry logic for database locks
                max_retries = 5
                retry_delay = 1
                for attempt in range(max_retries):
                    try:
                        db.add(problem)
                        db.flush()
                        problems_added += 1
                        break
                    except OperationalError as e:
                        if "locked" in str(e).lower() and attempt < max_retries - 1:
                            logger.warning(f"  [RETRY {attempt + 1}/{max_retries}] Database locked, waiting {retry_delay}s...")
                            db.rollback()
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            raise
                
                logger.info(f"  [OK] Problem extracted: {problem.title[:60]}...")
                logger.info(f"       Category: {problem.category.value}")
                
                # Extract capabilities using GPT-4o
                logger.info("  [2/3] Extracting capabilities using GPT-4o...")
                capabilities = extractor.process(
                    problem.description,
                    problem_id=problem.id
                )
                
                for cap in capabilities:
                    # Check if exists
                    existing_cap = db.query(Capability).filter(
                        Capability.name == cap.name,
                        Capability.type == cap.type
                    ).first()
                    
                    if existing_cap:
                        cap = existing_cap
                    else:
                        # Retry logic for database locks
                        max_retries = 5
                        retry_delay = 1
                        for attempt in range(max_retries):
                            try:
                                db.add(cap)
                                db.flush()
                                capabilities_added += 1
                                break
                            except OperationalError as e:
                                if "locked" in str(e).lower() and attempt < max_retries - 1:
                                    logger.warning(f"  [RETRY {attempt + 1}/{max_retries}] Database locked, waiting {retry_delay}s...")
                                    db.rollback()
                                    time.sleep(retry_delay)
                                    retry_delay *= 2
                                else:
                                    raise
                    
                    # Create mapping
                    mapping = ProblemCapabilityMapping(
                        problem_id=problem.id,
                        capability_id=cap.id,
                        confidence_score=0.8
                    )
                    db.add(mapping)
                
                logger.info(f"  [OK] {len(capabilities)} capabilities identified")
                
                # Retry commit for database locks
                max_retries = 5
                retry_delay = 1
                for attempt in range(max_retries):
                    try:
                        db.commit()
                        break
                    except OperationalError as e:
                        if "locked" in str(e).lower() and attempt < max_retries - 1:
                            logger.warning(f"  [RETRY {attempt + 1}/{max_retries}] Database locked on commit, waiting {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            db.rollback()
                            raise
                
            except Exception as e:
                logger.error(f"  [ERROR] Error processing paper: {e}", exc_info=True)
                db.rollback()
                continue
        
        logger.info("\n" + "=" * 60)
        logger.info("RESULTS:")
        logger.info("=" * 60)
        logger.info(f"  Problems added: {problems_added}")
        logger.info(f"  Capabilities added: {capabilities_added}")
        logger.info(f"\n[SUCCESS] Real data from PubMed processed!")
        logger.info("  - Refresh your browser to see the new data")
        logger.info("  - All problems link to real PubMed papers")
        
        # Show final count
        from sqlalchemy import func
        total = db.query(func.count(Problem.id)).scalar()
        pubmed_count = db.query(func.count(Problem.id)).filter(Problem.source == 'pubmed').scalar()
        logger.info(f"\nDatabase now has:")
        logger.info(f"  Total problems: {total}")
        logger.info(f"  From PubMed (REAL): {pubmed_count}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_process_quick()

