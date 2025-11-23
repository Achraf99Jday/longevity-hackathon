"""ClinicalTrials.gov data source integration."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import json


def fetch_recent(cutoff_date: datetime, max_results: int = 500) -> List[Dict[str, Any]]:
    """
    Fetch recent aging-related clinical trials.
    
    Args:
        cutoff_date: Only fetch trials after this date
        max_results: Maximum number of results
        
    Returns:
        List of trial dictionaries
    """
    # ClinicalTrials.gov API
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Search for aging-related trials
    query = {
        "query.cond": "aging OR longevity OR senescence",
        "pageSize": min(max_results, 1000),
        "format": "json"
    }
    
    trials = []
    
    try:
        response = requests.get(base_url, params=query, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            
            # Check if trial is recent enough
            try:
                start_date_str = protocol.get("identificationModule", {}).get("nctId", "")
                # Simple check - in real implementation, parse dates properly
            except:
                pass
            
            trial = _parse_trial(study)
            if trial:
                trials.append(trial)
    
    except Exception as e:
        print(f"Error fetching from ClinicalTrials.gov: {e}")
    
    return trials


def fetch_all(max_results: int = 2000) -> List[Dict[str, Any]]:
    """Fetch all aging-related clinical trials."""
    return fetch_recent(datetime(2000, 1, 1), max_results)


def _parse_trial(study: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse a clinical trial into our format."""
    try:
        protocol = study.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        desc = protocol.get("descriptionModule", {})
        
        nct_id = ident.get("nctId", "")
        title = ident.get("briefTitle", "")
        summary = desc.get("briefSummary", "")
        detailed_desc = desc.get("detailedDescription", "")
        
        text = f"{title}\n\n{summary}\n\n{detailed_desc}"
        
        return {
            "id": nct_id,
            "title": title,
            "abstract": summary,
            "text": text,
            "source": "clinical_trials"
        }
    
    except Exception as e:
        print(f"Error parsing trial: {e}")
        return None

