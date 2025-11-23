"""Problem model representing open problems in aging research."""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from longevity_map.database.base import Base


class ProblemCategory(str, Enum):
    """Categories based on hallmarks of aging."""
    GENOMIC_INSTABILITY = "genomic_instability"
    TELOMERE_ATTENTION = "telomere_attrition"
    EPIGENETIC_ALTERATIONS = "epigenetic_alterations"
    LOSS_OF_PROTEOSTASIS = "loss_of_proteostasis"
    DEREGULATED_NUTRIENT_SENSING = "deregulated_nutrient_sensing"
    MITOCHONDRIAL_DYSFUNCTION = "mitochondrial_dysfunction"
    CELLULAR_SENESCENCE = "cellular_senescence"
    STEM_CELL_EXHAUSTION = "stem_cell_exhaustion"
    ALTERED_INTERCELLULAR_COMMUNICATION = "altered_intercellular_communication"
    OTHER = "other"


class Problem(Base):
    """Represents an open problem in aging research."""
    
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ProblemCategory), nullable=False, index=True)
    source = Column(String(200))  # e.g., "paper_doi", "grant_id", "preprint_id"
    source_id = Column(String(200), index=True)
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capability_mappings = relationship("ProblemCapabilityMapping", back_populates="problem")
    
    def __repr__(self):
        return f"<Problem(id={self.id}, title='{self.title[:50]}...')>"

