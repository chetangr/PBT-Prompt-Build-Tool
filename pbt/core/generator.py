"""
PBT Prompt Generator
"""

import os
import yaml
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI

class PromptGenerator:
    """Handles prompt generation using LLMs"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
    
    def _get_anthropic_client(self) -> Anthropic:
        """Get Anthropic client with API key validation"""
        if not self.anthropic_client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.anthropic_client = Anthropic(api_key=api_key)
        return self.anthropic_client
    
    def _get_openai_client(self) -> OpenAI:
        """Get OpenAI client with API key validation"""
        if not self.openai_client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.openai_client = OpenAI(api_key=api_key)
        return self.openai_client
    
    def generate(
        self, 
        goal: str, 
        model: str = "claude",
        style: str = "professional",
        variables: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a structured prompt from a goal description"""
        
        variables = variables or []
        
        system_prompt = f"""You are an expert prompt engineer. Generate a structured prompt template for this goal: "{goal}"

Return a YAML structure with:
- name: snake_case name (no spaces, lowercase, underscores)
- version: "0.1.0" 
- description: brief description (1-2 sentences)
- variables: list of input variables needed
- template: the actual prompt template with {{{{ variable }}}} placeholders
- examples: 2-3 example inputs/outputs showing usage
- tags: relevant tags for categorization
- model_config: recommended model settings (temperature, max_tokens)

Requirements:
- Style: {style}
- Variables to include: {variables if variables else 'determine automatically'}
- Template should be clear, specific, and effective
- Examples should be realistic and helpful
- Use proper YAML formatting

Return ONLY the YAML structure, no additional text."""

        try:
            if model == "claude":
                client = self._get_anthropic_client()
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": system_prompt}]
                )
                content = response.content[0].text
            elif model == "openai":
                client = self._get_openai_client()
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": system_prompt}],
                    max_tokens=1500
                )
                content = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported model: {model}")

            # Parse the YAML response
            try:
                prompt_yaml = yaml.safe_load(content)
                return {"success": True, "prompt_yaml": prompt_yaml, "raw_content": content}
            except yaml.YAMLError as e:
                return {"success": False, "raw_content": content, "error": str(e)}
                
        except Exception as e:
            raise Exception(f"Error generating prompt: {str(e)}")
    
    def compare_models(self, prompt: str, models: List[str]) -> Dict[str, Any]:
        """Run the same prompt across multiple models and compare outputs"""
        
        results = {}
        
        for model in models:
            try:
                if model == "claude":
                    client = self._get_anthropic_client()
                    response = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=500,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    results[model] = response.content[0].text
                elif model == "gpt-4":
                    client = self._get_openai_client()
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500
                    )
                    results[model] = response.choices[0].message.content
                elif model == "mistral":
                    # Placeholder for Mistral API integration
                    results[model] = "Mistral integration coming soon"
                else:
                    results[model] = f"Model {model} not supported"
            except Exception as e:
                results[model] = f"Error: {str(e)}"
        
        return {"results": results}
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render a prompt template with variables"""
        
        rendered = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered