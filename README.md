# PBT - Prompt Build Tool

A simple tool for converting Python agent code to YAML-based prompt templates.

## Installation

```bash
pip install -e .
```

## Usage

Convert your Python agent code to use YAML-based prompts:

```bash
# Convert a single file
pbt convert my_agent.py

# Convert multiple files
pbt convert . --batch --pattern "*agent*.py"

# Specify output directory
pbt convert my_agent.py --output prompts/
```

## How it works

PBT automatically:
1. Extracts prompts from your Python agent functions
2. Creates YAML files with the prompt templates
3. Generates converted Python code that loads prompts from YAML

### Example

Original code:
```python
def summarizer_agent(content):
    prompt = f"Summarize this content:\n\n{content}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
```

After conversion:
```python
from pbt.runtime import PromptRunner

summarizer_runner = PromptRunner("agents/summarizer.prompt.yaml")

def summarizer_agent(content):
    """Run summarizer prompt via PBT"""
    return summarizer_runner.run({"content": content})
```

YAML file (`agents/summarizer.prompt.yaml`):
```yaml
name: Summarizer
version: '1.0'
model: gpt-4
template: |
  Summarize this content:
  
  {{ content }}
```

## Benefits

- **Version Control**: Track prompt changes in Git
- **Separation of Concerns**: Keep prompts separate from code
- **Easy Updates**: Modify prompts without changing code
- **Consistency**: Use the same prompt format across projects