# Comprehensive Multi-Aspect Testing in PBT

PBT now supports comprehensive testing that evaluates prompts across multiple dimensions, similar to professional prompt engineering workflows.

## Overview

The `pbt testcomp` command runs multi-aspect evaluations on your prompts:

- **Correctness**: Is the output accurate and sensible?
- **Faithfulness**: Does it preserve the original meaning?
- **Style/Tone**: Is it appropriately concise or verbose?
- **Safety**: Does it avoid harmful or inappropriate content?
- **Stability**: Are outputs consistent across multiple runs?
- **Model Quality**: How do different models compare?

## Quick Start

```bash
# Run comprehensive tests
pbt testcomp summarizer.prompt.yaml tests/comprehensive.yaml

# Test specific aspects only
pbt testcomp prompt.yaml tests.yaml --aspects correctness,safety

# Compare models
pbt testcomp prompt.yaml tests.yaml --model gpt-4
```

## Test File Format

### YAML Format

```yaml
# comprehensive_test.yaml
prompt_file: summarizer.prompt.yaml

# Configuration
evaluation_config:
  min_scores:
    correctness: 7.0
    faithfulness: 8.0
    style_tone: 6.0
    safety: 9.0
    stability: 7.0

# Test cases
tests:
  - name: cat_curiosity_test
    inputs:
      text: "Cats are curious creatures who like to explore."
    expected: "Cats like to explore and are curious."
    style_expectation: concise
    evaluate:
      correctness: true
      faithfulness: true
      style_tone: true
      safety: true
      
  - name: stability_check
    inputs:
      text: "Test input for consistency"
    stability_runs: 5  # Run 5 times to check consistency
    evaluate:
      stability: true
      
  - name: model_comparison
    inputs:
      text: "Compare model outputs"
    compare_models:
      - gpt-4
      - claude
      - gpt-3.5-turbo
    evaluate:
      model_quality: true
```

### JSONL Format

```jsonl
{"name": "test1", "inputs": {"text": "Input text"}, "expected": "Expected output", "evaluate": {"correctness": true, "faithfulness": true}}
{"name": "test2", "inputs": {"text": "Another input"}, "style_expectation": "verbose", "evaluate": {"style_tone": true, "safety": true}}
{"name": "test3", "inputs": {"text": "Stability test"}, "stability_runs": 5, "evaluate": {"stability": true}}
```

## Evaluation Aspects

### Correctness
- Checks if the output is factually accurate
- Verifies logical consistency
- Ensures relevance to input
- Default minimum score: 7.0/10

### Faithfulness  
- Ensures no hallucinated information
- Preserves key facts and concepts
- Maintains semantic meaning
- Default minimum score: 8.0/10

### Style/Tone
- Evaluates if output matches expected style (concise/verbose)
- Checks clarity and readability
- Assesses professional tone
- Default minimum score: 6.0/10

### Safety
- Scans for harmful or inappropriate content
- Checks for personal information exposure
- Identifies potentially dangerous instructions
- Default minimum score: 9.0/10

### Stability
- Runs prompt multiple times
- Measures consistency of outputs
- Calculates variation metrics
- Default minimum score: 7.0/10

### Model Quality
- Compares outputs across different models
- Ranks models by quality scores
- Identifies best performing model
- Default minimum score: 7.0/10

## Command Options

```bash
pbt testcomp [OPTIONS] PROMPT_FILE TEST_FILE

Options:
  --model TEXT              Model to test with [default: gpt-4]
  --aspects TEXT            Comma-separated aspects to evaluate
  --format TEXT             Output format: table, json, markdown [default: table]
  --save/--no-save         Save detailed report [default: save]
  --help                   Show this message and exit
```

## Output Formats

### Table Format (Default)
Shows a visual table with scores for each aspect:

```
📊 Comprehensive Test Results:
Total Tests: 5
Passed: 4
Failed: 1
Pass Rate: 80.0%

📈 Aspect Analysis:
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━┳━━━━━┳━━━━━━━━━━┓
┃ Aspect        ┃ Avg Score ┃ Min ┃ Max ┃ Pass Rate┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━╇━━━━━╇━━━━━━━━━━┩
│ Correctness   │    8.5    │ 7.0 │ 9.5 │   100%   │
│ Faithfulness  │    8.2    │ 7.5 │ 9.0 │   100%   │
│ Style Tone    │    7.8    │ 6.5 │ 9.0 │    80%   │
│ Safety        │    9.5    │ 9.0 │ 10  │   100%   │
│ Stability     │    8.0    │ 7.0 │ 9.0 │   100%   │
└───────────────┴───────────┴─────┴─────┴──────────┘
```

### JSON Format
```bash
pbt testcomp prompt.yaml tests.yaml --format json
```

Outputs detailed JSON with all scores and metadata.

### Markdown Format
```bash
pbt testcomp prompt.yaml tests.yaml --format markdown
```

Generates a markdown report suitable for documentation.

## Example Workflow

1. **Create your prompt file** (`summarizer.prompt.yaml`):
```yaml
name: summarizer
model: gpt-4
inputs:
  text: string
template: |
  Summarize this clearly:
  "{{ text }}"
```

2. **Create comprehensive tests** (`tests/comprehensive.yaml`):
```yaml
tests:
  - name: basic_test
    inputs:
      text: "Long text to summarize..."
    expected: "Short summary"
    evaluate:
      correctness: true
      faithfulness: true
      style_tone: true
      safety: true
```

3. **Run comprehensive testing**:
```bash
pbt testcomp summarizer.prompt.yaml tests/comprehensive.yaml
```

4. **Review results**:
- Check aspect scores
- Review failed tests
- Compare model performance
- Analyze stability metrics

## Integration with CI/CD

```yaml
# .github/workflows/test.yml
name: Prompt Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install PBT
        run: pip install prompt-build-tool
        
      - name: Run comprehensive tests
        run: |
          pbt testcomp prompts/*.yaml tests/*.yaml \
            --format json \
            --save
            
      - name: Upload test reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: evaluations/
```

## Best Practices

1. **Test all aspects** for production prompts
2. **Set appropriate thresholds** based on use case
3. **Run stability tests** for critical prompts
4. **Compare models** before deployment
5. **Monitor safety scores** carefully
6. **Save reports** for compliance and auditing

## Troubleshooting

### Low Correctness Scores
- Review expected outputs
- Check if prompt template is clear
- Verify input formatting

### Failed Safety Checks
- Review output for sensitive content
- Check for unintended harmful patterns
- Adjust prompt to be more restrictive

### Poor Stability
- Increase temperature settings
- Add more specific instructions
- Consider using different models

### Model Quality Variations
- Test with consistent inputs
- Compare token usage
- Evaluate cost vs quality tradeoffs