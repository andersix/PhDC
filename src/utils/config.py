# src/utils/config.py
import yaml
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict
from .constants import CONFIG_DIR, LOG_DIR
from .exceptions import ConfigError

class Config:
    """Configuration handler for PiHole Display"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self._load_config()
            self._setup_logging()
    
    def _load_config(self) -> None:
        """Load configuration from yaml file"""
        config_file = CONFIG_DIR / 'config.yaml'
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load config: {str(e)}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_config = self._config.get('logging', {})
        LOG_DIR.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    LOG_DIR / log_config.get('file', 'display_controller.log'),
                    maxBytes=log_config.get('max_bytes', 1048576),
                    backupCount=log_config.get('backup_count', 5)
                )
            ]
        )
    
    @property
    def display(self) -> Dict[str, Any]:
        """Get display configuration"""
        return self._config.get('display', {})
    
    @property
    def buttons(self) -> Dict[str, Any]:
        """Get buttons configuration"""
        return self._config.get('buttons', {})

