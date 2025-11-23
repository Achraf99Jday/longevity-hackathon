"""Script to run the visualization dashboard."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.visualization.dashboard import create_dashboard

if __name__ == "__main__":
    app = create_dashboard()
    app.run_server(debug=True, port=8050)

