"""
PBT Project Management
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

class PBTProject:
    """Manages PBT project structure and configuration"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.config_file = self.project_dir / "pbt.yaml"
    
    @classmethod
    def init(cls, project_dir: Path, name: str, template: str = "default") -> "PBTProject":
        """Initialize a new PBT project"""
        
        project_dir = Path(project_dir)
        project_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        (project_dir / "prompts").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "evaluations").mkdir(exist_ok=True)
        
        # Create pbt.yaml configuration
        config = {
            "name": name,
            "version": "0.1.0",
            "description": f"PBT project: {name}",
            "created_at": datetime.now().isoformat(),
            "template": template,
            "models": ["claude", "gpt-4"],
            "eval_criteria": ["accuracy", "relevance", "safety"],
            "directories": {
                "prompts": "prompts",
                "tests": "tests", 
                "evaluations": "evaluations"
            },
            "defaults": {
                "model": "claude",
                "style": "professional",
                "test_count": 5
            }
        }
        
        with open(project_dir / "pbt.yaml", 'w') as f:
            yaml.dump(config, f, indent=2)
        
        # Create .env.example
        env_example = """# PBT Configuration
# Copy this file to .env and add your actual API keys

# Required for prompt generation and evaluation
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Required for database functionality (free tier available at supabase.com)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional: Server configuration
PBT_SERVER_HOST=127.0.0.1
PBT_SERVER_PORT=8000

# Optional: Stripe for marketplace functionality
STRIPE_SECRET_KEY=sk_test_your-stripe-key

# Optional: Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
"""
        
        with open(project_dir / ".env.example", 'w') as f:
            f.write(env_example)
        
        # Create sample prompt
        sample_prompt = {
            "name": "sample_prompt",
            "version": "0.1.0",
            "description": "A sample prompt to get you started",
            "variables": ["input_text"],
            "template": "Please analyze the following text and provide insights:\n\n{{ input_text }}",
            "examples": [
                {
                    "input": {"input_text": "The quick brown fox jumps over the lazy dog"},
                    "output": "This is a pangram containing all letters of the alphabet..."
                }
            ],
            "tags": ["analysis", "sample"],
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
        
        with open(project_dir / "prompts" / "sample_prompt.yaml", 'w') as f:
            yaml.dump(sample_prompt, f, indent=2)
        
        # Create .gitignore
        gitignore = """.env
*.pyc
__pycache__/
.pytest_cache/
.coverage
.venv/
venv/
node_modules/
.DS_Store
evaluations/*.json
*.log
"""
        
        with open(project_dir / ".gitignore", 'w') as f:
            f.write(gitignore)
        
        return cls(project_dir)
    
    def load_config(self) -> dict:
        """Load project configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"No pbt.yaml found in {self.project_dir}")
        
        with open(self.config_file) as f:
            return yaml.safe_load(f)
    
    def get_prompts_dir(self) -> Path:
        """Get prompts directory"""
        config = self.load_config()
        prompts_dir = config.get("directories", {}).get("prompts", "prompts")
        return self.project_dir / prompts_dir
    
    def get_tests_dir(self) -> Path:
        """Get tests directory"""
        config = self.load_config()
        tests_dir = config.get("directories", {}).get("tests", "tests")
        return self.project_dir / tests_dir
    
    def get_evaluations_dir(self) -> Path:
        """Get evaluations directory"""
        config = self.load_config()
        evals_dir = config.get("directories", {}).get("evaluations", "evaluations")
        return self.project_dir / evals_dir
    
    def list_prompts(self) -> list:
        """List all prompt files in the project"""
        prompts_dir = self.get_prompts_dir()
        if not prompts_dir.exists():
            return []
        
        return list(prompts_dir.glob("*.yaml")) + list(prompts_dir.glob("*.yml"))
    
    @classmethod
    def find_project_root(cls, start_path: Optional[Path] = None) -> Optional[Path]:
        """Find the project root by looking for pbt.yaml"""
        current = Path(start_path or Path.cwd()).resolve()
        
        while current != current.parent:
            if (current / "pbt.yaml").exists():
                return current
            current = current.parent
        
        return None