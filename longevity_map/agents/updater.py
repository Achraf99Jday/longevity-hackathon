"""Updater agent that continuously ingests new papers, grants, and announcements."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from longevity_map.agents.base_agent import BaseAgent
from longevity_map.agents.problem_parser import ProblemParser
from longevity_map.agents.capability_extractor import CapabilityExtractor
from longevity_map.agents.resource_mapper import ResourceMapper
from longevity_map.database.session import SessionLocal, init_db
from longevity_map.models.problem import Problem
from longevity_map.models.capability import Capability
from longevity_map.models.mapping import ProblemCapabilityMapping, CapabilityResourceMapping
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class Updater(BaseAgent):
    """Continuously updates the database with new information."""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.problem_parser = ProblemParser(config_path)
        self.capability_extractor = CapabilityExtractor(config_path)
        self.resource_mapper = ResourceMapper(config_path)
        
        # Initialize data source modules
        try:
            from longevity_map.data_sources import pubmed, clinical_trials, grants, preprints
            self.data_sources = {
                "pubmed": pubmed if self.config.get("data_sources", {}).get("pubmed", {}).get("enabled") else None,
                "clinical_trials": clinical_trials if self.config.get("data_sources", {}).get("clinical_trials", {}).get("enabled") else None,
                "grants": grants if self.config.get("data_sources", {}).get("grants", {}).get("enabled") else None,
                "preprints": preprints if self.config.get("data_sources", {}).get("preprints", {}).get("enabled") else None,
            }
        except ImportError:
            self.data_sources = {}
    
    def process(self, days_back: int = 30) -> Dict[str, int]:
        """
        Process and update all data sources (required by BaseAgent).
        
        Args:
            days_back: Number of days to look back for updates
            
        Returns:
            Dict with counts of items added from each source
        """
        db = SessionLocal()
        try:
            return self.update_all(db, days_back)
        finally:
            db.close()
    
    def update_all(self, db: Session, days_back: int = 30) -> Dict[str, int]:
        """
        Update all data sources.
        
        Args:
            db: Database session
            days_back: Number of days to look back for updates
            
        Returns:
            Dict with counts of items added from each source
        """
        results = {}
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Update from each enabled source
        for source_name, source_module in self.data_sources.items():
            if source_module is None:
                continue
            
            try:
                count = self._update_source(db, source_name, source_module, cutoff_date)
                results[source_name] = count
                self.log(f"Updated {count} items from {source_name}", "INFO")
            except Exception as e:
                self.log(f"Error updating {source_name}: {e}", "ERROR")
                results[source_name] = 0
        
        return results
    
    def _update_source(self, db: Session, source_name: str, source_module: Any, 
                      cutoff_date: datetime) -> int:
        """Update from a specific data source."""
        count = 0
        
        # Fetch new items
        try:
            # Try fetch_recent first, with max_results limit
            max_results = self.config.get("data_sources", {}).get(source_name, {}).get("max_results", 100)
            if hasattr(source_module, 'fetch_recent'):
                items = source_module.fetch_recent(cutoff_date, max_results=max_results)
            else:
                items = source_module.fetch_all(max_results=max_results)
            
            logger.info(f"Fetched {len(items)} items from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            return 0
        
        if not items:
            logger.warning(f"No items fetched from {source_name}")
            return 0
        
        # Process each item
        for item in items:
            try:
                # Parse problem
                problem = self.problem_parser.process(
                    item.get("text", item.get("abstract", "")),
                    source=source_name,
                    source_id=item.get("id")
                )
                
                # Add source URL if available
                if "doi" in item and item["doi"]:
                    problem.source_url = f"https://doi.org/{item['doi']}"
                elif source_name == "pubmed" and item.get("id"):
                    problem.source_url = f"https://pubmed.ncbi.nlm.nih.gov/{item['id']}"
                
                # Check if problem already exists
                existing = db.query(Problem).filter(
                    Problem.source == source_name,
                    Problem.source_id == problem.source_id
                ).first()
                
                if existing:
                    continue  # Skip duplicates
                
                # Extract capabilities
                capabilities = self.capability_extractor.process(
                    problem.description,
                    problem_id=problem.id
                )
                
                # Save problem
                db.add(problem)
                db.flush()  # Get problem.id
                
                # Save capabilities and mappings
                for cap in capabilities:
                    # Check if capability exists
                    existing_cap = db.query(Capability).filter(
                        Capability.name == cap.name,
                        Capability.type == cap.type
                    ).first()
                    
                    if existing_cap:
                        cap = existing_cap
                    else:
                        db.add(cap)
                        db.flush()
                    
                    # Create mapping
                    from longevity_map.models.mapping import ProblemCapabilityMapping
                    mapping = ProblemCapabilityMapping(
                        problem_id=problem.id,
                        capability_id=cap.id,
                        confidence_score=0.8  # Default confidence
                    )
                    db.add(mapping)
                    
                    # Try to find matching resources
                    resource_matches = self.resource_mapper.process(cap, db)
                    for resource, score in resource_matches:
                        from longevity_map.models.mapping import CapabilityResourceMapping
                        resource_mapping = CapabilityResourceMapping(
                            capability_id=cap.id,
                            resource_id=resource.id,
                            match_score=score
                        )
                        db.add(resource_mapping)
                
                count += 1
                
            except Exception as e:
                self.log(f"Error processing item from {source_name}: {e}", "ERROR")
                continue
        
        db.commit()
        return count
    
    def run_scheduled_update(self):
        """Run scheduled update (called by scheduler)."""
        db = next(SessionLocal())
        try:
            results = self.update_all(db)
            self.log(f"Scheduled update completed: {results}", "INFO")
        finally:
            db.close()

