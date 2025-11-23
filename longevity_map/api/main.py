"""FastAPI application for longevity R&D map."""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import yaml
from pathlib import Path
import threading
import logging

from longevity_map.database.session import get_db, init_db
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.models.capability import Capability, CapabilityType
from longevity_map.models.resource import Resource, ResourceType
from longevity_map.models.gap import Gap, GapPriority
from longevity_map.models.mapping import ProblemCapabilityMapping, CapabilityResourceMapping
from longevity_map.agents.gap_analyzer import GapAnalyzer
from longevity_map.agents.coordination_agent import CoordinationAgent
from longevity_map.agents.funding_agent import FundingAgent

# Initialize database (lazy - will be created on first use if needed)
# Don't fail if database can't be initialized at import time
try:
    init_db()
except Exception as e:
    logging.warning(f"Database initialization deferred: {e}")

# Load config - handle missing config.yaml gracefully
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
if not config_path.exists():
    config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
except Exception as e:
    logging.warning(f"Could not load config file: {e}. Using defaults.")
    config = {}

# Create FastAPI app
app = FastAPI(
    title="Longevity R&D Map API",
    description="API for mapping open problems in aging sciences to capabilities, resources, and gaps",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
gap_analyzer = GapAnalyzer()
coordination_agent = CoordinationAgent()
funding_agent = FundingAgent()

# Global state for fetch status
fetch_status = {"running": False, "progress": 0, "total": 0, "message": ""}
fetch_lock = threading.Lock()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Longevity R&D Map API",
        "version": "0.1.0",
        "description": "API for mapping open problems in aging sciences"
    }


@app.get("/problems", response_model=List[dict])
def get_problems(
    category: Optional[ProblemCategory] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get problems, optionally filtered by category."""
    query = db.query(Problem)
    
    if category:
        query = query.filter(Problem.category == category)
    
    problems = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "category": p.category.value,
            "source": p.source,
            "source_id": p.source_id,
            "source_url": p.source_url
        }
        for p in problems
    ]


@app.get("/problems/{problem_id}")
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    """Get a single problem by ID."""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    return {
        "id": problem.id,
        "title": problem.title,
        "description": problem.description,
        "category": problem.category.value,
        "source": problem.source,
        "source_id": problem.source_id,
        "source_url": problem.source_url or (f"https://pubmed.ncbi.nlm.nih.gov/{problem.source_id}" if problem.source == "pubmed" and problem.source_id else None)
    }

@app.get("/problems/{problem_id}/capabilities", response_model=List[dict])
def get_problem_capabilities(problem_id: int, db: Session = Depends(get_db)):
    """Get capabilities required for a problem."""
    mappings = db.query(ProblemCapabilityMapping).filter(
        ProblemCapabilityMapping.problem_id == problem_id
    ).all()
    
    return [
        {
            "capability_id": m.capability_id,
            "capability": {
                "id": m.capability.id,
                "name": m.capability.name,
                "description": m.capability.description,
                "type": m.capability.type.value,
                "estimated_cost": m.capability.estimated_cost,
                "estimated_time": m.capability.estimated_time
            },
            "confidence_score": m.confidence_score,
            "is_required": bool(m.is_required)
        }
        for m in mappings
    ]


@app.get("/capabilities", response_model=List[dict])
def get_capabilities(
    type: Optional[CapabilityType] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get capabilities."""
    query = db.query(Capability)
    
    if type:
        query = query.filter(Capability.type == type)
    
    capabilities = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "type": c.type.value,
            "estimated_cost": c.estimated_cost,
            "estimated_time": c.estimated_time,
            "complexity_score": c.complexity_score
        }
        for c in capabilities
    ]


@app.get("/capabilities/{capability_id}")
def get_capability(capability_id: int, db: Session = Depends(get_db)):
    """Get a single capability by ID."""
    capability = db.query(Capability).filter(Capability.id == capability_id).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")
    
    return {
        "id": capability.id,
        "name": capability.name,
        "description": capability.description,
        "type": capability.type.value,
        "estimated_cost": capability.estimated_cost,
        "estimated_time": capability.estimated_time,
        "complexity_score": capability.complexity_score
    }

