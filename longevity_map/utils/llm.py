"""LLM utilities using OpenAI GPT API."""

from typing import List, Dict, Any, Optional
from openai import OpenAI
import yaml
from pathlib import Path
import json
import logging
import os

logger = logging.getLogger(__name__)


class LLMHelper:
    """Helper class for LLM operations using OpenAI API."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize LLM helper with API key from config."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
            if not config_path.exists():
                config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}
                import logging
                logging.warning(f"No config file found at {config_path}, using defaults")
        except Exception as e:
            import logging
            logging.warning(f"Could not load config from {config_path}: {e}, using defaults")
            config = {}
        
        # Get API key from config or environment variable
        api_key = (
            config.get("api_keys", {}).get("openai", {}).get("api_key", "") or
            os.environ.get("OPENAI_API_KEY", "")
        )
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not found. LLM features will be disabled.")
        
        # Use GPT-4o (latest model) as default
        self.model = config.get("agents", {}).get("problem_parser", {}).get("model", "gpt-4o")
        self.temperature = config.get("agents", {}).get("problem_parser", {}).get("temperature", 0.3)
    
    def extract_problem_info(self, text: str) -> Dict[str, Any]:
        """
        Extract problem information using GPT.
        
        Args:
            text: Problem description or paper abstract
            
        Returns:
            Dict with title, description, category, and capabilities
        """
        if not self.enabled:
            return {}
        
        try:
            prompt = f"""Analyze the following research text about aging/longevity and extract:
1. A clear problem statement (title and description)
2. The primary hallmark of aging it relates to (genomic_instability, telomere_attrition, epigenetic_alterations, loss_of_proteostasis, deregulated_nutrient_sensing, mitochondrial_dysfunction, cellular_senescence, stem_cell_exhaustion, altered_intercellular_communication, or other)
3. Required capabilities/tools/technologies needed to solve this problem

Text: {text[:2000]}

Return JSON format:
{{
    "title": "Problem title",
    "description": "Detailed description",
    "category": "one_of_the_hallmarks",
    "capabilities": [
        {{"name": "capability name", "type": "measurement_tool|model_system|dataset|computational_method|software|hardware|protocol|infrastructure", "description": "what it does"}}
    ]
}}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in aging research and longevity science. Extract structured information from research texts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return {}
    
    def extract_capabilities(self, problem_text: str) -> List[Dict[str, Any]]:
        """
        Extract required capabilities from problem description.
        
        Args:
            problem_text: Problem description
            
        Returns:
            List of capability dicts
        """
        if not self.enabled:
            return []
        
        try:
            prompt = f"""You are an expert in aging research infrastructure. Analyze this research problem and identify ALL specific capabilities (tools, technologies, datasets, methods, equipment) needed to solve it.

Research Problem:
{problem_text[:2000]}

Think carefully about:
- What measurement tools are needed? (e.g., flow cytometry, mass spectrometry, sequencing platforms)
- What model systems? (e.g., mouse models, cell lines, organoids)
- What datasets or databases? (e.g., transcriptomic data, proteomic databases)
- What computational methods or software? (e.g., machine learning models, analysis pipelines)
- What hardware or equipment? (e.g., microscopes, bioreactors, imaging systems)
- What protocols or methods? (e.g., specific experimental protocols, standardized procedures)
- What infrastructure? (e.g., core facilities, specialized labs)

Be SPECIFIC and DETAILED. Identify 3-8 concrete capabilities.

Return JSON format with a "capabilities" array:
{{
    "capabilities": [
        {{
            "name": "Specific capability name (e.g., 'Single-cell RNA sequencing platform')",
            "type": "measurement_tool|model_system|dataset|computational_method|software|hardware|protocol|infrastructure",
            "description": "Detailed description of what it does and why it's needed for this specific problem",
            "estimated_cost_usd": 50000,
            "estimated_time_months": 6
        }}
    ]
}}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in aging research infrastructure, tools, and technologies. You identify specific, concrete capabilities needed to solve research problems. Always return a JSON object with a 'capabilities' array, even if you find just 1 capability."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            capabilities = result.get("capabilities", [])
            
            if not capabilities:
                logger.warning(f"No capabilities extracted from LLM for text: {problem_text[:100]}...")
            else:
                logger.info(f"LLM extracted {len(capabilities)} capabilities")
            
            return capabilities
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in LLM capability extraction: {e}")
            logger.error(f"Response was: {response.choices[0].message.content[:500] if 'response' in locals() else 'No response'}")
            return []
        except Exception as e:
            logger.error(f"Error in LLM capability extraction: {e}", exc_info=True)
            return []
    
    def classify_category(self, text: str) -> str:
        """
        Classify problem into hallmark category.
        
        Args:
            text: Problem description
            
        Returns:
            Category string
        """
        if not self.enabled:
            return "other"
        
        try:
            prompt = f"""Classify this aging research problem into one of these hallmarks:
- genomic_instability
- telomere_attrition
- epigenetic_alterations
- loss_of_proteostasis
- deregulated_nutrient_sensing
- mitochondrial_dysfunction
- cellular_senescence
- stem_cell_exhaustion
- altered_intercellular_communication
- other

Text: {text[:1000]}

Return only the category name."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in aging research. Classify problems by hallmarks of aging."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().lower()
        
        except Exception as e:
            logger.error(f"Error in LLM classification: {e}")
            return "other"
    
    def find_resource_matches(self, capability_description: str, existing_resources: List[str]) -> List[Dict[str, Any]]:
        """
        Find which existing resources match a capability.
        
        Args:
            capability_description: Description of needed capability
            existing_resources: List of resource descriptions
            
        Returns:
            List of matches with scores
        """
        if not self.enabled or not existing_resources:
            return []
        
        try:
            resources_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(existing_resources[:20])])
            
            prompt = f"""Which of these existing resources could fill this capability need?

Needed: {capability_description}

Available resources:
{resources_text}

Return JSON array with matches (0-1 score):
[
    {{"resource_index": 1, "match_score": 0.9, "reason": "why it matches"}}
]"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You match research capabilities to existing resources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("matches", [])
        
        except Exception as e:
            logger.error(f"Error in LLM resource matching: {e}")
            return []

