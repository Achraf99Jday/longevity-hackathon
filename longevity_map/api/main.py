"""FastAPI application for longevity R&D map."""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import yaml
from pathlib import Path

from longevity_map.database.session import get_db, init_db
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.models.capability import Capability, CapabilityType
from longevity_map.models.resource import Resource, ResourceType
from longevity_map.models.gap import Gap, GapPriority
from longevity_map.models.mapping import ProblemCapabilityMapping, CapabilityResourceMapping
from longevity_map.agents.gap_analyzer import GapAnalyzer
from longevity_map.agents.coordination_agent import CoordinationAgent
from longevity_map.agents.funding_agent import FundingAgent

# Initialize database
init_db()

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
if not config_path.exists():
    config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

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

