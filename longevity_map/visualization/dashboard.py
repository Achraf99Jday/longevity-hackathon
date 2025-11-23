"""Interactive dashboard using Dash."""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from longevity_map.database.session import SessionLocal
from longevity_map.visualization.matrix import (
    create_problem_capability_heatmap,
    create_category_distribution,
    create_gap_priority_chart
)
from longevity_map.models.problem import ProblemCategory


def create_dashboard():
    """Create interactive Dash dashboard."""
    app = dash.Dash(__name__)
    
    db = next(SessionLocal())
    
    app.layout = html.Div([
        html.H1("Longevity R&D Map Dashboard", style={'textAlign': 'center'}),
        
        html.Div([
            dcc.Dropdown(
                id='category-filter',
                options=[
                    {'label': 'All Categories', 'value': 'all'}
                ] + [
                    {'label': cat.value.replace('_', ' ').title(), 'value': cat.value}
                    for cat in ProblemCategory
                ],
                value='all',
                style={'width': '300px', 'margin': '10px'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'center'}),
        
        html.Div([
            dcc.Graph(id='category-distribution'),
        ]),
        
        html.Div([
            dcc.Graph(id='problem-capability-matrix'),
        ]),
        
        html.Div([
            dcc.Graph(id='gap-priority-chart'),
        ]),
    ])
    
    @app.callback(
        [Output('category-distribution', 'figure'),
         Output('problem-capability-matrix', 'figure'),
         Output('gap-priority-chart', 'figure')],
        [Input('category-filter', 'value')]
    )
    def update_dashboard(category):
        db = next(SessionLocal())
        try:
            category_enum = ProblemCategory(category) if category != 'all' else None
            
            fig1 = create_category_distribution(db)
            fig2 = create_problem_capability_heatmap(db, category_enum)
            fig3 = create_gap_priority_chart(db)
            
            return fig1, fig2, fig3
        finally:
            db.close()
    
    return app


if __name__ == "__main__":
    app = create_dashboard()
    app.run_server(debug=True, port=8050)

