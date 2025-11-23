"""Capability Extractor agent that identifies required tools, technologies, and methods."""

from typing import List, Dict, Any, Optional
from longevity_map.models.capability import Capability, CapabilityType
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.utils.llm import LLMHelper
import re


class CapabilityExtractor(BaseAgent):
    """Extracts required capabilities from problem descriptions."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.llm = LLMHelper(config_path)
        # Patterns for different capability types
        self.capability_patterns = {
            CapabilityType.MEASUREMENT_TOOL: [
                r"measure(?:ment|ing|s)?\s+(?:of|for|tool|method|technique)",
                r"assay", r"detection", r"quantification", r"imaging",
                r"microscopy", r"flow cytometry", r"sequencing"
            ],
            CapabilityType.MODEL_SYSTEM: [
                r"mouse model", r"animal model", r"cell line", r"organoid",
                r"in vitro", r"in vivo", r"model system"
            ],
            CapabilityType.DATASET: [
                r"dataset", r"data", r"database", r"repository",
                r"omics data", r"transcriptomic", r"proteomic"
            ],
            CapabilityType.COMPUTATIONAL_METHOD: [
                r"algorithm", r"computational", r"machine learning",
                r"modeling", r"simulation", r"prediction"
            ],
            CapabilityType.SOFTWARE: [
                r"software", r"tool", r"platform", r"pipeline"
            ],
            CapabilityType.HARDWARE: [
                r"equipment", r"instrument", r"device", r"machine"
            ],
            CapabilityType.PROTOCOL: [
                r"protocol", r"method", r"procedure", r"standard"
            ],
        }
    
    def process(self, problem_text: str, problem_id: Optional[int] = None) -> List[Capability]:
        """
        Extract required capabilities from a problem description.
        
        Args:
            problem_text: Problem description
            problem_id: Optional problem ID for tracking
            
        Returns:
            List of Capability objects
        """
        capabilities = []
        
        # Try LLM extraction first if enabled
        if self.llm.enabled:
            llm_caps = self.llm.extract_capabilities(problem_text)
            for cap_data in llm_caps:
                try:
                    cap_type = CapabilityType(cap_data.get("type", "other"))
                except ValueError:
                    cap_type = CapabilityType.OTHER
                
                cap = Capability(
                    name=cap_data.get("name", "Unknown"),
                    description=cap_data.get("description", ""),
                    type=cap_type,
                    estimated_cost=cap_data.get("estimated_cost_usd"),
                    estimated_time=cap_data.get("estimated_time_months"),
                    complexity_score=self._estimate_complexity_from_data(cap_data)
                )
                capabilities.append(cap)
        
        # Fallback to pattern-based extraction if LLM didn't find anything
        if not capabilities:
            text_lower = problem_text.lower()
            for cap_type, patterns in self.capability_patterns.items():
                matches = self._find_capabilities(text_lower, patterns, cap_type)
                capabilities.extend(matches)
            
            # Remove duplicates
            capabilities = self._deduplicate_capabilities(capabilities)
            
            # Estimate cost and time
            for cap in capabilities:
                if not cap.estimated_cost:
                    cap.estimated_cost, cap.estimated_time = self._estimate_requirements(cap)
                if not cap.complexity_score:
                    cap.complexity_score = self._estimate_complexity(cap)
        
        return capabilities
    
    def _estimate_complexity_from_data(self, cap_data: Dict[str, Any]) -> float:
        """Estimate complexity from LLM-extracted data."""
        # Use cost and time as proxies for complexity
        cost = cap_data.get("estimated_cost_usd", 50000)
        time = cap_data.get("estimated_time_months", 6)
        
        # Normalize to 0-1 scale
        cost_score = min(1.0, cost / 1_000_000)
        time_score = min(1.0, time / 60)
        
        return (cost_score + time_score) / 2
    
    def _find_capabilities(self, text: str, patterns: List[str], cap_type: CapabilityType) -> List[Capability]:
        """Find capabilities matching patterns."""
        capabilities = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract surrounding context as capability name
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Try to extract a meaningful name
                name = self._extract_capability_name(context, match.group())
                description = context.strip()
                
                if name and len(name) > 3:  # Filter out very short names
                    cap = Capability(
                        name=name,
                        description=description,
                        type=cap_type
                    )
                    capabilities.append(cap)
        
        return capabilities
    
    def _extract_capability_name(self, context: str, matched_text: str) -> str:
        """Extract a meaningful capability name from context."""
        # Simple heuristic: look for noun phrases around the match
        words = context.split()
        match_idx = context.lower().find(matched_text.lower())
        if match_idx == -1:
            return matched_text
        
        # Get words around the match
        char_pos = 0
        word_idx = 0
        for i, word in enumerate(words):
            if char_pos >= match_idx:
                word_idx = i
                break
            char_pos += len(word) + 1
        
        # Extract 2-4 words around the match
        start = max(0, word_idx - 1)
        end = min(len(words), word_idx + 3)
        name = ' '.join(words[start:end])
        
        return name.strip()
    
    def _deduplicate_capabilities(self, capabilities: List[Capability]) -> List[Capability]:
        """Remove duplicate capabilities based on name similarity."""
        if not capabilities:
            return []
        
        unique = []
        seen_names = set()
        
        for cap in capabilities:
            # Simple deduplication: check if name is very similar
            name_lower = cap.name.lower()
            is_duplicate = False
            
            for seen_name in seen_names:
                # Check if names are very similar (simple heuristic)
                if name_lower in seen_name or seen_name in name_lower:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(cap)
                seen_names.add(name_lower)
        
        return unique
    
    def _estimate_requirements(self, capability: Capability) -> tuple[float, int]:
        """Estimate cost (USD) and time (months) for a capability."""
        # Simple heuristics based on type
        base_costs = {
            CapabilityType.MEASUREMENT_TOOL: (50000, 6),
            CapabilityType.MODEL_SYSTEM: (100000, 12),
            CapabilityType.DATASET: (20000, 3),
            CapabilityType.COMPUTATIONAL_METHOD: (50000, 6),
            CapabilityType.SOFTWARE: (100000, 12),
            CapabilityType.HARDWARE: (200000, 18),
            CapabilityType.PROTOCOL: (10000, 2),
            CapabilityType.INFRASTRUCTURE: (500000, 24),
        }
        
        cost, time = base_costs.get(capability.type, (50000, 6))
        
        # Adjust based on complexity keywords
        desc_lower = capability.description.lower()
        if any(word in desc_lower for word in ["complex", "advanced", "novel", "cutting-edge"]):
            cost *= 1.5
            time *= 1.3
        
        return cost, time
    
    def _estimate_complexity(self, capability: Capability) -> float:
        """Estimate complexity score (0-1)."""
        # Simple heuristic based on type and description length
        base_complexity = {
            CapabilityType.MEASUREMENT_TOOL: 0.5,
            CapabilityType.MODEL_SYSTEM: 0.7,
            CapabilityType.DATASET: 0.3,
            CapabilityType.COMPUTATIONAL_METHOD: 0.6,
            CapabilityType.SOFTWARE: 0.6,
            CapabilityType.HARDWARE: 0.8,
            CapabilityType.PROTOCOL: 0.4,
            CapabilityType.INFRASTRUCTURE: 0.9,
        }
        
        complexity = base_complexity.get(capability.type, 0.5)
        
        # Adjust based on description
        if len(capability.description) > 500:
            complexity = min(1.0, complexity + 0.1)
        
        return complexity

