"""Gap Analyzer agent that scores missing capabilities."""

from typing import List, Dict, Any, Optional
from longevity_map.models.gap import Gap, GapPriority
from longevity_map.models.capability import Capability
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.database.session import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func


class GapAnalyzer(BaseAgent):
    """Analyzes gaps and scores them by cost, time, and impact."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        gap_config = self.agent_config
        self.cost_weight = gap_config.get("cost_weight", 0.3)
        self.time_weight = gap_config.get("time_weight", 0.3)
        self.impact_weight = gap_config.get("impact_weight", 0.4)
    
    def process(self, capability: Capability, db: Session) -> Optional[Gap]:
        """
        Analyze if a capability represents a gap and create Gap object.
        
        Args:
            capability: Capability to analyze
            db: Database session
            
        Returns:
            Gap object if capability is missing, None otherwise
        """
        # Check if capability has any matching resources
        from longevity_map.models.mapping import CapabilityResourceMapping
        
        has_resources = db.query(CapabilityResourceMapping).filter(
            CapabilityResourceMapping.capability_id == capability.id,
            CapabilityResourceMapping.match_score >= 0.7
        ).first() is not None
        
        if has_resources:
            return None  # Not a gap, resources exist
        
        # Count blocked problems
        from longevity_map.models.mapping import ProblemCapabilityMapping
        
        num_blocked = db.query(ProblemCapabilityMapping).filter(
            ProblemCapabilityMapping.capability_id == capability.id,
            ProblemCapabilityMapping.is_required == 1
        ).count()
        
        # Estimate blocked research value (simple heuristic)
        blocked_value = num_blocked * 2_000_000  # $2M per problem on average
        
        # Determine priority
        priority = self._determine_priority(blocked_value, num_blocked)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(
            capability.estimated_cost or 0,
            capability.estimated_time or 0,
            blocked_value,
            num_blocked
        )
        
        # Create gap
        gap = Gap(
            capability_id=capability.id,
            description=f"Missing capability: {capability.name}",
            estimated_cost=capability.estimated_cost,
            estimated_time=capability.estimated_time,
            blocked_research_value=blocked_value,
            num_blocked_problems=num_blocked,
            priority=priority,
            impact_score=impact_score
        )
        
        return gap
    
    def _determine_priority(self, blocked_value: float, num_blocked: int) -> GapPriority:
        """Determine priority based on blocked value and number of problems."""
        if blocked_value >= 100_000_000 or num_blocked >= 10:
            return GapPriority.CRITICAL
        elif blocked_value >= 10_000_000 or num_blocked >= 5:
            return GapPriority.HIGH
        elif blocked_value >= 1_000_000 or num_blocked >= 2:
            return GapPriority.MEDIUM
        else:
            return GapPriority.LOW
    
    def _calculate_impact_score(self, cost: float, time: int, blocked_value: float, 
                                num_blocked: int) -> float:
        """Calculate overall impact score (0-1)."""
        # Normalize components
        cost_score = min(1.0, 1.0 - (cost / 10_000_000))  # Lower cost = higher score
        time_score = min(1.0, 1.0 - (time / 60))  # Lower time = higher score
        value_score = min(1.0, blocked_value / 100_000_000)  # Higher value = higher score
        problems_score = min(1.0, num_blocked / 20)  # More problems = higher score
        
        # Weighted combination
        impact = (
            self.cost_weight * cost_score +
            self.time_weight * time_score +
            self.impact_weight * (value_score + problems_score) / 2
        )
        
        return min(1.0, max(0.0, impact))
    
    def find_keystone_capabilities(self, db: Session, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Find keystone capabilities that unlock multiple problems.
        
        Args:
            db: Database session
            top_n: Number of top capabilities to return
            
        Returns:
            List of capability info dicts sorted by impact
        """
        from longevity_map.models.mapping import ProblemCapabilityMapping
        
        # Get capabilities with most problems
        results = db.query(
            Capability.id,
            Capability.name,
            Capability.description,
            Capability.type,
            func.count(ProblemCapabilityMapping.problem_id).label('num_problems')
        ).join(
            ProblemCapabilityMapping,
            Capability.id == ProblemCapabilityMapping.capability_id
        ).group_by(
            Capability.id
        ).order_by(
            func.count(ProblemCapabilityMapping.problem_id).desc()
        ).limit(top_n).all()
        
        keystones = []
        for result in results:
            keystones.append({
                "capability_id": result.id,
                "name": result.name,
                "description": result.description,
                "type": result.type.value,
                "num_problems": result.num_problems,
            })
        
        return keystones

