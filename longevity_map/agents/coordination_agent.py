"""Coordination Agent that detects when multiple groups are building the same thing."""

from typing import List, Dict, Any
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.agents.resource_mapper import ResourceMapper
from longevity_map.database.session import SessionLocal
from sqlalchemy.orm import Session


class CoordinationAgent(BaseAgent):
    """Detects duplication and coordination opportunities."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.resource_mapper = ResourceMapper(config_path)
    
    def process(self, db: Session) -> List[Dict[str, Any]]:
        """
        Process and detect coordination opportunities.
        
        Args:
            db: Database session
            
        Returns:
            List of coordination opportunities
        """
        return self.find_coordination_opportunities(db)
    
    def detect_duplication_clusters(self, db: Session, min_groups: int = 3) -> List[Dict[str, Any]]:
        """
        Detect clusters where multiple groups are building the same thing.
        
        Args:
            db: Database session
            min_groups: Minimum number of groups to consider it a cluster
            
        Returns:
            List of duplication cluster info
        """
        duplicates = self.resource_mapper.find_duplicates(db, threshold=0.85)
        
        clusters = []
        for duplicate_group in duplicates:
            if len(duplicate_group) >= min_groups:
                cluster_info = {
                    "resources": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "organization": r.organization,
                            "type": r.type.value
                        }
                        for r in duplicate_group
                    ],
                    "num_groups": len(duplicate_group),
                    "description": duplicate_group[0].description if duplicate_group else "",
                }
                clusters.append(cluster_info)
        
        return clusters
    
    def find_coordination_opportunities(self, db: Session) -> List[Dict[str, Any]]:
        """
        Find opportunities for coordination between groups.
        
        Returns:
            List of coordination opportunities
        """
        clusters = self.detect_duplication_clusters(db, min_groups=2)
        
        opportunities = []
        for cluster in clusters:
            if cluster["num_groups"] >= 2:
                opportunities.append({
                    "type": "duplication",
                    "severity": "high" if cluster["num_groups"] >= 3 else "medium",
                    "description": f"{cluster['num_groups']} groups building similar resources",
                    "resources": cluster["resources"],
                    "recommendation": "Consider coordination or resource sharing"
                })
        
        return opportunities

