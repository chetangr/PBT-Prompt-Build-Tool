from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
import yaml
import os
from anthropic import Anthropic
from openai import OpenAI

router = APIRouter()

class PromptGenRequest(BaseModel):
    goal: str
    model: str = "claude"
    variables: list = []
    style: str = "professional"

def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    return Anthropic(api_key=api_key)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    return OpenAI(api_key=api_key)

@router.post("/generate")
def generate_prompt(request: PromptGenRequest):
    """Generate a structured prompt YAML from a goal description"""
    
    system_prompt = f"""You are an expert prompt engineer. Generate a structured prompt template for this goal: "{request.goal}"

Return a YAML structure with:
- name: snake_case name
- version: "0.1.0" 
- description: brief description
- variables: list of input variables
- template: the actual prompt template with {{{{ variable }}}} placeholders
- examples: 2-3 example inputs/outputs
- tags: relevant tags
- model_config: recommended model settings

Style: {request.style}
Variables to include: {request.variables}"""

    try:
        if request.model == "claude":
            client = get_anthropic_client()
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": system_prompt}]
            )
            content = response.content[0].text
        elif request.model == "openai":
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": system_prompt}],
                max_tokens=1000
            )
            content = response.choices[0].message.content
        else:
            raise HTTPException(status_code=400, detail="Unsupported model")

        # Parse the YAML response
        try:
            prompt_yaml = yaml.safe_load(content)
            return {"success": True, "prompt_yaml": prompt_yaml, "raw_content": content}
        except yaml.YAMLError:
            return {"success": True, "raw_content": content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

@router.post("/render")
def render_prompt(template: str = Body(...), variables: dict = Body(...)):
    """Render a prompt template with variables"""
    try:
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return {"rendered": rendered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error rendering template: {str(e)}")

@router.post("/compare")
def compare_models(prompt: str = Body(...), models: list = Body(...)):
    """Run the same prompt across multiple models and compare outputs"""
    results = {}
    
    for model in models:
        try:
            if model == "claude":
                client = get_anthropic_client()
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                results[model] = response.content[0].text
            elif model == "gpt-4":
                client = get_openai_client()
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                results[model] = response.choices[0].message.content
            elif model == "mistral":
                # Placeholder for Mistral API integration
                results[model] = "Mistral integration coming soon"
        except Exception as e:
            results[model] = f"Error: {str(e)}"
    
    return {"results": results}