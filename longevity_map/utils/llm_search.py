"""LLM-powered conversational search for the platform."""

from typing import List, Dict, Any, Optional
from longevity_map.utils.llm import LLMHelper
from longevity_map.database.session import SessionLocal
from longevity_map.models.problem import Problem
from longevity_map.models.capability import Capability
from longevity_map.models.gap import Gap
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import logging
import json

logger = logging.getLogger(__name__)


class LLMSearch:
    """Conversational search powered by GPT-4o."""
    
    def __init__(self, config_path=None):
        self.llm = LLMHelper(config_path)
    
    def search(self, query: str, db: Session) -> Dict[str, Any]:
        """
        Natural language search across problems, capabilities, and gaps.
        
        Args:
            query: Natural language query (e.g., "What problems need mouse models?")
            db: Database session
            
        Returns:
            Dict with search results and LLM-generated summary
        """
        if not self.llm.enabled:
            return {
                "query": query,
                "results": [],
                "summary": "LLM search is disabled. Please enable OpenAI API key.",
                "suggestions": []
            }
        
        try:
            # First, use LLM to understand the query and generate search terms
            search_terms = self._extract_search_terms(query, db)
            
            # Search problems
            problems = self._search_problems(query, search_terms, db)
            
            # Search capabilities
            capabilities = self._search_capabilities(query, search_terms, db)
            
            # Search gaps
            gaps = self._search_gaps(query, search_terms, db)
            
            # Use LLM to generate a natural language summary
            summary = self._generate_summary(query, problems, capabilities, gaps)
            
            # Generate follow-up suggestions
            suggestions = self._generate_suggestions(query, problems, capabilities, gaps)
            
            return {
                "query": query,
                "results": {
                    "problems": problems[:10],  # Top 10
                    "capabilities": capabilities[:10],
                    "gaps": gaps[:10]
                },
                "summary": summary,
                "suggestions": suggestions,
                "total_problems": len(problems),
                "total_capabilities": len(capabilities),
                "total_gaps": len(gaps)
            }
        
        except Exception as e:
            logger.error(f"Error in LLM search: {e}", exc_info=True)
            return {
                "query": query,
                "results": {},
                "summary": f"Error: {str(e)}",
                "suggestions": []
            }
    
    def _extract_search_terms(self, query: str, db: Session) -> Dict[str, Any]:
        """Use LLM to extract search terms and intent from query."""
        try:
            # Get some context about what's in the database
            num_problems = db.query(func.count(Problem.id)).scalar()
            num_capabilities = db.query(func.count(Capability.id)).scalar()
            
            prompt = f"""Analyze this search query about aging research and extract search intent:

Query: "{query}"

Database context:
- {num_problems} research problems
- {num_capabilities} capabilities

Extract:
1. What is the user looking for? (problems, capabilities, gaps, or all)
2. Key search terms and concepts
3. Any specific filters (hallmark of aging, capability type, etc.)

Return JSON:
{{
    "intent": "find_problems|find_capabilities|find_gaps|general_search",
    "search_terms": ["term1", "term2"],
    "filters": {{
        "category": "hallmark_name_or_null",
        "capability_type": "type_or_null"
    }},
    "question_type": "what|how|why|where|who"
}}"""
            
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {"role": "system", "content": "You are a search assistant for a longevity research platform. Extract search intent from natural language queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Error extracting search terms: {e}")
            return {
                "intent": "general_search",
                "search_terms": query.lower().split(),
                "filters": {},
                "question_type": "what"
            }
    
    def _search_problems(self, query: str, search_terms: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Search problems using LLM-enhanced matching."""
        # Get all problems
        problems = db.query(Problem).limit(100).all()
        
        if not problems:
            return []
        
        # Use LLM to score relevance
        try:
            problems_text = "\n".join([
                f"{i+1}. {p.title}: {p.description[:200]}"
                for i, p in enumerate(problems[:50])  # Limit for LLM
            ])
            
            prompt = f"""Given this search query and list of research problems, rank them by relevance.

Query: "{query}"

Problems:
{problems_text}

Return JSON with relevance scores (0-1):
{{
    "rankings": [
        {{"index": 1, "relevance": 0.9, "reason": "why it's relevant"}},
        {{"index": 2, "relevance": 0.7, "reason": "why it's relevant"}}
    ]
}}"""
            
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {"role": "system", "content": "You rank research problems by relevance to search queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            rankings = json.loads(response.choices[0].message.content).get("rankings", [])
            
            # Sort problems by relevance
            problem_scores = {r["index"] - 1: r["relevance"] for r in rankings}
            problems_with_scores = [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "category": p.category.value,
                    "source_url": p.source_url,
                    "relevance": problem_scores.get(i, 0.0),
                    "reason": next((r["reason"] for r in rankings if r["index"] - 1 == i), "")
                }
                for i, p in enumerate(problems[:50])
            ]
            
            # Sort by relevance
            problems_with_scores.sort(key=lambda x: x["relevance"], reverse=True)
            return problems_with_scores
        
        except Exception as e:
            logger.error(f"Error in LLM problem search: {e}")
            # Fallback to keyword search
            terms = search_terms.get("search_terms", query.lower().split())
            results = []
            for p in problems:
                text = f"{p.title} {p.description}".lower()
                score = sum(1 for term in terms if term in text) / len(terms) if terms else 0
                if score > 0:
                    results.append({
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "category": p.category.value,
                        "source_url": p.source_url,
                        "relevance": score,
                        "reason": "Keyword match"
                    })
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results
    
    def _search_capabilities(self, query: str, search_terms: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Search capabilities using LLM-enhanced matching."""
        capabilities = db.query(Capability).limit(100).all()
        
        if not capabilities:
            return []
        
        # Simple keyword matching for now (can be enhanced with LLM)
        terms = search_terms.get("search_terms", query.lower().split())
        results = []
        for cap in capabilities:
            text = f"{cap.name} {cap.description}".lower()
            score = sum(1 for term in terms if term in text) / len(terms) if terms else 0
            if score > 0:
                results.append({
                    "id": cap.id,
                    "name": cap.name,
                    "description": cap.description,
                    "type": cap.type.value,
                    "relevance": score
                })
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    def _search_gaps(self, query: str, search_terms: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Search gaps using LLM-enhanced matching."""
        gaps = db.query(Gap).limit(50).all()
        
        if not gaps:
            return []
        
        terms = search_terms.get("search_terms", query.lower().split())
        results = []
        for gap in gaps:
            text = f"{gap.description} {gap.capability.name if gap.capability else ''}".lower()
            score = sum(1 for term in terms if term in text) / len(terms) if terms else 0
            if score > 0:
                results.append({
                    "id": gap.id,
                    "capability_name": gap.capability.name if gap.capability else "Unknown",
                    "description": gap.description,
                    "priority": gap.priority.value,
                    "blocked_value": gap.blocked_research_value,
                    "relevance": score
                })
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    def _generate_summary(self, query: str, problems: List[Dict], capabilities: List[Dict], gaps: List[Dict]) -> str:
        """Generate a natural language summary of search results."""
        try:
            prompt = f"""Generate a helpful, conversational summary of search results for this query:

Query: "{query}"

Results:
- {len(problems)} relevant problems found
- {len(capabilities)} relevant capabilities found
- {len(gaps)} relevant gaps found

Top problems: {', '.join([p['title'][:50] for p in problems[:3]])}

Write a 2-3 sentence summary that:
1. Directly answers the user's question
2. Highlights the most relevant findings
3. Is conversational and helpful

Just return the summary text, no JSON."""
            
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant. Write clear, conversational summaries of search results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Found {len(problems)} problems, {len(capabilities)} capabilities, and {len(gaps)} gaps related to your query."
    
    def _generate_suggestions(self, query: str, problems: List[Dict], capabilities: List[Dict], gaps: List[Dict]) -> List[str]:
        """Generate follow-up question suggestions."""
        try:
            prompt = f"""Based on this search query and results, suggest 3-4 helpful follow-up questions:

Query: "{query}"
Results: {len(problems)} problems, {len(capabilities)} capabilities, {len(gaps)} gaps

Return JSON:
{{
    "suggestions": [
        "Follow-up question 1",
        "Follow-up question 2",
        "Follow-up question 3"
    ]
}}"""
            
            response = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {"role": "system", "content": "You suggest helpful follow-up questions for research queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("suggestions", [])
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []

