"""Analysis script for identifying and analyzing gaps."""

from longevity_map.database.session import SessionLocal, init_db
from longevity_map.agents.gap_analyzer import GapAnalyzer
from longevity_map.agents.coordination_agent import CoordinationAgent
from longevity_map.agents.funding_agent import FundingAgent
from longevity_map.models.capability import Capability
from longevity_map.models.gap import Gap
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_all_gaps():
    """Analyze all capabilities and identify gaps."""
    db = next(SessionLocal())
    
    try:
        gap_analyzer = GapAnalyzer()
        
        # Get all capabilities
        capabilities = db.query(Capability).all()
        
        logger.info(f"Analyzing {len(capabilities)} capabilities...")
        
        gaps_created = 0
        for capability in capabilities:
            gap = gap_analyzer.process(capability, db)
            if gap:
                # Check if gap already exists
                existing = db.query(Gap).filter(
                    Gap.capability_id == capability.id
                ).first()
                
                if not existing:
                    db.add(gap)
                    gaps_created += 1
                    logger.info(f"Created gap for capability: {capability.name}")
        
        db.commit()
        logger.info(f"Created {gaps_created} new gaps")
        
        # Find keystone capabilities
        keystones = gap_analyzer.find_keystone_capabilities(db, top_n=10)
        logger.info(f"\nTop 10 Keystone Capabilities:")
        for i, keystone in enumerate(keystones, 1):
            logger.info(f"{i}. {keystone['name']} - Unlocks {keystone['num_problems']} problems")
        
    finally:
        db.close()


def find_duplication_clusters():
    """Find duplication clusters."""
    db = next(SessionLocal())
    
    try:
        coordination_agent = CoordinationAgent()
        clusters = coordination_agent.detect_duplication_clusters(db, min_groups=3)
        
        logger.info(f"\nFound {len(clusters)} duplication clusters:")
        for i, cluster in enumerate(clusters, 1):
            logger.info(f"\nCluster {i}: {cluster['num_groups']} groups")
            for resource in cluster['resources']:
                logger.info(f"  - {resource['name']} ({resource['organization']})")
    
    finally:
        db.close()


def analyze_funding_potential():
    """Analyze funding potential of gaps."""
    db = next(SessionLocal())
    
    try:
        funding_agent = FundingAgent()
        ranked = funding_agent.rank_gaps_by_funding_potential(db, top_n=20)
        
        logger.info(f"\nTop 20 Gaps by Funding Potential:")
        for i, gap_info in enumerate(ranked, 1):
            gap = gap_info['gap']
            logger.info(
                f"{i}. {gap['capability_id']} - "
                f"Score: {gap_info['attractiveness_score']:.2f}, "
                f"Blocked Value: ${gap['blocked_research_value']/1_000_000:.1f}M, "
                f"Problems: {gap['num_blocked_problems']}"
            )
    
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    
    logger.info("Starting gap analysis...")
    analyze_all_gaps()
    
    logger.info("\nFinding duplication clusters...")
    find_duplication_clusters()
    
    logger.info("\nAnalyzing funding potential...")
    analyze_funding_potential()
    
    logger.info("\nAnalysis complete!")

