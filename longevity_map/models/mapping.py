"""Mapping models connecting problems, capabilities, and resources."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from longevity_map.database.base import Base


class ProblemCapabilityMapping(Base):
    """Maps problems to required capabilities."""
    
    __tablename__ = "problem_capability_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id"), nullable=False, index=True)
    confidence_score = Column(Float, default=0.5)  # 0-1 scale, extraction confidence
    is_required = Column(Integer, default=1)  # 1 = required, 0 = optional
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    problem = relationship("Problem", back_populates="capability_mappings")
    capability = relationship("Capability", back_populates="problem_mappings")
    
    __table_args__ = (
        UniqueConstraint('problem_id', 'capability_id', name='uq_problem_capability'),
    )
    
    def __repr__(self):
        return f"<ProblemCapabilityMapping(problem_id={self.problem_id}, capability_id={self.capability_id})>"


class CapabilityResourceMapping(Base):
    """Maps capabilities to existing resources that could fill them."""
    
    __tablename__ = "capability_resource_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False, index=True)
    match_score = Column(Float, default=0.5)  # 0-1 scale, how well resource matches capability
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    capability = relationship("Capability", back_populates="resource_mappings")
    resource = relationship("Resource", back_populates="capability_mappings")
    
    __table_args__ = (
        UniqueConstraint('capability_id', 'resource_id', name='uq_capability_resource'),
    )
    
    def __repr__(self):
        return f"<CapabilityResourceMapping(capability_id={self.capability_id}, resource_id={self.resource_id})>"

