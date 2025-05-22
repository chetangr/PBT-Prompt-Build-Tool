"""
PBT Runtime - Core execution engine for prompts
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import openai

# Ensure env vars are loaded
load_dotenv()

class PromptRunner:
    """Run individual prompt YAML files"""
    
    def __init__(self, prompt_file):
        self.prompt_file = Path(prompt_file)
        self.prompt_data = self._load_prompt()
        
        # Initialize LLM clients
        self.anthropic_client = None
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def _load_prompt(self):
        """Load prompt from YAML file"""
        with open(self.prompt_file, 'r') as f:
            return yaml.safe_load(f)
    
    def run(self, variables, model=None):
        """Run the prompt with given variables"""
        template = self.prompt_data['template']
        model = model or self.prompt_data.get('model', 'gpt-4')
        
        # Render template with variables
        content = template
        for key, value in variables.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))
        
        # Call appropriate LLM
        if model.startswith('claude') and self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": content}]
            )
            return response.content[0].text.strip()
        
        elif model.startswith('gpt'):
            try:
                # Try new OpenAI API (v1.0+)
                client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": content}]
                )
                return response.choices[0].message.content.strip()
            except AttributeError:
                # Fallback to old OpenAI API
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": content}]
                )
                return response.choices[0].message["content"].strip()
        
        else:
            raise ValueError(f"Model {model} not supported or API key missing")