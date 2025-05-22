import openai

def bad_agent(content):
    prompt = f"Test prompt with {content}"
    # This will have intentional syntax errors after conversion
    response = openai.ChatCompletion.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"].strip()