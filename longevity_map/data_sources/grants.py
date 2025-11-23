"""Grants data source integration (NIH RePORTER, etc.)."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import json


def fetch_recent(cutoff_date: datetime, max_results: int = 500) -> List[Dict[str, Any]]:
    """
    Fetch recent aging-related grants from NIH RePORTER.
    
    Args:
        cutoff_date: Only fetch grants after this date
        max_results: Maximum number of results
        
    Returns:
        List of grant dictionaries
    """
    # NIH RePORTER API (simplified - real implementation would use proper API)
    grants = []
    
    # Note: NIH RePORTER API requires proper setup
    # This is a placeholder implementation
    try:
        # Example query structure (would need actual API key and proper endpoint)
        query = {
            "criteria": {
                "project_title": "aging OR longevity OR senescence"
            },
            "offset": 0,
            "limit": max_results
        }
        
        # In real implementation, make API call here
        # For now, return empty list
        pass
    
    except Exception as e:
        print(f"Error fetching grants: {e}")
    
    return grants


def fetch_all(max_results: int = 1000) -> List[Dict[str, Any]]:
    """Fetch all aging-related grants."""
    return fetch_recent(datetime(2000, 1, 1), max_results)


def _parse_grant(grant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse a grant into our format."""
    try:
        title = grant_data.get("project_title", "")
        abstract = grant_data.get("abstract_text", "")
        grant_id = grant_data.get("project_number", "")
        
        text = f"{title}\n\n{abstract}"
        
        return {
            "id": grant_id,
            "title": title,
            "abstract": abstract,
            "text": text,
            "source": "grants"
        }
    
    except Exception as e:
        print(f"Error parsing grant: {e}")
        return None

