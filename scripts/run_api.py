"""Script to run the API server."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from longevity_map.api.main import app
import uvicorn
import yaml

config_path = Path(__file__).parent.parent / "config" / "config.yaml"
if not config_path.exists():
    config_path = Path(__file__).parent.parent / "config" / "config.example.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

api_config = config.get("api", {})

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=api_config.get("reload", True)
    )

