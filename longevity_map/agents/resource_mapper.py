"""Resource Mapper agent that finds existing tools and resources."""

from typing import List, Dict, Any, Optional, Tuple
from longevity_map.models.resource import Resource, ResourceType
from longevity_map.models.capability import Capability
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.database.session import SessionLocal
from sqlalchemy.orm import Session
# Lazy import to avoid loading heavy model in serverless
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
# numpy is optional - only needed if sentence-transformers is available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class ResourceMapper(BaseAgent):
    """Maps capabilities to existing resources using semantic similarity."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.similarity_threshold = self.agent_config.get("similarity_threshold", 0.7)
        # Initialize sentence transformer for semantic similarity (lazy load)
        self.model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                self.log(f"Could not load sentence transformer: {e}. Using simple matching.", "WARNING")
                self.model = None
        else:
            self.log("Sentence transformers not available. Using simple matching.", "INFO")
    
    def process(self, capability: Capability, db: Session) -> List[Tuple[Resource, float]]:
        """
        Find existing resources that could fill a capability gap.
        
        Args:
            capability: Capability to find resources for
            db: Database session
            
        Returns:
            List of (Resource, match_score) tuples
        """
        # Get all active resources of compatible types
        compatible_types = self._get_compatible_resource_types(capability.type)
        resources = db.query(Resource).filter(
            Resource.type.in_(compatible_types),
            Resource.is_active == True
        ).all()
        
        if not resources:
            return []
        
        # Calculate similarity scores
        matches = []
        capability_text = f"{capability.name} {capability.description}"
        
        for resource in resources:
            score = self._calculate_similarity(capability_text, resource)
            if score >= self.similarity_threshold:
                matches.append((resource, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _get_compatible_resource_types(self, capability_type) -> List[ResourceType]:
        """Get compatible resource types for a capability type."""
        mapping = {
            "measurement_tool": [ResourceType.CORE_FACILITY, ResourceType.HARDWARE, ResourceType.SOFTWARE],
            "model_system": [ResourceType.MOUSE_MODEL, ResourceType.CELL_LINE],
            "dataset": [ResourceType.DATASET, ResourceType.DATABASE],
            "computational_method": [ResourceType.SOFTWARE],
            "software": [ResourceType.SOFTWARE],
            "hardware": [ResourceType.HARDWARE, ResourceType.CORE_FACILITY],
            "protocol": [ResourceType.PROTOCOL],
            "infrastructure": [ResourceType.CORE_FACILITY, ResourceType.INFRASTRUCTURE, ResourceType.HARDWARE],
        }
        
        return mapping.get(capability_type.value, list(ResourceType))
    
    def _calculate_similarity(self, capability_text: str, resource: Resource) -> float:
        """Calculate similarity score between capability and resource."""
        if self.model is None:
            # Fallback to simple keyword matching
            return self._simple_similarity(capability_text, resource)
        
        try:
            resource_text = f"{resource.name} {resource.description}"
            embeddings = self.model.encode([capability_text, resource_text])
            # Use numpy if available, otherwise calculate manually
            if NUMPY_AVAILABLE and np is not None:
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
            else:
                # Manual cosine similarity calculation without numpy
                dot_product = sum(a * b for a, b in zip(embeddings[0], embeddings[1]))
                norm_a = sum(a * a for a in embeddings[0]) ** 0.5
                norm_b = sum(b * b for b in embeddings[1]) ** 0.5
                similarity = dot_product / (norm_a * norm_b) if (norm_a * norm_b) > 0 else 0.0
            return float(similarity)
        except Exception as e:
            self.log(f"Error calculating similarity: {e}", "WARNING")
            return self._simple_similarity(capability_text, resource)
    
    def _simple_similarity(self, capability_text: str, resource: Resource) -> float:
        """Simple keyword-based similarity as fallback."""
        capability_words = set(capability_text.lower().split())
        resource_words = set(f"{resource.name} {resource.description}".lower().split())
        
        if not capability_words or not resource_words:
            return 0.0
        
        intersection = capability_words & resource_words
        union = capability_words | resource_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_duplicates(self, db: Session, threshold: float = 0.9) -> List[List[Resource]]:
        """
        Find duplicate resources (multiple groups building the same thing).
        
        Args:
            db: Database session
            threshold: Similarity threshold for considering resources duplicates
            
        Returns:
            List of lists of duplicate resources
        """
        resources = db.query(Resource).filter(Resource.is_active == True).all()
        
        if not resources or self.model is None:
            return []
        
        duplicates = []
        processed = set()
        
        for i, resource1 in enumerate(resources):
            if resource1.id in processed:
                continue
            
            duplicate_group = [resource1]
            
            for resource2 in resources[i+1:]:
                if resource2.id in processed:
                    continue
                
                similarity = self._calculate_similarity(
                    f"{resource1.name} {resource1.description}",
                    resource2
                )
                
                if similarity >= threshold:
                    duplicate_group.append(resource2)
                    processed.add(resource2.id)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
                processed.add(resource1.id)
        
        return duplicates

