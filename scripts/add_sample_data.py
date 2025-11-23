"""Add sample data for testing/demo purposes."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.database.session import SessionLocal, init_db
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.models.capability import Capability, CapabilityType
from longevity_map.models.resource import Resource, ResourceType
from longevity_map.models.gap import Gap, GapPriority
from longevity_map.models.mapping import ProblemCapabilityMapping, CapabilityResourceMapping
from longevity_map.agents.problem_parser import ProblemParser
from longevity_map.agents.capability_extractor import CapabilityExtractor
from longevity_map.agents.gap_analyzer import GapAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_sample_data():
    """Add sample problems and data for demonstration."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Problem).count()
        if existing > 0:
            logger.info(f"Database already has {existing} problems. Skipping sample data.")
            return
        
        logger.info("Adding sample data...")
        
        parser = ProblemParser()
        extractor = CapabilityExtractor()
        
        # Try to fetch real data first, fallback to sample if that fails
        logger.info("Attempting to fetch real data from PubMed...")
        try:
            from longevity_map.data_sources import pubmed
            from datetime import datetime, timedelta
            
            # Fetch a few real papers
            real_papers = pubmed.fetch_recent(datetime.now() - timedelta(days=30), max_results=10)
            
            if real_papers and len(real_papers) > 0:
                logger.info(f"Found {len(real_papers)} real papers from PubMed!")
                sample_problems = [
                    {
                        "text": f"{paper['title']}\n\n{paper['abstract']}",
                        "source": "pubmed",
                        "source_id": paper['id'],
                        "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{paper['id']}"
                    }
                    for paper in real_papers[:5]  # Use first 5 real papers
                ]
            else:
                logger.warning("No real papers found, using sample data")
                raise Exception("No real papers")
        except Exception as e:
            logger.warning(f"Could not fetch real data: {e}. Using sample data instead.")
            # Sample problems based on real aging research (these are real research areas)
            sample_problems = [
                {
                    "text": "Understanding the mechanisms of cellular senescence and developing effective senolytic interventions to clear senescent cells and extend healthspan.",
                    "source": "sample",
                    "source_id": "sample_1"
                },
                {
                    "text": "Investigating mitochondrial dysfunction in aging and developing interventions to restore mitochondrial function and reduce oxidative stress.",
                    "source": "sample",
                    "source_id": "sample_2"
                },
                {
                    "text": "Mapping epigenetic alterations during aging and developing epigenetic clocks to predict biological age and intervention efficacy.",
                    "source": "sample",
                    "source_id": "sample_3"
                },
                {
                    "text": "Understanding stem cell exhaustion mechanisms and developing strategies to rejuvenate hematopoietic stem cells in aging.",
                    "source": "sample",
                    "source_id": "sample_4"
                },
                {
                    "text": "Investigating loss of proteostasis in aging and developing interventions to restore protein folding and clearance mechanisms.",
                    "source": "sample",
                    "source_id": "sample_5"
                },
            ]
        
        problems_added = 0
        capabilities_added = 0
        
        for sample in sample_problems:
            # Parse problem
            problem = parser.process(
                sample["text"],
                source=sample["source"],
                source_id=sample["source_id"]
            )
            
            # Add source URL if available
            if "source_url" in sample:
                problem.source_url = sample["source_url"]
            
            # Check if exists
            existing = db.query(Problem).filter(
                Problem.source_id == problem.source_id
            ).first()
            
            if existing:
                continue
            
            db.add(problem)
            db.flush()
            problems_added += 1
            
            # Extract capabilities
            capabilities = extractor.process(problem.description, problem_id=problem.id)
            
            for cap in capabilities:
                # Check if capability exists
                existing_cap = db.query(Capability).filter(
                    Capability.name == cap.name,
                    Capability.type == cap.type
                ).first()
                
                if existing_cap:
                    cap = existing_cap
                else:
                    db.add(cap)
                    db.flush()
                    capabilities_added += 1
                
                # Create mapping
                mapping = ProblemCapabilityMapping(
                    problem_id=problem.id,
                    capability_id=cap.id,
                    confidence_score=0.85,
                    is_required=1
                )
                db.add(mapping)
        
        # Add some sample resources
        sample_resources = [
            {
                "name": "Senescence-Associated Beta-Galactosidase Assay Kit",
                "description": "Commercial kit for detecting senescent cells via SA-β-gal staining",
                "type": ResourceType.HARDWARE,
                "organization": "Sigma-Aldrich",
                "availability": "commercial",
                "url": "https://www.sigmaaldrich.com"
            },
            {
                "name": "Aging Mouse Models Database",
                "description": "Comprehensive database of aging-related mouse models and their characteristics",
                "type": ResourceType.DATABASE,
                "organization": "Jackson Laboratory",
                "availability": "public",
                "url": "https://www.jax.org"
            },
            {
                "name": "Epigenetic Clock Analysis Pipeline",
                "description": "Open-source software for analyzing DNA methylation age",
                "type": ResourceType.SOFTWARE,
                "organization": "Horvath Lab",
                "availability": "public",
                "url": "https://github.com"
            },
        ]
        
        resources_added = 0
        for res_data in sample_resources:
            existing = db.query(Resource).filter(
                Resource.name == res_data["name"]
            ).first()
            
            if existing:
                continue
            
            resource = Resource(**res_data)
            db.add(resource)
            resources_added += 1
        
        db.commit()
        
        logger.info(f"✅ Added {problems_added} problems, {capabilities_added} capabilities, {resources_added} resources")
        
        # Now analyze gaps
        logger.info("Analyzing gaps...")
        gap_analyzer = GapAnalyzer()
        capabilities = db.query(Capability).all()
        
        gaps_created = 0
        for capability in capabilities:
            gap = gap_analyzer.process(capability, db)
            if gap:
                existing = db.query(Gap).filter(
                    Gap.capability_id == capability.id
                ).first()
                
                if not existing:
                    db.add(gap)
                    gaps_created += 1
        
        db.commit()
        logger.info(f"✅ Created {gaps_created} gaps")
        
        logger.info("\n🎉 Sample data added successfully!")
        logger.info("   Refresh your browser to see the data!")
        
    except Exception as e:
        logger.error(f"Error adding sample data: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_data()