@app.get("/capabilities/{capability_id}/resources", response_model=List[dict])
def get_capability_resources(capability_id: int, db: Session = Depends(get_db)):
    """Get resources that could fill a capability."""
    mappings = db.query(CapabilityResourceMapping).filter(
        CapabilityResourceMapping.capability_id == capability_id
    ).order_by(CapabilityResourceMapping.match_score.desc()).all()
    
    return [
        {
            "resource_id": m.resource_id,
            "resource": {
                "id": m.resource.id,
                "name": m.resource.name,
                "description": m.resource.description,
                "type": m.resource.type.value,
                "organization": m.resource.organization,
                "location": m.resource.location,
                "url": m.resource.url,
                "availability": m.resource.availability
            },
            "match_score": m.match_score
        }
        for m in mappings
    ]


@app.get("/gaps", response_model=List[dict])
def get_gaps(
    priority: Optional[GapPriority] = None,
    min_blocked_value: Optional[float] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get infrastructure gaps."""
    query = db.query(Gap)
    
    if priority:
        query = query.filter(Gap.priority == priority)
    
    if min_blocked_value:
        query = query.filter(Gap.blocked_research_value >= min_blocked_value)
    
    gaps = query.order_by(Gap.impact_score.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": g.id,
            "capability_id": g.capability_id,
            "capability": {
                "id": g.capability.id,
                "name": g.capability.name,
                "type": g.capability.type.value
            },
            "description": g.description,
            "estimated_cost": g.estimated_cost,
            "estimated_time": g.estimated_time,
            "blocked_research_value": g.blocked_research_value,
            "num_blocked_problems": g.num_blocked_problems,
            "priority": g.priority.value,
            "impact_score": g.impact_score
        }
        for g in gaps
    ]

@app.get("/gaps/{gap_id}")
def get_gap(gap_id: int, db: Session = Depends(get_db)):
    """Get a single gap by ID."""
    gap = db.query(Gap).filter(Gap.id == gap_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    return {
        "id": gap.id,
        "capability_id": gap.capability_id,
        "capability": {
            "id": gap.capability.id,
            "name": gap.capability.name,
            "description": gap.capability.description,
            "type": gap.capability.type.value
        },
        "description": gap.description,
        "estimated_cost": gap.estimated_cost,
        "estimated_time": gap.estimated_time,
        "blocked_research_value": gap.blocked_research_value,
        "num_blocked_problems": gap.num_blocked_problems,
        "priority": gap.priority.value,
        "impact_score": gap.impact_score
    }


@app.get("/matrix/problem-capability")
def get_problem_capability_matrix(
    category: Optional[ProblemCategory] = None,
    db: Session = Depends(get_db)
):
    """Get problem-capability matrix."""
    query = db.query(Problem)
    if category:
        query = query.filter(Problem.category == category)
    
    problems = query.all()
    
    matrix = []
    for problem in problems:
        mappings = db.query(ProblemCapabilityMapping).filter(
            ProblemCapabilityMapping.problem_id == problem.id
        ).all()
        
        for mapping in mappings:
            matrix.append({
                "problem_id": problem.id,
                "problem_title": problem.title,
                "problem_category": problem.category.value,
                "capability_id": mapping.capability_id,
                "capability_name": mapping.capability.name,
                "capability_type": mapping.capability.type.value,
                "confidence_score": mapping.confidence_score,
                "is_required": bool(mapping.is_required)
            })
    
    return {
        "matrix": matrix,
        "num_problems": len(problems),
        "num_entries": len(matrix)
    }


@app.get("/keystone-capabilities")
def get_keystone_capabilities(
    top_n: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get keystone capabilities that unlock multiple problems."""
    keystones = gap_analyzer.find_keystone_capabilities(db, top_n)
    return {"keystones": keystones}


@app.get("/duplication-clusters")
def get_duplication_clusters(
    min_groups: int = Query(3, ge=2, le=10),
    db: Session = Depends(get_db)
):
    """Get duplication clusters where multiple groups are building the same thing."""
    clusters = coordination_agent.detect_duplication_clusters(db, min_groups)
    return {"clusters": clusters, "num_clusters": len(clusters)}


@app.get("/gaps/funding-potential")
def get_gaps_by_funding_potential(
    top_n: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get gaps ranked by funding potential."""
    ranked = funding_agent.rank_gaps_by_funding_potential(db, top_n)
    return {"gaps": ranked}


# Global state for fetch status
fetch_status = {"running": False, "progress": 0, "total": 0, "message": ""}
fetch_lock = threading.Lock()

def fetch_data_background():
    """Fetch data in background with proper database connection handling."""
    global fetch_status
    
    with fetch_lock:
        if fetch_status["running"]:
            return
        fetch_status["running"] = True
        fetch_status["progress"] = 0
        fetch_status["total"] = 0
        fetch_status["message"] = "Starting data fetch..."
    
    try:
        from longevity_map.database.session import SessionLocal
        from longevity_map.data_sources import pubmed
        from datetime import datetime, timedelta
        import time
        
        # Create a NEW database session for this background task
        db = SessionLocal()
        
        try:
            fetch_status["message"] = "Fetching papers from PubMed..."
            
            # Fetch papers first - start with just 3 for speed
            cutoff = datetime.now() - timedelta(days=30)
            papers = pubmed.fetch_recent(cutoff, max_results=3)
            
            fetch_status["total"] = len(papers)
            fetch_status["message"] = f"Processing {len(papers)} papers..."
            
            from longevity_map.agents.problem_parser import ProblemParser
            from longevity_map.agents.capability_extractor import CapabilityExtractor
            from longevity_map.models.problem import Problem
            from longevity_map.models.capability import Capability
            from longevity_map.models.mapping import ProblemCapabilityMapping
            from sqlalchemy.exc import OperationalError
            
            parser = ProblemParser()
            extractor = CapabilityExtractor()
            
            problems_added = 0
            
            for i, paper in enumerate(papers, 1):
                # Check if cancelled
                if not fetch_status["running"]:
                    break
                    
                try:
                    fetch_status["progress"] = i
                    fetch_status["message"] = f"Processing paper {i}/{len(papers)}: {paper['title'][:50]}..."
                    
                    # Check if exists
                    try:
                        existing = db.query(Problem).filter(
                            Problem.source == "pubmed",
                            Problem.source_id == paper['id']
                        ).first()
                    except OperationalError:
                        # DB locked on read, skip this paper
                        fetch_status["message"] = f"Paper {i}: Database busy, skipping..."
                        continue
                    
                    if existing:
                        continue
                    
                    # Parse problem
                    problem = parser.process(
                        paper.get("text", paper.get("abstract", "")),
                        source="pubmed",
                        source_id=paper['id']
                    )
                    
                    problem.source_url = f"https://pubmed.ncbi.nlm.nih.gov/{paper['id']}"
                    if paper.get('doi'):
                        problem.source_url = f"https://doi.org/{paper['doi']}"
                    
                    # Try to save problem - skip immediately if locked (don't block)
                    try:
                        db.add(problem)
                        db.flush()
                        problems_added += 1
                    except OperationalError as e:
                        if "locked" in str(e).lower():
                            fetch_status["message"] = f"Paper {i}: Database locked, skipping..."
                            logging.warning(f"Could not save paper {i}: database locked, skipping")
                            try:
                                db.rollback()
                            except:
                                pass
                            continue  # Skip to next paper immediately
                        else:
                            raise
                    
                    # Extract capabilities (with timeout protection)
                    try:
                        capabilities = extractor.process(
                            problem.description,
                            problem_id=problem.id
                        )
                    except Exception as e:
                        fetch_status["message"] = f"Paper {i}: Error extracting capabilities: {str(e)[:50]}..."
                        logging.error(f"Error extracting capabilities for paper {i}: {e}")
                        capabilities = []
                    
                    for cap in capabilities:
                        existing_cap = db.query(Capability).filter(
                            Capability.name == cap.name,
                            Capability.type == cap.type
                        ).first()
                        
                        if existing_cap:
                            cap = existing_cap
                        else:
                            # Try to save capability, but don't block forever
                            try:
                                db.add(cap)
                                db.flush()
                            except OperationalError as e:
                                if "locked" in str(e).lower():
                                    # Skip this capability if DB is locked
                                    logging.warning(f"Could not save capability {cap.name}: {e}")
                                    continue
                                else:
                                    raise
                        
                        # Create mapping
                        try:
                            mapping = ProblemCapabilityMapping(
                                problem_id=problem.id,
                                capability_id=cap.id,
                                confidence_score=0.8
                            )
                            db.add(mapping)
                            db.commit()
                        except OperationalError as e:
                            if "locked" in str(e).lower():
                                # Skip this mapping if DB is locked
                                logging.warning(f"Could not save mapping: {e}")
                                try:
                                    db.rollback()
                                except:
                                    pass
                                continue
                            else:
                                raise
                    
                except Exception as e:
                    error_msg = str(e)[:100]
                    fetch_status["message"] = f"Paper {i}: Error - {error_msg}... (skipping)"
                    logging.error(f"Error processing paper {i}: {e}", exc_info=True)
                    try:
                        db.rollback()
                    except:
                        pass
                    # Create new session
                    try:
                        db.close()
                    except:
                        pass
                    db = SessionLocal()
                    # Update progress even on error
                    fetch_status["progress"] = i
                    continue
            
            fetch_status["message"] = f"Completed! Added {problems_added} problems."
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = str(e)[:200]
        fetch_status["message"] = f"Error: {error_msg}"
        logging.error(f"Background fetch error: {e}", exc_info=True)
    finally:
        try:
            db.close()
        except:
            pass
        with fetch_lock:
            fetch_status["running"] = False
            if fetch_status["progress"] == 0:
                fetch_status["message"] = "Failed to start. Check API server logs."

@app.get("/search")
def conversational_search(query: str = Query(..., description="Natural language search query"), db: Session = Depends(get_db)):
    """
    Conversational search powered by GPT-4o.
    
    Examples:
    - "What problems need mouse models?"
    - "Show me gaps in mitochondrial research"
    - "What capabilities are needed for senolytic research?"
    - "Find problems related to telomeres"
    """
    from longevity_map.utils.llm_search import LLMSearch
    
    try:
        search_engine = LLMSearch()
        results = search_engine.search(query, db)
        return results
    except Exception as e:
        logging.error(f"Error in conversational search: {e}", exc_info=True)
        return {
            "query": query,
            "results": {},
            "summary": f"Search error: {str(e)}",
            "suggestions": []
        }

@app.post("/fetch-data")
def trigger_fetch_data(background_tasks: BackgroundTasks):
    """Trigger data fetch from sources (runs in background seamlessly)."""
    global fetch_status
    
    with fetch_lock:
        if fetch_status["running"]:
            return {
                "status": "already_running",
                "message": fetch_status["message"],
                "progress": fetch_status["progress"],
                "total": fetch_status["total"]
            }
        
        # Start background task
        background_tasks.add_task(fetch_data_background)
        
        return {
            "status": "started",
            "message": "Data fetch started in background. Use /fetch-status to check progress."
        }

@app.get("/fetch-status")
def get_fetch_status():
    """Get the status of the background data fetch."""
    return {
        "running": fetch_status["running"],
        "progress": fetch_status["progress"],
        "total": fetch_status["total"],
        "message": fetch_status["message"]
    }


@app.post("/fetch-cancel")
def cancel_fetch():
    """Cancel the running fetch (if stuck)."""
    global fetch_status
    with fetch_lock:
        if fetch_status["running"]:
            fetch_status["running"] = False
            fetch_status["message"] = "Cancelled by user"
            return {"status": "cancelled", "message": "Fetch cancelled"}
        return {"status": "not_running", "message": "No fetch in progress"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics."""
    from sqlalchemy import func
    
    num_problems = db.query(func.count(Problem.id)).scalar()
    num_capabilities = db.query(func.count(Capability.id)).scalar()
    num_resources = db.query(func.count(Resource.id)).scalar()
    num_gaps = db.query(func.count(Gap.id)).scalar()
    
    total_blocked_value = db.query(func.sum(Gap.blocked_research_value)).scalar() or 0
    
    return {
        "num_problems": num_problems,
        "num_capabilities": num_capabilities,
        "num_resources": num_resources,
        "num_gaps": num_gaps,
        "total_blocked_research_value": total_blocked_value
    }


if __name__ == "__main__":
    import uvicorn
    api_config = config.get("api", {})
    uvicorn.run(
        "longevity_map.api.main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=api_config.get("reload", True)
    )

