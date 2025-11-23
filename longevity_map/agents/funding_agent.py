"""Funding/Impact Agent that predicts which gaps matter most and attract capital."""

from typing import List, Dict, Any, Optional
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.models.gap import Gap
from longevity_map.database.session import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import desc


class FundingAgent(BaseAgent):
    """Predicts funding attractiveness and impact of gaps."""
    
    def process(self, gap: Gap, db: Session) -> Dict[str, Any]:
        """
        Process a gap to predict funding attractiveness.
        
        Args:
            gap: Gap to analyze
            db: Database session
            
        Returns:
            Dict with funding predictions
        """
        return self.predict_funding_attractiveness(gap, db)
    
    def predict_funding_attractiveness(self, gap: Gap, db: Session) -> Dict[str, Any]:
        """
        Predict how attractive a gap is for funding.
        
        Args:
            gap: Gap to analyze
            db: Database session
            
        Returns:
            Dict with funding predictions
        """
        # Factors that make gaps attractive for funding:
        # 1. High impact (many blocked problems)
        # 2. Reasonable cost
        # 3. Clear market need
        # 4. Technical feasibility
        
        attractiveness_score = 0.0
        factors = {}
        
        # Impact factor (0-0.3)
        if gap.num_blocked_problems > 0:
            impact_factor = min(0.3, gap.num_blocked_problems / 20 * 0.3)
            attractiveness_score += impact_factor
            factors["impact"] = impact_factor
        
        # Cost efficiency (0-0.2)
        if gap.estimated_cost and gap.num_blocked_problems > 0:
            cost_per_problem = gap.estimated_cost / gap.num_blocked_problems
            if cost_per_problem < 1_000_000:  # <$1M per problem is good
                cost_factor = 0.2
            elif cost_per_problem < 5_000_000:
                cost_factor = 0.1
            else:
                cost_factor = 0.05
            attractiveness_score += cost_factor
            factors["cost_efficiency"] = cost_factor
        
        # Market size (0-0.3)
        if gap.blocked_research_value:
            if gap.blocked_research_value >= 100_000_000:
                market_factor = 0.3
            elif gap.blocked_research_value >= 10_000_000:
                market_factor = 0.2
            else:
                market_factor = 0.1
            attractiveness_score += market_factor
            factors["market_size"] = market_factor
        
        # Technical feasibility (0-0.2)
        if gap.estimated_time:
            if gap.estimated_time <= 12:  # <= 1 year
                feasibility_factor = 0.2
            elif gap.estimated_time <= 24:
                feasibility_factor = 0.15
            else:
                feasibility_factor = 0.1
            attractiveness_score += feasibility_factor
            factors["feasibility"] = feasibility_factor
        
        return {
            "gap_id": gap.id,
            "attractiveness_score": min(1.0, attractiveness_score),
            "factors": factors,
            "predicted_funding_likelihood": "high" if attractiveness_score >= 0.7 else 
                                           "medium" if attractiveness_score >= 0.4 else "low"
        }
    
    def rank_gaps_by_funding_potential(self, db: Session, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Rank gaps by funding potential.
        
        Args:
            db: Database session
            top_n: Number of top gaps to return
            
        Returns:
            List of gap info with funding predictions
        """
        gaps = db.query(Gap).order_by(desc(Gap.impact_score)).limit(top_n * 2).all()
        
        ranked = []
        for gap in gaps:
            funding_info = self.predict_funding_attractiveness(gap, db)
            ranked.append({
                **funding_info,
                "gap": {
                    "id": gap.id,
                    "capability_id": gap.capability_id,
                    "priority": gap.priority.value,
                    "blocked_research_value": gap.blocked_research_value,
                    "num_blocked_problems": gap.num_blocked_problems,
                }
            })
        
        # Sort by attractiveness score
        ranked.sort(key=lambda x: x["attractiveness_score"], reverse=True)
        
        return ranked[:top_n]

