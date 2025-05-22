import os
from anthropic import Anthropic
from openai import OpenAI

# Initialize clients with proper error handling
def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return Anthropic(api_key=api_key)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)

def generate_prompt_llm(prompt: str, model: str = "claude"):
    """Generate a response using the specified LLM"""
    try:
        if model == "claude":
            client = get_anthropic_client()
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif model == "openai" or model == "gpt-4":
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Model {model} not supported")
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")

def judge_prompt_output(reference: str, output: str, criteria: str = "similarity"):
    """Use Claude to judge prompt output quality"""
    judge_prompt = f"""
    You are an expert prompt evaluator. Rate the quality of this output on a scale of 1-10.
    
    Reference/Expected: {reference}
    Actual Output: {output}
    Evaluation Criteria: {criteria}
    
    Provide:
    1. Score (1-10)
    2. Brief explanation
    3. Specific strengths and weaknesses
    
    Format: Score: X/10
    Explanation: [your analysis]
    """
    
    try:
        client = get_anthropic_client()
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        
        content = response.content[0].text
        
        # Extract score
        score_line = [line for line in content.split('\n') if 'Score:' in line]
        if score_line:
            score_text = score_line[0].split('Score:')[1].strip()
            try:
                score = int(score_text.split('/')[0])
            except ValueError:
                score = 5  # Default score if parsing fails
        else:
            score = 5  # Default score if no score line found
            
        return {
            "score": score,
            "explanation": content,
            "passed": score >= 6
        }
    except Exception as e:
        raise Exception(f"Error judging output: {str(e)}")