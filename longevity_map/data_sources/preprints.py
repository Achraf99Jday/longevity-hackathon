"""Preprint data source integration (bioRxiv, medRxiv)."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import json


def fetch_recent(cutoff_date: datetime, max_results: int = 500) -> List[Dict[str, Any]]:
    """
    Fetch recent aging-related preprints from bioRxiv/medRxiv.
    
    Args:
        cutoff_date: Only fetch preprints after this date
        max_results: Maximum number of results
        
    Returns:
        List of preprint dictionaries
    """
    preprints = []
    
    # bioRxiv/medRxiv API
    servers = ["biorxiv", "medrxiv"]
    
    for server in servers:
        try:
            base_url = f"https://api.biorxiv.org/details/{server}"
            
            # Convert date to format needed by API
            date_str = cutoff_date.strftime("%Y-%m-%d")
            
            query = {
                "query": "aging OR longevity OR senescence",
                "start": 0,
                "num": min(max_results, 100)
            }
            
            response = requests.get(base_url, params=query, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for paper in data.get("collection", []):
                preprint = _parse_preprint(paper, server)
                if preprint:
                    preprints.append(preprint)
        
        except Exception as e:
            print(f"Error fetching from {server}: {e}")
    
    return preprints


def fetch_all(max_results: int = 1000) -> List[Dict[str, Any]]:
    """Fetch all aging-related preprints."""
    return fetch_recent(datetime(2020, 1, 1), max_results)


def _parse_preprint(paper: Dict[str, Any], server: str) -> Optional[Dict[str, Any]]:
    """Parse a preprint into our format."""
    try:
        doi = paper.get("doi", "")
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        
        text = f"{title}\n\n{abstract}"
        
        return {
            "id": doi,
            "title": title,
            "abstract": abstract,
            "text": text,
            "doi": doi,
            "source": f"preprint_{server}"
        }
    
    except Exception as e:
        print(f"Error parsing preprint: {e}")
        return None

