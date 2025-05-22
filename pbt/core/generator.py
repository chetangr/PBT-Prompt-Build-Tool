"""
PBT Prompt Generator
"""

import os
import yaml
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI

# Ensure .env files are loaded
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from current directory and upward
except ImportError:
    pass

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
                # Provide helpful error message with debugging info
                from pathlib import Path
                cwd = Path.cwd()
                env_files = []
                
                # Check for .env files
                if (cwd / ".env").exists():
                    env_files.append(str(cwd / ".env"))
                
                for parent in cwd.parents:
                    if (parent / ".env").exists():
                        env_files.append(str(parent / ".env"))
                        break
                
                error_msg = "ANTHROPIC_API_KEY environment variable is required.\n\n"
                error_msg += "💡 To fix this:\n"
                error_msg += "1. Get your API key from: https://console.anthropic.com\n"
                error_msg += "2. Add it to your .env file:\n"
                error_msg += "   echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' >> .env\n\n"
                
                if env_files:
                    error_msg += f"📁 Found .env files: {', '.join(env_files)}\n"
                    error_msg += "   Make sure ANTHROPIC_API_KEY is set in one of these files.\n"
                else:
                    error_msg += "📁 No .env files found. Create one in your project directory:\n"
                    error_msg += f"   echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' > {cwd}/.env\n"
                
                error_msg += f"\n🔍 Current directory: {cwd}\n"
                error_msg += f"🔍 Environment variables checked: {list(os.environ.keys())[:5]}...\n"
                
                raise ValueError(error_msg)
            
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
                # Remove markdown code blocks if present
                clean_content = content.strip()
                if clean_content.startswith('```yaml'):
                    clean_content = clean_content[7:]  # Remove ```yaml
                elif clean_content.startswith('```'):
                    clean_content = clean_content[3:]   # Remove ```
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3]  # Remove closing ```
                
                clean_content = clean_content.strip()
                
                prompt_yaml = yaml.safe_load(clean_content)
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
    
    def generate_jsonl_tests(
        self, 
        prompt_yaml: str, 
        num_tests: int = 6,
        test_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate JSONL test cases for a prompt template"""
        
        if test_types is None:
            test_types = ["functional", "edge_case", "error_handling"]
        
        try:
            prompt_data = yaml.safe_load(prompt_yaml)
            
            # Extract variables from template
            template = prompt_data.get('template', '')
            import re
            variables = re.findall(r'\{\{\s*(\w+)\s*\}\}', template)
            
            system_prompt = f"""Generate {num_tests} JSONL test cases for this prompt template:

PROMPT TEMPLATE: {template}
VARIABLES FOUND: {variables}
DESCRIPTION: {prompt_data.get('description', '')}
GOAL: {prompt_data.get('name', '')}

Generate diverse test cases covering:
- Functional tests: Normal use cases with realistic inputs
- Edge cases: Short input, long input, unusual formatting
- Error handling: Missing data, malformed input

For each test case, create realistic, substantial inputs that would be used in production.

Return ONLY a JSON array where each item has this exact structure:
{{
  "test_name": "descriptive_name",
  "inputs": {{"variable_name": "realistic_test_content"}},
  "expected_keywords": ["keyword1", "keyword2", "keyword3"],
  "quality_criteria": "specific description of what makes a good response"
}}

CRITICAL REQUIREMENTS:
1. Make inputs substantial and realistic - not placeholder text
2. Include 3-5 relevant expected_keywords for each test
3. Write specific quality_criteria describing what success looks like
4. Create diverse test scenarios covering different use cases
5. Variables to populate: {variables}

Return ONLY the JSON array, no other text."""

            client = self._get_anthropic_client()
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": system_prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # Try to parse as JSON
            try:
                test_cases = json.loads(content)
                if isinstance(test_cases, list):
                    return {"success": True, "test_cases": test_cases}
                else:
                    return {"success": False, "error": "Response is not a JSON array", "raw_content": content}
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Invalid JSON: {str(e)}", "raw_content": content}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_jsonl_tests(self, test_cases: List[Dict], output_file: str) -> bool:
        """Save test cases to a JSONL file"""
        try:
            with open(output_file, 'w') as f:
                for test_case in test_cases:
                    f.write(json.dumps(test_case) + '\n')
            return True
        except Exception as e:
            print(f"Error saving JSONL file: {e}")
            return False