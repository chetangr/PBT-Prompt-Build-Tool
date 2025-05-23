"""Profile management for different environments - DBT-like profiles"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import os
from dataclasses import dataclass
import json


@dataclass
class Profile:
    """Represents a deployment/execution profile"""
    name: str
    target: str
    outputs: Dict[str, Dict[str, Any]]
    

class ProfileManager:
    """Manages environment profiles for PBT projects"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.profiles_path = self._find_profiles_file()
        self.profiles: Dict[str, Profile] = {}
        self.active_profile: Optional[str] = None
        self.active_target: Optional[str] = None
        
        if self.profiles_path and self.profiles_path.exists():
            self._load_profiles()
            
    def _find_profiles_file(self) -> Optional[Path]:
        """Find profiles.yml file in standard locations"""
        # Check project root first
        project_profiles = self.project_root / "profiles.yml"
        if project_profiles.exists():
            return project_profiles
            
        # Check user home directory
        home_profiles = Path.home() / ".pbt" / "profiles.yml"
        if home_profiles.exists():
            return home_profiles
            
        return None
        
    def _load_profiles(self) -> None:
        """Load profiles from YAML file"""
        with open(self.profiles_path, 'r') as f:
            data = yaml.safe_load(f) or {}
            
        for profile_name, profile_data in data.items():
            if profile_name == 'config':
                continue
                
            profile = Profile(
                name=profile_name,
                target=profile_data.get('target', 'dev'),
                outputs=profile_data.get('outputs', {})
            )
            
            self.profiles[profile_name] = profile
            
        # Set active profile from environment or config
        self.active_profile = os.environ.get('PBT_PROFILE') or data.get('config', {}).get('active_profile')
        self.active_target = os.environ.get('PBT_TARGET')
        
    def get_active_profile(self) -> Optional[Profile]:
        """Get the currently active profile"""
        if self.active_profile and self.active_profile in self.profiles:
            return self.profiles[self.active_profile]
        elif self.profiles:
            # Return first profile if no active set
            return next(iter(self.profiles.values()))
        return None
        
    def get_active_config(self) -> Dict[str, Any]:
        """Get configuration for active profile and target"""
        profile = self.get_active_profile()
        if not profile:
            return {}
            
        target = self.active_target or profile.target
        return profile.outputs.get(target, {})
        
    def set_active_profile(self, profile_name: str, target: str = None) -> None:
        """Set the active profile and optionally target"""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
            
        self.active_profile = profile_name
        if target:
            self.active_target = target
            
    def create_profile(self, name: str, outputs: Dict[str, Dict[str, Any]], 
                      target: str = 'dev', save: bool = True) -> Profile:
        """Create a new profile"""
        profile = Profile(name=name, target=target, outputs=outputs)
        self.profiles[name] = profile
        
        if save:
            self._save_profiles()
            
        return profile
        
    def _save_profiles(self) -> None:
        """Save profiles to YAML file"""
        if not self.profiles_path:
            # Create default location
            self.profiles_path = self.project_root / "profiles.yml"
            
        data = {}
        
        # Add config section
        if self.active_profile:
            data['config'] = {'active_profile': self.active_profile}
            
        # Add profiles
        for name, profile in self.profiles.items():
            data[name] = {
                'target': profile.target,
                'outputs': profile.outputs
            }
            
        with open(self.profiles_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
            
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration from active profile"""
        config = self.get_active_config()
        
        return {
            'provider': config.get('llm_provider', 'openai'),
            'model': config.get('llm_model', 'gpt-4'),
            'api_key': config.get('api_key') or os.environ.get(f"{config.get('llm_provider', 'OPENAI').upper()}_API_KEY"),
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('max_tokens', 2000),
            'timeout': config.get('timeout', 30),
            'retry_count': config.get('retry_count', 3)
        }
        
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration from active profile"""
        config = self.get_active_config()
        
        deployment = {
            'provider': config.get('deployment_provider', 'supabase'),
            'credentials': {}
        }
        
        # Provider-specific configurations
        provider = deployment['provider']
        
        if provider == 'supabase':
            deployment['credentials'] = {
                'url': config.get('supabase_url') or os.environ.get('SUPABASE_URL'),
                'anon_key': config.get('supabase_anon_key') or os.environ.get('SUPABASE_ANON_KEY'),
                'service_key': config.get('supabase_service_key') or os.environ.get('SUPABASE_SERVICE_KEY'),
                'table_name': config.get('table_name', 'prompts')
            }
        elif provider == 'firebase':
            deployment['credentials'] = {
                'project_id': config.get('firebase_project_id') or os.environ.get('FIREBASE_PROJECT_ID'),
                'credentials_path': config.get('firebase_credentials_path') or os.environ.get('FIREBASE_CREDENTIALS_PATH'),
                'collection': config.get('collection', 'prompts')
            }
        elif provider == 'huggingface':
            deployment['credentials'] = {
                'token': config.get('hf_token') or os.environ.get('HF_TOKEN'),
                'namespace': config.get('hf_namespace') or os.environ.get('HF_NAMESPACE'),
                'visibility': config.get('visibility', 'private')
            }
            
        return deployment
        
    def get_test_config(self) -> Dict[str, Any]:
        """Get test configuration from active profile"""
        config = self.get_active_config()
        
        return {
            'parallel': config.get('test_parallel', True),
            'fail_fast': config.get('test_fail_fast', False),
            'timeout': config.get('test_timeout', 60),
            'retries': config.get('test_retries', 1),
            'coverage_threshold': config.get('coverage_threshold', 0.8),
            'output_format': config.get('test_output_format', 'json')
        }
        
    def validate_profile(self, profile_name: str = None) -> List[str]:
        """Validate a profile has required configurations"""
        profile_name = profile_name or self.active_profile
        if not profile_name or profile_name not in self.profiles:
            return ["No valid profile found"]
            
        profile = self.profiles[profile_name]
        errors = []
        
        # Check each output target
        for target_name, target_config in profile.outputs.items():
            # Check LLM configuration
            if not target_config.get('llm_provider'):
                errors.append(f"Target '{target_name}' missing llm_provider")
                
            # Check API key availability
            provider = target_config.get('llm_provider', 'openai')
            if not target_config.get('api_key') and not os.environ.get(f"{provider.upper()}_API_KEY"):
                errors.append(f"Target '{target_name}' missing API key for {provider}")
                
            # Check deployment configuration if specified
            if target_config.get('deployment_provider'):
                dep_provider = target_config['deployment_provider']
                
                if dep_provider == 'supabase':
                    if not (target_config.get('supabase_url') or os.environ.get('SUPABASE_URL')):
                        errors.append(f"Target '{target_name}' missing Supabase URL")
                elif dep_provider == 'firebase':
                    if not (target_config.get('firebase_project_id') or os.environ.get('FIREBASE_PROJECT_ID')):
                        errors.append(f"Target '{target_name}' missing Firebase project ID")
                        
        return errors
        
    def export_env_template(self) -> str:
        """Generate environment variable template"""
        template = ["# PBT Environment Variables Template", ""]
        
        # Add profile variables
        template.extend([
            "# Profile Configuration",
            "export PBT_PROFILE=development",
            "export PBT_TARGET=dev",
            ""
        ])
        
        # Add LLM provider keys
        template.extend([
            "# LLM Provider API Keys",
            "export OPENAI_API_KEY=your_openai_key_here",
            "export ANTHROPIC_API_KEY=your_anthropic_key_here",
            "export MISTRAL_API_KEY=your_mistral_key_here",
            ""
        ])
        
        # Add deployment provider credentials
        template.extend([
            "# Deployment Provider Credentials",
            "# Supabase",
            "export SUPABASE_URL=your_supabase_url",
            "export SUPABASE_ANON_KEY=your_anon_key",
            "export SUPABASE_SERVICE_KEY=your_service_key",
            "",
            "# Firebase",
            "export FIREBASE_PROJECT_ID=your_project_id",
            "export FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json",
            "",
            "# HuggingFace",
            "export HF_TOKEN=your_hf_token",
            "export HF_NAMESPACE=your_namespace",
            ""
        ])
        
        return '\n'.join(template)