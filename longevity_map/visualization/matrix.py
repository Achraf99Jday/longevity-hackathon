"""Visualization for problem-capability matrices."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from longevity_map.database.session import SessionLocal
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.models.mapping import ProblemCapabilityMapping


def create_problem_capability_heatmap(db: Session, category: ProblemCategory = None) -> go.Figure:
    """Create a heatmap of problems vs capabilities."""
    query = db.query(Problem)
    if category:
        query = query.filter(Problem.category == category)
    
    problems = query.all()
    
    # Build matrix
    problem_ids = [p.id for p in problems]
    problem_titles = [p.title[:50] for p in problems]  # Truncate for display
    
    # Get all capabilities
    all_capabilities = set()
    for problem in problems:
        mappings = db.query(ProblemCapabilityMapping).filter(
            ProblemCapabilityMapping.problem_id == problem.id
        ).all()
        for mapping in mappings:
            all_capabilities.add((mapping.capability_id, mapping.capability.name))
    
    capability_ids = [cap_id for cap_id, _ in sorted(all_capabilities)]
    capability_names = [name[:50] for _, name in sorted(all_capabilities)]
    
    # Build matrix data
    matrix_data = []
    for problem_id in problem_ids:
        row = []
        mappings = db.query(ProblemCapabilityMapping).filter(
            ProblemCapabilityMapping.problem_id == problem_id
        ).all()
        mapping_dict = {m.capability_id: m.confidence_score for m in mappings}
        
        for cap_id in capability_ids:
            row.append(mapping_dict.get(cap_id, 0.0))
        matrix_data.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=capability_names,
        y=problem_titles,
        colorscale='Viridis',
        colorbar=dict(title="Confidence Score")
    ))
    
    fig.update_layout(
        title="Problem-Capability Matrix",
        xaxis_title="Capabilities",
        yaxis_title="Problems",
        height=max(600, len(problems) * 20),
        width=max(800, len(capability_ids) * 15)
    )
    
    return fig


def create_category_distribution(db: Session) -> go.Figure:
    """Create a bar chart of problems by category."""
    from sqlalchemy import func
    
    category_counts = db.query(
        Problem.category,
        func.count(Problem.id).label('count')
    ).group_by(Problem.category).all()
    
    categories = [cat.value.replace('_', ' ').title() for cat, _ in category_counts]
    counts = [count for _, count in category_counts]
    
    fig = go.Figure(data=go.Bar(
        x=categories,
        y=counts,
        marker_color='steelblue'
    ))
    
    fig.update_layout(
        title="Problems by Hallmark of Aging",
        xaxis_title="Category",
        yaxis_title="Number of Problems",
        xaxis_tickangle=-45
    )
    
    return fig


def create_gap_priority_chart(db: Session) -> go.Figure:
    """Create a chart showing gaps by priority."""
    from longevity_map.models.gap import Gap
    from sqlalchemy import func
    
    priority_counts = db.query(
        Gap.priority,
        func.count(Gap.id).label('count'),
        func.sum(Gap.blocked_research_value).label('total_value')
    ).group_by(Gap.priority).all()
    
    priorities = [p.value.title() for p, _, _ in priority_counts]
    counts = [c for _, c, _ in priority_counts]
    values = [v / 1_000_000 if v else 0 for _, _, v in priority_counts]  # Convert to millions
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=priorities,
        y=counts,
        name="Number of Gaps",
        yaxis='y',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=priorities,
        y=values,
        name="Blocked Research Value ($M)",
        yaxis='y2',
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title="Gaps by Priority",
        xaxis_title="Priority",
        yaxis=dict(title="Number of Gaps", side="left"),
        yaxis2=dict(title="Blocked Research Value ($M)", overlaying="y", side="right"),
        barmode='group'
    )
    
    return fig

