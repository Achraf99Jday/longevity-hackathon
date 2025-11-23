"""Resource model representing existing R&D resources."""

from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
from longevity_map.database.base import Base


class ResourceType(str, Enum):
    """Types of existing resources."""
    CORE_FACILITY = "core_facility"
    DATASET = "dataset"
    CRO = "cro"  # Contract Research Organization
    SOFTWARE = "software"
    HARDWARE = "hardware"
    MOUSE_MODEL = "mouse_model"
    CELL_LINE = "cell_line"
    PROTOCOL = "protocol"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class Resource(Base):
    """Represents an existing R&D resource."""
    
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(SQLEnum(ResourceType), nullable=False, index=True)
    organization = Column(String(200))
    location = Column(String(200))
    url = Column(String(500))
    cost = Column(Float)  # in USD, if applicable
    availability = Column(String(100))  # e.g., "public", "academic", "commercial"
    is_active = Column(Boolean, default=True, index=True)
    source = Column(String(200))  # e.g., "pubmed", "clinical_trials", "manual"
    source_id = Column(String(200), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capability_mappings = relationship("CapabilityResourceMapping", back_populates="resource")
    
    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', type={self.type})>"

