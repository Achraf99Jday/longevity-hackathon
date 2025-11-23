"""Gap model representing missing capabilities."""

from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Float, ForeignKey
from sqlalchemy.orm import relationship
from longevity_map.database.base import Base


class GapPriority(str, Enum):
    """Priority levels for gaps."""
    CRITICAL = "critical"  # Blocks >$100M research
    HIGH = "high"  # Blocks >$10M research
    MEDIUM = "medium"  # Blocks >$1M research
    LOW = "low"  # Blocks <$1M research


class Gap(Base):
    """Represents a missing capability (infrastructure gap)."""
    
    __tablename__ = "gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id"), nullable=False, index=True)
    description = Column(Text)
    estimated_cost = Column(Float)  # in USD
    estimated_time = Column(Integer)  # in months
    blocked_research_value = Column(Float)  # Estimated value of blocked research in USD
    num_blocked_problems = Column(Integer, default=0)
    priority = Column(SQLEnum(GapPriority), nullable=False, index=True)
    impact_score = Column(Float)  # 0-1 scale, calculated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capability = relationship("Capability", backref="gaps")
    
    def __repr__(self):
        return f"<Gap(id={self.id}, capability_id={self.capability_id}, priority={self.priority})>"

