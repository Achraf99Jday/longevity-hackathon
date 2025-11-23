"""PubMed/PMC data source integration."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from Bio import Entrez
import yaml
from pathlib import Path
import time


def _load_config() -> Dict[str, Any]:
    """Load configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    if not config_path.exists():
        config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def _setup_entrez():
    """Setup Entrez with API credentials."""
    config = _load_config()
    api_config = config.get("api_keys", {}).get("pubmed", {})
    
    email = api_config.get("email", "")
    api_key = api_config.get("api_key", "")
    
    if email:
        Entrez.email = email
    if api_key:
        Entrez.api_key = api_key


def fetch_recent(cutoff_date: datetime, max_results: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetch recent aging-related papers from PubMed.
    
    Args:
        cutoff_date: Only fetch papers after this date
        max_results: Maximum number of results to fetch
        
    Returns:
        List of paper dictionaries
    """
    _setup_entrez()
    
    # Search query for aging-related papers
    query = (
        "(aging OR ageing OR longevity OR senescence OR gerontology) "
        "AND (research OR study OR intervention OR mechanism)"
    )
    
    # Date filter
    date_str = cutoff_date.strftime("%Y/%m/%d")
    query += f" AND {date_str}[PDAT] : {datetime.now().strftime('%Y/%m/%d')}[PDAT]"
    
    papers = []
    
    try:
        # Search
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="pub_date"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        pmids = search_results["IdList"]
        
        if not pmids:
            return papers
        
        # Fetch details in batches
        batch_size = 100
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=",".join(batch),
                retmode="xml"
            )
            articles = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            # Parse articles
            for article in articles["PubmedArticle"]:
                paper = _parse_article(article)
                if paper:
                    papers.append(paper)
            
            # Rate limiting
            time.sleep(0.34)  # Max 3 requests per second
    
    except Exception as e:
        print(f"Error fetching from PubMed: {e}")
    
    return papers


def fetch_all(max_results: int = 10000) -> List[Dict[str, Any]]:
    """Fetch all aging-related papers (no date filter)."""
    _setup_entrez()
    
    query = (
        "(aging OR ageing OR longevity OR senescence OR gerontology) "
        "AND (research OR study OR intervention OR mechanism)"
    )
    
    papers = []
    
    try:
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="pub_date"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        pmids = search_results["IdList"]
        
        # Fetch in batches
        batch_size = 100
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=",".join(batch),
                retmode="xml"
            )
            articles = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            for article in articles["PubmedArticle"]:
                paper = _parse_article(article)
                if paper:
                    papers.append(paper)
            
            time.sleep(0.34)
    
    except Exception as e:
        print(f"Error fetching from PubMed: {e}")
    
    return papers


def _parse_article(article: Any) -> Optional[Dict[str, Any]]:
    """Parse a PubMed article into our format."""
    try:
        medline = article["MedlineCitation"]
        pmid = str(medline["PMID"])
        
        # Get title
        article_data = medline.get("Article", {})
        title = ""
        if "ArticleTitle" in article_data:
            title = str(article_data["ArticleTitle"])
        
        # Get abstract
        abstract = ""
        if "Abstract" in article_data and "AbstractText" in article_data["Abstract"]:
            abstract_texts = article_data["Abstract"]["AbstractText"]
            if isinstance(abstract_texts, list):
                abstract = " ".join(str(t) for t in abstract_texts)
            else:
                abstract = str(abstract_texts)
        
        # Get publication date
        pub_date = None
        if "ArticleDate" in article_data:
            date = article_data["ArticleDate"]
            try:
                year = int(date.get("Year", 2000))
                month = int(date.get("Month", 1))
                day = int(date.get("Day", 1))
                pub_date = datetime(year, month, day)
            except:
                pass
        
        # Get DOI
        doi = ""
        if "ELocationID" in article_data:
            for eloc in article_data["ELocationID"]:
                if eloc.attributes.get("EIdType") == "doi":
                    doi = str(eloc)
        
        return {
            "id": pmid,
            "title": title,
            "abstract": abstract,
            "text": f"{title}\n\n{abstract}",
            "doi": doi,
            "publication_date": pub_date,
            "source": "pubmed"
        }
    
    except Exception as e:
        print(f"Error parsing article: {e}")
        return None

