"""Capability model representing required tools, technologies, and methods."""

from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from longevity_map.database.base import Base


class CapabilityType(str, Enum):
    """Types of capabilities needed for research."""
    MEASUREMENT_TOOL = "measurement_tool"
    MODEL_SYSTEM = "model_system"
    DATASET = "dataset"
    COMPUTATIONAL_METHOD = "computational_method"
    INFRASTRUCTURE = "infrastructure"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    PROTOCOL = "protocol"
    OTHER = "other"


class Capability(Base):
    """Represents a required capability for solving problems."""
    
    __tablename__ = "capabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(SQLEnum(CapabilityType), nullable=False, index=True)
    estimated_cost = Column(Float)  # in USD
    estimated_time = Column(Integer)  # in months
    complexity_score = Column(Float)  # 0-1 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    problem_mappings = relationship("ProblemCapabilityMapping", back_populates="capability")
    resource_mappings = relationship("CapabilityResourceMapping", back_populates="capability")
    
    def __repr__(self):
        return f"<Capability(id={self.id}, name='{self.name}', type={self.type})>"

