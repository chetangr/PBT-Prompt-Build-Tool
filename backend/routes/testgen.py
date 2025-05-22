from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
import yaml
import json
import os
from anthropic import Anthropic

router = APIRouter()

class TestGenRequest(BaseModel):
    prompt_yaml: str
    num_tests: int = 5
    test_type: str = "functional"  # functional, edge_case, performance

def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    return Anthropic(api_key=api_key)

@router.post("/generate")
def generate_tests(request: TestGenRequest):
    """Generate test cases for a prompt template"""
    
    try:
        prompt_data = yaml.safe_load(request.prompt_yaml)
        
        system_prompt = f"""Generate {request.num_tests} test cases for this prompt:

Prompt: {prompt_data.get('template', '')}
Description: {prompt_data.get('description', '')}
Variables: {prompt_data.get('variables', [])}

Generate test cases of type: {request.test_type}

Return JSON with this structure:
{{
  "tests": [
    {{
      "name": "test_name",
      "inputs": {{"variable": "value"}},
      "expected_output": "expected result",
      "test_type": "{request.test_type}",
      "criteria": "what to check for"
    }}
  ]
}}"""

        client = get_anthropic_client()
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": system_prompt}]
        )
        
        content = response.content[0].text
        
        # Try to parse as JSON
        try:
            test_data = json.loads(content)
            return {"success": True, "tests": test_data.get("tests", [])}
        except json.JSONDecodeError:
            return {"success": False, "raw_content": content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tests: {str(e)}")

@router.post("/run")
def run_tests(prompt_template: str = Body(...), tests: list = Body(...), model: str = Body("claude")):
    """Run test cases against a prompt template"""
    
    results = []
    
    for test in tests:
        try:
            # Render the prompt with test inputs
            rendered_prompt = prompt_template
            for key, value in test.get("inputs", {}).items():
                rendered_prompt = rendered_prompt.replace(f"{{{{{key}}}}}", str(value))
            
            # Get model output
            if model == "claude":
                client = get_anthropic_client()
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": rendered_prompt}]
                )
                actual_output = response.content[0].text
            else:
                actual_output = "Model not implemented"
            
            # Simple pass/fail logic (could be enhanced with LLM judge)
            expected = test.get("expected_output", "")
            passed = expected.lower() in actual_output.lower() if expected else True
            
            results.append({
                "test_name": test.get("name", "unnamed"),
                "inputs": test.get("inputs", {}),
                "expected": expected,
                "actual": actual_output,
                "passed": passed,
                "criteria": test.get("criteria", "")
            })
            
        except Exception as e:
            results.append({
                "test_name": test.get("name", "unnamed"),
                "error": str(e),
                "passed": False
            })
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get("passed", False))
    
    return {
        "results": results,
        "summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
    }