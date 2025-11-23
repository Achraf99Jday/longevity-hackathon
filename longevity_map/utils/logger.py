"""Logging utilities."""

import logging
import sys
from pathlib import Path
import yaml


def setup_logging(config_path: Path = None):
    """Setup logging configuration."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if not config_path.exists():
            config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        log_config = config.get("logging", {})
        level = log_config.get("level", "INFO")
        log_file = log_config.get("file")
    except:
        level = "INFO"
        log_file = None
    
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

