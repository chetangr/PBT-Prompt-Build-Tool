"""
PBT Configuration Management
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel

class PBTConfig(BaseModel):
    """PBT configuration model"""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Database
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Server
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    
    # Defaults
    default_model: str = "claude"
    default_style: str = "professional"
    
    # Paths
    prompts_dir: str = "prompts"
    tests_dir: str = "tests"
    evaluations_dir: str = "evaluations"
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "PBTConfig":
        """Load configuration from file and environment"""
        
        # Start with environment variables
        config_data = {
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "supabase_url": os.getenv("SUPABASE_URL"),
            "supabase_key": os.getenv("SUPABASE_KEY"),
        }
        
        # Load from config file if provided
        if config_path and config_path.exists():
            with open(config_path) as f:
                file_config = yaml.safe_load(f)
                config_data.update(file_config)
        
        # Try to load from default locations
        default_configs = [
            Path.cwd() / "pbt.yaml",
            Path.cwd() / "pbt.yml",
            Path.home() / ".pbt" / "config.yaml",
        ]
        
        for default_config in default_configs:
            if default_config.exists():
                with open(default_config) as f:
                    file_config = yaml.safe_load(f)
                    # Don't override existing values
                    for key, value in file_config.items():
                        if key not in config_data or config_data[key] is None:
                            config_data[key] = value
                break
        
        return cls(**{k: v for k, v in config_data.items() if v is not None})
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present"""
        return {
            "anthropic": bool(self.anthropic_api_key),
            "openai": bool(self.openai_api_key),
            "supabase": bool(self.supabase_url and self.supabase_key),
        }