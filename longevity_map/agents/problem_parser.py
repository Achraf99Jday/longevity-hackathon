"""Problem Parser agent that classifies aging problems into a clean hierarchy."""

from typing import List, Dict, Any, Optional
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.database.session import SessionLocal
from longevity_map.utils.llm import LLMHelper
import re


class ProblemParser(BaseAgent):
    """Classifies aging problems into categories based on hallmarks of aging."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.llm = LLMHelper(config_path)
        # Keywords mapping for each category
        self.category_keywords = {
            ProblemCategory.GENOMIC_INSTABILITY: [
                "genomic instability", "DNA damage", "mutations", "chromosomal aberrations",
                "double-strand breaks", "nucleotide excision repair"
            ],
            ProblemCategory.TELOMERE_ATTENTION: [
                "telomere", "telomerase", "telomere shortening", "telomere attrition"
            ],
            ProblemCategory.EPIGENETIC_ALTERATIONS: [
                "epigenetic", "DNA methylation", "histone modification", "chromatin",
                "epigenome", "epigenetic clock"
            ],
            ProblemCategory.LOSS_OF_PROTEOSTASIS: [
                "proteostasis", "protein folding", "protein aggregation", "autophagy",
                "ubiquitin-proteasome", "chaperone"
            ],
            ProblemCategory.DEREGULATED_NUTRIENT_SENSING: [
                "nutrient sensing", "mTOR", "insulin", "IGF-1", "AMPK", "sirtuin",
                "caloric restriction"
            ],
            ProblemCategory.MITOCHONDRIAL_DYSFUNCTION: [
                "mitochondria", "mitochondrial", "oxidative stress", "ROS", "ATP",
                "mitochondrial DNA", "mitophagy"
            ],
            ProblemCategory.CELLULAR_SENESCENCE: [
                "senescence", "senescent cells", "SASP", "p16", "p21", "senolytics"
            ],
            ProblemCategory.STEM_CELL_EXHAUSTION: [
                "stem cell", "hematopoietic", "regenerative capacity", "tissue repair"
            ],
            ProblemCategory.ALTERED_INTERCELLULAR_COMMUNICATION: [
                "inflammation", "inflammaging", "cytokine", "immune system",
                "cell-cell communication", "signaling"
            ],
        }
    
    def process(self, text: str, source: Optional[str] = None, source_id: Optional[str] = None) -> Problem:
        """
        Parse a problem from text and classify it.
        
        Args:
            text: Problem description or paper abstract
            source: Source identifier (e.g., "pubmed", "preprint")
            source_id: Unique ID from source
            
        Returns:
            Problem object
        """
        # Try LLM extraction first if enabled
        if self.llm.enabled:
            llm_result = self.llm.extract_problem_info(text)
            if llm_result and llm_result.get("title"):
                try:
                    category = ProblemCategory(llm_result.get("category", "other"))
                except ValueError:
                    category = ProblemCategory.OTHER
                
                problem = Problem(
                    title=llm_result.get("title", text[:200]),
                    description=llm_result.get("description", text),
                    category=category,
                    source=source,
                    source_id=source_id
                )
                return problem
        
        # Fallback to rule-based extraction
        title, description = self._extract_title_description(text)
        category = self._classify_category(text)
        
        problem = Problem(
            title=title,
            description=description,
            category=category,
            source=source,
            source_id=source_id
        )
        
        return problem
    
    def _extract_title_description(self, text: str) -> tuple[str, str]:
        """Extract title and description from text."""
        # Simple heuristic: first line or sentence is title
        lines = text.strip().split('\n')
        if len(lines) > 1:
            title = lines[0].strip()
            description = '\n'.join(lines[1:]).strip()
        else:
            # Try to split by sentence
            sentences = re.split(r'[.!?]\s+', text)
            if len(sentences) > 1:
                title = sentences[0]
                description = '. '.join(sentences[1:])
            else:
                title = text[:200] + "..." if len(text) > 200 else text
                description = text
        
        return title, description
    
    def _classify_category(self, text: str) -> ProblemCategory:
        """Classify problem into a category based on keywords or LLM."""
        # Try LLM first
        if self.llm.enabled:
            llm_category = self.llm.classify_category(text)
            try:
                return ProblemCategory(llm_category)
            except ValueError:
                pass
        
        # Fallback to keyword-based classification
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            return max(category_scores, key=category_scores.get)
        else:
            return ProblemCategory.OTHER
    
    def batch_process(self, texts: List[str], sources: Optional[List[str]] = None, 
                     source_ids: Optional[List[str]] = None) -> List[Problem]:
        """Process multiple problems in batch."""
        if sources is None:
            sources = [None] * len(texts)
        if source_ids is None:
            source_ids = [None] * len(texts)
        
        return [self.process(text, source, source_id) 
                for text, source, source_id in zip(texts, sources, source_ids)]

