# 🧪 Test Examples - Comprehensive Testing Guide

## Overview

This guide provides practical examples of all testing procedures in PBT, from basic unit tests to comprehensive multi-aspect evaluations.

## Table of Contents
1. [Basic Testing](#basic-testing)
2. [Comprehensive Testing](#comprehensive-testing)
3. [JSONL Testing](#jsonl-testing)
4. [Regression Testing](#regression-testing)
5. [Chain Testing](#chain-testing)
6. [Performance Testing](#performance-testing)
7. [Integration Testing](#integration-testing)

## Basic Testing

### 1. Simple Test Case

```yaml
# summarizer.test.yaml
name: summarizer-tests
prompt_file: summarizer.prompt.yaml
tests:
  - name: basic_summary
    inputs:
      text: "The quick brown fox jumps over the lazy dog. This is a test sentence."
    expected_output: "A fox jumps over a dog."
    
  - name: empty_input
    inputs:
      text: ""
    expected_output: "No content to summarize."
    
  - name: long_text
    inputs:
      text: |
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    expected_pattern: "Lorem ipsum.*summary"
```

**Run the test:**
```bash
pbt test summarizer.test.yaml

# Output:
✅ Test: basic_summary - PASSED
✅ Test: empty_input - PASSED  
✅ Test: long_text - PASSED
Summary: 3/3 tests passed (100%)
```

### 2. Testing with Multiple Models

```yaml
# multi_model.test.yaml
name: cross-model-test
prompt_file: classifier.prompt.yaml
models:
  - gpt-4
  - claude-3
  - gpt-3.5-turbo
tests:
  - name: sentiment_classification
    inputs:
      text: "I love this product!"
    expected_output: "positive"
    tolerance: 0.9  # 90% similarity required
```

**Run cross-model test:**
```bash
pbt test multi_model.test.yaml --compare

# Output:
Model Comparison Results:
┌─────────────────┬──────────┬───────────┬─────────┐
│ Test            │ GPT-4    │ Claude-3  │ GPT-3.5 │
├─────────────────┼──────────┼───────────┼─────────┤
│ sentiment_class │ ✅ PASS  │ ✅ PASS   │ ✅ PASS │
└─────────────────┴──────────┴───────────┴─────────┘
```

## Comprehensive Testing

### 1. Six-Aspect Evaluation

```yaml
# comprehensive.test.yaml
name: comprehensive-evaluation
prompt_file: customer_service.prompt.yaml
evaluation_config:
  aspects:
    - correctness:
        weight: 0.3
        evaluator: gpt-4
    - faithfulness:
        weight: 0.2
        evaluator: claude-3
    - style_tone:
        weight: 0.15
        target: "professional, empathetic"
    - safety:
        weight: 0.15
        check_toxicity: true
    - stability:
        weight: 0.1
        runs: 5
    - model_quality:
        weight: 0.1
        compare_models: [gpt-4, claude-3]

tests:
  - name: angry_customer
    inputs:
      message: "Your service is terrible! I want a refund NOW!"
      customer_history: "Long-time customer, first complaint"
    expected_qualities:
      empathy_score: ">0.8"
      resolution_offered: true
      escalation_needed: false
```

**Run comprehensive test:**
```bash
pbt testcomp customer_service.prompt.yaml comprehensive.test.yaml

# Output:
🧪 Comprehensive Evaluation Results
═══════════════════════════════════

📊 Aspect Scores:
├─ ✅ Correctness:    8.5/10 (Weight: 30%)
├─ ✅ Faithfulness:   9.0/10 (Weight: 20%)
├─ ✅ Style/Tone:     7.5/10 (Weight: 15%)
├─ ✅ Safety:         9.5/10 (Weight: 15%)
├─ ✅ Stability:      8.0/10 (Weight: 10%)
└─ ✅ Model Quality:  8.5/10 (Weight: 10%)

🎯 OVERALL SCORE: 8.4/10 (B+)
✅ PRODUCTION READY

💡 Recommendations:
- Improve tone consistency for better style scores
- Add more examples to increase stability
```

### 2. Custom Evaluation Criteria

```yaml
# custom_eval.test.yaml
name: domain-specific-evaluation
prompt_file: medical_advisor.prompt.yaml
custom_evaluators:
  - medical_accuracy:
      evaluator_prompt: |
        Evaluate if the medical advice is accurate and safe.
        Score from 0-10 based on:
        - Factual correctness
        - Appropriate disclaimers
        - No harmful advice
      model: gpt-4
      
  - readability:
      evaluator_prompt: |
        Score the readability for a general audience.
        Consider:
        - Simple language
        - Clear explanations
        - Avoiding jargon
      model: claude-3

tests:
  - name: headache_advice
    inputs:
      symptoms: "Persistent headache for 3 days"
    evaluate:
      medical_accuracy: ">8"
      readability: ">7"
      includes_disclaimer: true
```

## JSONL Testing

### 1. Bulk Test Cases

```jsonl
# test_cases.jsonl
{"test_name": "positive_sentiment", "inputs": {"text": "Amazing product!"}, "expected": "positive", "tags": ["sentiment"]}
{"test_name": "negative_sentiment", "inputs": {"text": "Terrible experience"}, "expected": "negative", "tags": ["sentiment"]}
{"test_name": "neutral_sentiment", "inputs": {"text": "It's okay"}, "expected": "neutral", "tags": ["sentiment"]}
{"test_name": "mixed_sentiment", "inputs": {"text": "Good quality but expensive"}, "expected": "mixed", "tags": ["sentiment", "edge_case"]}
```

**Run JSONL tests:**
```bash
pbt testjsonl sentiment_analyzer.prompt.yaml test_cases.jsonl

# Output:
Processing JSONL tests...
[████████████████████] 100% 4/4 tests

Results by Tag:
- sentiment: 4/4 passed (100%)
- edge_case: 1/1 passed (100%)

Detailed Results:
✅ positive_sentiment: PASSED (0.95 similarity)
✅ negative_sentiment: PASSED (0.98 similarity)
✅ neutral_sentiment: PASSED (0.91 similarity)
✅ mixed_sentiment: PASSED (0.89 similarity)
```

### 2. Parameterized Testing

```jsonl
# parameterized_tests.jsonl
{"test_name": "length_10", "inputs": {"text": "a" * 10, "max_length": 5}, "expected_length": 5}
{"test_name": "length_100", "inputs": {"text": "b" * 100, "max_length": 50}, "expected_length": 50}
{"test_name": "length_1000", "inputs": {"text": "c" * 1000, "max_length": 200}, "expected_length": 200}
```

## Regression Testing

### 1. Version Comparison

```yaml
# regression_test.yaml
name: version-regression
baseline_prompt: v1.0/summarizer.prompt.yaml
new_prompt: v1.1/summarizer.prompt.yaml
test_suite: regression_suite.jsonl
regression_config:
  tolerance: 0.05  # Allow 5% deviation
  metrics:
    - quality_score
    - token_count
    - execution_time
  fail_on_regression: true
```

**Run regression test:**
```bash
pbt regression v1.1/summarizer.prompt.yaml v1.0/summarizer.prompt.yaml regression_suite.jsonl

# Output:
🔄 Regression Test Results
════════════════════════════

Baseline: v1.0/summarizer.prompt.yaml
New Version: v1.1/summarizer.prompt.yaml

📊 Metrics Comparison:
┌──────────────────┬──────────┬──────────┬─────────┐
│ Metric           │ Baseline │ New      │ Change  │
├──────────────────┼──────────┼──────────┼─────────┤
│ Quality Score    │ 8.5      │ 8.7      │ +2.4% ✅│
│ Token Count      │ 245      │ 198      │ -19.2% ✅│
│ Execution Time   │ 1.2s     │ 1.1s     │ -8.3% ✅│
└──────────────────┴──────────┴──────────┴─────────┘

✅ NO REGRESSIONS DETECTED
```

### 2. A/B Testing

```yaml
# ab_test.yaml
name: prompt-ab-test
variants:
  - name: variant_a
    prompt_file: prompts/variant_a.yaml
  - name: variant_b
    prompt_file: prompts/variant_b.yaml
test_config:
  sample_size: 100
  metrics:
    - user_satisfaction
    - completion_rate
    - response_time
  statistical_significance: 0.95
```

## Chain Testing

### 1. Multi-Agent Chain Test

```yaml
# chain_test.yaml
name: customer-service-chain-test
chain_file: chains/customer_service.yaml
test_scenarios:
  - name: simple_inquiry
    initial_input:
      message: "What are your business hours?"
    expected_flow:
      - agent: classifier
        output: {intent: "info_request", urgency: 1}
      - agent: info_responder
        output_contains: "business hours"
        
  - name: escalation_path
    initial_input:
      message: "I need to speak to a manager immediately!"
    expected_flow:
      - agent: classifier
        output: {intent: "escalation", urgency: 5}
      - agent: escalation_handler
        output_contains: "manager"
```

**Run chain test:**
```bash
pbt chain test chain_test.yaml

# Output:
🔗 Chain Test Results
═════════════════════

Test: simple_inquiry
└─ ✅ classifier -> {intent: "info_request", urgency: 1}
└─ ✅ info_responder -> Contains "business hours"

Test: escalation_path  
└─ ✅ classifier -> {intent: "escalation", urgency: 5}
└─ ✅ escalation_handler -> Contains "manager"

Chain Performance:
- Average latency: 2.3s
- Success rate: 100%
- Resource usage: Normal
```

### 2. Conditional Flow Testing

```yaml
# conditional_chain_test.yaml
name: conditional-flow-test
chain_file: chains/decision_tree.yaml
test_cases:
  - name: path_a_test
    input: {score: 85}
    expected_path: ["scorer", "high_performer", "reward_calculator"]
    
  - name: path_b_test
    input: {score: 45}
    expected_path: ["scorer", "low_performer", "improvement_plan"]
```

## Performance Testing

### 1. Load Testing

```yaml
# load_test.yaml
name: performance-test
prompt_file: api_endpoint.prompt.yaml
load_test_config:
  concurrent_users: 50
  duration: 300  # 5 minutes
  ramp_up: 30   # 30 seconds
  scenarios:
    - name: standard_load
      weight: 70
      inputs_file: standard_inputs.jsonl
    - name: edge_cases
      weight: 20
      inputs_file: edge_cases.jsonl
    - name: stress_test
      weight: 10
      inputs_file: large_inputs.jsonl
```

**Run load test:**
```bash
pbt test load_test.yaml --type performance

# Output:
🚀 Performance Test Results
═══════════════════════════

Test Duration: 5m 0s
Total Requests: 15,000

📊 Response Times:
- P50: 245ms
- P90: 512ms
- P95: 734ms
- P99: 1,205ms

✅ Success Rate: 99.8%
❌ Error Rate: 0.2%

📈 Throughput:
- Average: 50 req/s
- Peak: 73 req/s

⚠️ Warnings:
- Token rate limit reached 3 times
- Memory usage peaked at 78%
```

### 2. Optimization Testing

```yaml
# optimization_test.yaml
name: optimization-validation
original_prompt: verbose_prompt.yaml
optimized_prompt: optimized_prompt.yaml
test_metrics:
  - token_reduction:
      target: ">30%"
  - quality_preservation:
      minimum: 0.95  # 95% quality retained
  - cost_reduction:
      calculate: true
```

## Integration Testing

### 1. End-to-End Test

```yaml
# e2e_test.yaml
name: full-pipeline-test
workflow:
  - step: generate_prompt
    command: pbt generate --goal "Customer classifier"
    verify:
      - file_exists: customer_classifier.prompt.yaml
      
  - step: create_tests
    command: pbt gentests customer_classifier.prompt.yaml
    verify:
      - file_exists: tests/customer_classifier.test.yaml
      
  - step: run_tests
    command: pbt test tests/customer_classifier.test.yaml
    expect_success: true
    
  - step: optimize
    command: pbt optimize customer_classifier.prompt.yaml
    verify:
      - token_reduction: ">20%"
      
  - step: deploy
    command: pbt deploy --provider supabase --env staging
    verify:
      - deployment_status: "success"
```

### 2. API Integration Test

```python
# test_api_integration.py
import pytest
from pbt import PromptRunner

def test_prompt_api():
    """Test prompt execution via API"""
    runner = PromptRunner("calculator.prompt.yaml")
    
    # Test basic calculation
    result = runner.run({
        "expression": "2 + 2"
    })
    assert "4" in result.output
    
    # Test error handling
    with pytest.raises(ValueError):
        runner.run({"expression": None})
    
    # Test model switching
    result_gpt4 = runner.run(
        {"expression": "Complex calculation"},
        model="gpt-4"
    )
    result_claude = runner.run(
        {"expression": "Complex calculation"},
        model="claude-3"
    )
    assert result_gpt4.model == "gpt-4"
    assert result_claude.model == "claude-3"
```

## Best Practices

### 1. Test Organization
```
tests/
├── unit/               # Individual prompt tests
├── integration/        # Multi-component tests
├── regression/         # Version comparison
├── performance/        # Load and stress tests
├── fixtures/          # Test data
└── helpers/           # Test utilities
```

### 2. Test Configuration
```yaml
# pbt.yaml test configuration
testing:
  default_timeout: 30
  parallel_execution: true
  max_workers: 5
  retry_failed: 2
  
  coverage:
    minimum: 80
    fail_under: true
    
  reporting:
    format: "html"
    output_dir: "test_reports/"
```

### 3. Continuous Testing
```yaml
# .github/workflows/test.yml
name: PBT Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install PBT
        run: pip install prompt-build-tool
      - name: Run Tests
        run: |
          pbt test tests/ --coverage
          pbt testcomp comprehensive.yaml
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_reports/
```

## Troubleshooting Tests

### Common Issues

1. **Flaky Tests**
   ```yaml
   # Add stability configuration
   test_config:
     retry_on_failure: 3
     stability_threshold: 0.9
   ```

2. **Token Limits**
   ```yaml
   # Configure chunking
   test_config:
     chunk_large_inputs: true
     max_tokens_per_test: 2000
   ```

3. **Rate Limiting**
   ```yaml
   # Add delays
   test_config:
     delay_between_tests: 1.0
     respect_rate_limits: true
   ```

## Summary

PBT provides comprehensive testing capabilities from simple unit tests to complex multi-aspect evaluations. Use these examples as templates for your own testing needs.