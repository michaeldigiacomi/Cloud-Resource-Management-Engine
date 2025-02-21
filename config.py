from typing import Dict, Any
import yaml

class Config:
    def __init__(self, config_file: str = "config.yaml"):
        self.config: Dict[str, Any] = {}
        self.load_config(config_file)

    def load_config(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    @property
    def retry_attempts(self) -> int:
        return self.config.get('retry_attempts', 3)

    @property
    def cache_timeout(self) -> int:
        return self.config.get('cache_timeout', 300)

    @property
    def log_level(self) -> str:
        return self.config.get('log_level', 'INFO')
