"""Base agent class for all agents in the framework."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the longevity R&D mapping system."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize agent with configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
            if not config_path.exists():
                config_path = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                self.config = {}
                logger.warning(f"No config file found at {config_path}, using defaults")
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}, using defaults")
            self.config = {}
        
        self.agent_config = self.config.get("agents", {}).get(self.__class__.__name__.lower(), {})
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return results."""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        getattr(self.logger, level.lower())(message)

