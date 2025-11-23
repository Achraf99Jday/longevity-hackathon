"""Test PubMed scraper to ensure it fetches real data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.data_sources import pubmed
from datetime import datetime, timedelta

print("Testing PubMed scraper...")
print("=" * 60)

# Test fetching recent papers
cutoff = datetime.now() - timedelta(days=30)
papers = pubmed.fetch_recent(cutoff, max_results=10)

print(f"\n[OK] Fetched {len(papers)} real papers from PubMed")
print("\nSample papers:")
for i, paper in enumerate(papers[:5], 1):
    print(f"\n{i}. Title: {paper['title'][:80]}...")
    print(f"   PMID: {paper['id']}")
    print(f"   URL: https://pubmed.ncbi.nlm.nih.gov/{paper['id']}")
    print(f"   Abstract length: {len(paper.get('abstract', ''))} chars")
    if paper.get('doi'):
        print(f"   DOI: {paper['doi']}")

if len(papers) == 0:
    print("\n[WARNING] No papers fetched! Check:")
    print("   1. Internet connection")
    print("   2. PubMed API configuration in config/config.yaml")
    print("   3. Email set in config (required for PubMed API)")
    print("   Note: PubMed API works without API key, but email is required")

