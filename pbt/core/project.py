"""PBT Project management and initialization"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class PBTProject:
    """Manages PBT project structure and configuration"""
    
    def __init__(self, project_dir: Path, config: Dict[str, Any]):
        self.project_dir = Path(project_dir)
        self.config = config
        
    @classmethod
    def init(cls, project_dir: Path, project_name: str, template: str = "default") -> "PBTProject":
        """Initialize a new PBT project"""
        project_dir = Path(project_dir)
        project_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        directories = [
            "prompts",
            "tests", 
            "evaluations",
            "chains",
            "chunks"
        ]
        
        for dir_name in directories:
            (project_dir / dir_name).mkdir(exist_ok=True)
        
        # Create pbt.yaml configuration
        config = {
            "name": project_name,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "prompts_dir": "prompts",
            "tests_dir": "tests",
            "evaluations_dir": "evaluations",
            "models": {
                "default": "claude",
                "available": [
                    "claude",
                    "claude-3", 
                    "gpt-4",
                    "gpt-3.5-turbo",
                    "mistral"
                ]
            },
            "settings": {
                "test_timeout": 30,
                "max_retries": 3,
                "save_reports": True,
                "optimization": {
                    "max_token_reduction": 0.7,
                    "preserve_examples": True
                }
            }
        }
        
        # Save configuration
        with open(project_dir / "pbt.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        # Create .env.example
        env_example = """# PBT Environment Variables
# Copy this file to .env and add your API keys

# Required for Claude support
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Required for OpenAI models
OPENAI_API_KEY=sk-your-key-here

# Optional: Mistral AI
MISTRAL_API_KEY=your-key-here

# Optional: Default settings
PBT_DEFAULT_MODEL=claude
PBT_TEST_TIMEOUT=30

# Optional: Cloud deployment
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
"""
        
        with open(project_dir / ".env.example", "w") as f:
            f.write(env_example)
        
        # Create example prompt if using default template
        if template == "default":
            cls._create_example_prompt(project_dir)
        
        return cls(project_dir, config)
    
    @staticmethod
    def _create_example_prompt(project_dir: Path):
        """Create an example prompt for new projects"""
        example_prompt = {
            "name": "Example-Text-Summarizer",
            "version": "1.0",
            "model": "claude",
            "description": "Example prompt that summarizes text content",
            "template": """Summarize the following text concisely:

Text: {{ text }}

Please provide a brief summary highlighting the key points.""",
            "variables": {
                "text": {
                    "type": "string",
                    "description": "Text content to summarize",
                    "required": True
                }
            },
            "metadata": {
                "tags": ["example", "summarization"],
                "author": "PBT",
                "created": datetime.now().isoformat()[:10]
            }
        }
        
        prompts_dir = project_dir / "prompts"
        with open(prompts_dir / "example_summarizer.prompt.yaml", "w") as f:
            yaml.dump(example_prompt, f, default_flow_style=False, sort_keys=False)
        
        # Create example test
        example_test = {
            "prompt_file": "prompts/example_summarizer.prompt.yaml",
            "test_cases": [
                {
                    "name": "short_text",
                    "inputs": {
                        "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
                    },
                    "expected_keywords": ["machine learning", "AI", "algorithms", "data"],
                    "quality_criteria": "Should mention key concepts: ML, AI, algorithms, learning from data"
                },
                {
                    "name": "longer_text", 
                    "inputs": {
                        "text": "Climate change refers to long-term shifts in global temperatures and weather patterns. While these shifts may be natural, human activities have been the main driver since the 1800s, primarily through burning fossil fuels."
                    },
                    "expected_keywords": ["climate change", "temperature", "human activities", "fossil fuels"],
                    "quality_criteria": "Should summarize main points about climate change causes"
                }
            ]
        }
        
        tests_dir = project_dir / "tests"
        with open(tests_dir / "example_summarizer.test.yaml", "w") as f:
            yaml.dump(example_test, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def load(cls, project_dir: Path = None) -> Optional["PBTProject"]:
        """Load existing PBT project"""
        if project_dir is None:
            project_dir = Path.cwd()
        
        config_file = project_dir / "pbt.yaml"
        if not config_file.exists():
            return None
        
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        return cls(project_dir, config)
    
    def get_prompts_dir(self) -> Path:
        """Get prompts directory path"""
        return self.project_dir / self.config.get("prompts_dir", "prompts")
    
    def get_tests_dir(self) -> Path:
        """Get tests directory path"""
        return self.project_dir / self.config.get("tests_dir", "tests")
    
    def get_evaluations_dir(self) -> Path:
        """Get evaluations directory path"""
        return self.project_dir / self.config.get("evaluations_dir", "evaluations")
    
    def get_default_model(self) -> str:
        """Get default model for the project"""
        return self.config.get("models", {}).get("default", "claude")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.config.get("models", {}).get("available", ["claude", "gpt-4"])
    
    def save_config(self):
        """Save project configuration"""
        with open(self.project_dir / "pbt.yaml", "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)