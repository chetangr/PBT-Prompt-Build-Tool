"""
PBT Prompt Evaluator
"""

import os
import yaml
import json
from typing import List, Dict, Any
from anthropic import Anthropic

class PromptEvaluator:
    """Handles prompt testing and evaluation"""
    
    def __init__(self):
        self.anthropic_client = None
    
    def _get_anthropic_client(self) -> Anthropic:
        """Get Anthropic client with API key validation"""
        if not self.anthropic_client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.anthropic_client = Anthropic(api_key=api_key)
        return self.anthropic_client
    
    def generate_tests(
        self, 
        prompt_yaml: str, 
        num_tests: int = 5,
        test_type: str = "functional"
    ) -> Dict[str, Any]:
        """Generate test cases for a prompt template"""
        
        try:
            prompt_data = yaml.safe_load(prompt_yaml)
            
            system_prompt = f"""Generate {num_tests} test cases for this prompt:

Prompt Template: {prompt_data.get('template', '')}
Description: {prompt_data.get('description', '')}
Variables: {prompt_data.get('variables', [])}

Generate test cases of type: {test_type}

Test types:
- functional: Normal use cases with expected inputs/outputs
- edge_case: Boundary conditions, empty inputs, unusual data
- performance: Tests for response quality and consistency

Return JSON with this exact structure:
{{
  "tests": [
    {{
      "name": "descriptive_test_name",
      "inputs": {{"variable_name": "test_value"}},
      "expected_output": "what the output should contain or accomplish",
      "test_type": "{test_type}",
      "criteria": "specific criteria for pass/fail evaluation"
    }}
  ]
}}

Make sure:
- Test names are descriptive and unique
- Inputs match the prompt variables exactly
- Expected outputs are specific and measurable
- Criteria are clear for evaluation

Return ONLY the JSON structure."""

            client = self._get_anthropic_client()
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
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
            raise Exception(f"Error generating tests: {str(e)}")
    
    def run_tests(
        self, 
        prompt_template: str, 
        tests: List[Dict], 
        model: str = "claude"
    ) -> Dict[str, Any]:
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
                    client = self._get_anthropic_client()
                    response = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": rendered_prompt}]
                    )
                    actual_output = response.content[0].text
                else:
                    actual_output = "Model not implemented"
                
                # Evaluate with Claude as judge
                evaluation = self._judge_output(
                    test.get("expected_output", ""),
                    actual_output,
                    test.get("criteria", "similarity")
                )
                
                results.append({
                    "test_name": test.get("name", "unnamed"),
                    "inputs": test.get("inputs", {}),
                    "expected": test.get("expected_output", ""),
                    "actual": actual_output,
                    "passed": evaluation["passed"],
                    "score": evaluation["score"],
                    "explanation": evaluation["explanation"],
                    "criteria": test.get("criteria", "")
                })
                
            except Exception as e:
                results.append({
                    "test_name": test.get("name", "unnamed"),
                    "error": str(e),
                    "passed": False,
                    "score": 0
                })
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("passed", False))
        total_score = sum(r.get("score", 0) for r in results)
        avg_score = total_score / total_tests if total_tests > 0 else 0
        
        return {
            "results": results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "average_score": avg_score
            }
        }
    
    def _judge_output(self, expected: str, actual: str, criteria: str) -> Dict[str, Any]:
        """Use Claude to judge output quality"""
        
        judge_prompt = f"""You are an expert evaluator. Judge this prompt output on a scale of 1-10.

Expected Output: {expected}
Actual Output: {actual}
Evaluation Criteria: {criteria}

Consider:
- How well does the actual output meet the expected requirements?
- Does it follow the specified criteria?
- Is it accurate, relevant, and well-formatted?
- Are there any significant errors or omissions?

Scoring:
- 9-10: Excellent, exceeds expectations
- 7-8: Good, meets expectations well
- 5-6: Acceptable, meets basic requirements
- 3-4: Poor, significant issues
- 1-2: Very poor, fails requirements

Return your evaluation in this exact format:
Score: X/10
Passed: true/false (true if score >= 6)
Explanation: [Your detailed analysis in 1-2 sentences]"""

        try:
            client = self._get_anthropic_client()
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": judge_prompt}]
            )
            
            content = response.content[0].text
            
            # Extract score and passed status
            score = 5  # Default
            passed = False
            explanation = content
            
            lines = content.split('\n')
            for line in lines:
                if 'Score:' in line:
                    try:
                        score_text = line.split('Score:')[1].strip()
                        score = int(score_text.split('/')[0])
                    except (ValueError, IndexError):
                        pass
                elif 'Passed:' in line:
                    passed = 'true' in line.lower()
                elif 'Explanation:' in line:
                    explanation = line.split('Explanation:')[1].strip()
            
            # Fallback: determine passed status from score
            if score >= 6:
                passed = True
                
            return {
                "score": score,
                "passed": passed,
                "explanation": explanation
            }
            
        except Exception as e:
            return {
                "score": 0,
                "passed": False,
                "explanation": f"Error during evaluation: {str(e)}"
            }
    
    def run_evaluation(self, test_case: Dict, model: str = "claude") -> Dict[str, Any]:
        """Run a single evaluation case"""
        
        prompt_id = test_case.get("prompt_id", "test")
        test_cases = [test_case]
        
        # This would integrate with the test runner
        # For now, return a mock structure
        return {
            "prompt_id": prompt_id,
            "summary": {
                "total": 1,
                "passed": 1,
                "average_score": 8.5
            },
            "results": [test_case]
        }