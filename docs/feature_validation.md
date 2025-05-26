# ✔️ Feature Validation Guide

## Overview

This guide explains how to validate that PBT features are working correctly. Each feature includes validation steps, expected outputs, and troubleshooting tips.

## Core Features Validation

### 1. Prompt Versioning

**Feature**: Git-compatible prompt versioning

**Validation Steps:**
```bash
# 1. Initialize a project
pbt init version-test
cd version-test

# 2. Create a prompt
cat > prompts/test.prompt.yaml << EOF
name: version-test
version: 1.0.0
template: "Hello {{ name }}"
variables:
  name:
    type: string
EOF

# 3. Create initial commit
git add .
git commit -m "Initial prompt"

# 4. Modify prompt
sed -i '' 's/Hello/Hi/g' prompts/test.prompt.yaml

# 5. View diff
pbt compare prompts/test.prompt.yaml --with-git HEAD

# 6. Create snapshot
pbt snapshot create --tag v1.0.0
```

**Expected Output:**
```
✅ Project initialized
✅ Git diff showing "Hello" → "Hi" change
✅ Snapshot created with tag v1.0.0
```

**Validation Criteria:**
- [ ] Project creates .git directory
- [ ] Diff shows changes correctly
- [ ] Snapshots are tagged in git
- [ ] Can rollback to previous versions

### 2. Prompt Testing

**Feature**: Comprehensive testing framework

**Validation Steps:**
```bash
# 1. Generate test prompt
pbt generate --goal "Classify sentiment as positive, negative, or neutral"

# 2. Create test cases
cat > tests/sentiment.test.yaml << EOF
name: sentiment-tests
prompt_file: prompts/sentiment-classifier.prompt.yaml
tests:
  - name: positive_test
    inputs:
      text: "I love this product!"
    expected: "positive"
  - name: negative_test
    inputs:
      text: "This is terrible"
    expected: "negative"
  - name: neutral_test
    inputs:
      text: "It's okay"
    expected: "neutral"
EOF

# 3. Run tests
pbt test tests/sentiment.test.yaml --verbose

# 4. Generate more tests
pbt gentests prompts/sentiment-classifier.prompt.yaml --num 10
```

**Expected Output:**
```
Running sentiment tests...
✅ positive_test: PASSED (0.95 similarity)
✅ negative_test: PASSED (0.98 similarity)
✅ neutral_test: PASSED (0.92 similarity)

Summary: 3/3 tests passed (100%)
Average score: 9.5/10
```

**Validation Criteria:**
- [ ] All test cases execute
- [ ] Similarity scores are calculated
- [ ] Failed tests show clear errors
- [ ] Verbose mode shows actual outputs

### 3. Model Comparison

**Feature**: Cross-model testing and comparison

**Validation Steps:**
```bash
# 1. Create comparison test
pbt render prompts/sentiment-classifier.prompt.yaml \
  --compare gpt-4,gpt-3.5-turbo,claude-3 \
  --variables "text=Great product, highly recommend!"

# 2. Run comparative analysis
pbt compare tests/sentiment.test.yaml \
  --models gpt-4,claude-3 \
  --metrics quality,cost,speed
```

**Expected Output:**
```
Model Comparison Results
════════════════════════════════════════════════════════

Input: "Great product, highly recommend!"

┌─────────────────┬────────────┬──────────────┬────────────┐
│ Model           │ Output     │ Confidence   │ Cost       │
├─────────────────┼────────────┼──────────────┼────────────┤
│ gpt-4          │ positive   │ 0.98         │ $0.0003    │
│ gpt-3.5-turbo  │ positive   │ 0.95         │ $0.0001    │
│ claude-3       │ positive   │ 0.97         │ $0.0002    │
└─────────────────┴────────────┴──────────────┴────────────┘

Performance Metrics:
- Quality: claude-3 (9.5) > gpt-4 (9.3) > gpt-3.5-turbo (8.7)
- Speed: gpt-3.5-turbo (0.8s) > claude-3 (1.1s) > gpt-4 (1.3s)
- Cost: gpt-3.5-turbo < claude-3 < gpt-4
```

**Validation Criteria:**
- [ ] All models return responses
- [ ] Comparison table displays correctly
- [ ] Metrics are calculated accurately
- [ ] Cost estimates are shown

### 4. Comprehensive Testing (6 Aspects)

**Feature**: Multi-aspect evaluation system

**Validation Steps:**
```bash
# 1. Create comprehensive test
cat > tests/comprehensive.yaml << EOF
name: comprehensive-eval
evaluation_config:
  aspects:
    - correctness:
        weight: 0.3
    - faithfulness:
        weight: 0.2
    - style_tone:
        weight: 0.15
    - safety:
        weight: 0.15
    - stability:
        weight: 0.1
        runs: 5
    - model_quality:
        weight: 0.1
tests:
  - name: complex_test
    inputs:
      query: "Explain quantum computing"
    expected_qualities:
      technical_accuracy: high
      clarity: high
      appropriate_level: beginner
EOF

# 2. Run comprehensive test
pbt testcomp prompts/explainer.prompt.yaml tests/comprehensive.yaml
```

**Expected Output:**
```
🧪 Comprehensive Evaluation Results
═══════════════════════════════════

Running 6-aspect evaluation...

📊 Aspect Scores:
├─ ✅ Correctness:    8.5/10 (Weight: 30%)
├─ ✅ Faithfulness:   9.0/10 (Weight: 20%)
├─ ✅ Style/Tone:     8.0/10 (Weight: 15%)
├─ ✅ Safety:         9.5/10 (Weight: 15%)
├─ ✅ Stability:      8.5/10 (Weight: 10%)
└─ ✅ Model Quality:  8.8/10 (Weight: 10%)

🎯 OVERALL SCORE: 8.6/10 (B+)
✅ PRODUCTION READY

📈 Detailed Analysis:
- Correctness: High accuracy with minor improvements needed
- Faithfulness: Excellent adherence to instructions
- Style: Clear but could be more engaging
- Safety: No concerning content detected
- Stability: Consistent across 5 runs (σ=0.3)
- Model Quality: Performs well across providers
```

**Validation Criteria:**
- [ ] All 6 aspects are evaluated
- [ ] Weighted scoring works correctly
- [ ] Multiple runs for stability
- [ ] Detailed feedback provided

### 5. Prompt Optimization

**Feature**: Automated prompt optimization

**Validation Steps:**
```bash
# 1. Create verbose prompt
cat > prompts/verbose.prompt.yaml << EOF
name: verbose-example
template: |
  You are an AI assistant. Your role is to help users.
  Please be helpful and provide good answers.
  When answering, make sure to be clear and concise.
  Always be polite and professional.
  
  User query: {{ query }}
  
  Please provide a helpful response.
EOF

# 2. Analyze prompt
pbt optimize prompts/verbose.prompt.yaml --analyze

# 3. Optimize for cost
pbt optimize prompts/verbose.prompt.yaml \
  --strategy cost_reduce \
  --output prompts/optimized.prompt.yaml

# 4. Compare versions
pbt compare prompts/verbose.prompt.yaml prompts/optimized.prompt.yaml
```

**Expected Output:**
```
📊 Optimization Analysis
═══════════════════════

Original prompt:
- Token count: 67
- Estimated cost: $0.00012 per call
- Redundancy score: High
- Clarity score: Medium

Optimization recommendations:
✓ Remove redundant instructions
✓ Combine similar directives
✓ Shorten without losing meaning

Applying cost_reduce strategy...

✅ Optimization Complete
- Token reduction: 58% (67 → 28 tokens)
- Cost savings: $0.00007 per call
- Maintained functionality: Yes
- Quality preserved: 95%

Optimized prompt saved to: prompts/optimized.prompt.yaml
```

**Validation Criteria:**
- [ ] Token count is reduced
- [ ] Functionality is preserved
- [ ] Cost estimates are accurate
- [ ] Comparison shows differences

### 6. Multi-Agent Chains

**Feature**: Complex workflow orchestration

**Validation Steps:**
```bash
# 1. Create chain definition
cat > chains/support-flow.yaml << EOF
name: customer-support-chain
agents:
  - name: classifier
    prompt_file: prompts/classifier.prompt.yaml
    outputs: [category, urgency]
    
  - name: responder
    prompt_file: prompts/responder.prompt.yaml
    inputs:
      category: string
      urgency: number
      
flow:
  - from: classifier
    to: responder
    condition: urgency > 3
EOF

# 2. Test chain
pbt chain test chains/support-flow.yaml \
  --input "message=My order hasn't arrived and I need it urgently!"

# 3. Execute chain
pbt chain execute chains/support-flow.yaml \
  --inputs '{"message": "Where is my refund?"}'
```

**Expected Output:**
```
🔗 Chain Execution: customer-support-chain
═════════════════════════════════════════

Input: {"message": "Where is my refund?"}

Step 1: classifier
├─ Input: {"message": "Where is my refund?"}
├─ Output: {"category": "billing", "urgency": 4}
└─ Duration: 1.2s

Step 2: responder (triggered: urgency > 3)
├─ Input: {"category": "billing", "urgency": 4}
├─ Output: "I understand your concern about the refund..."
└─ Duration: 1.5s

✅ Chain completed successfully
Total duration: 2.7s
Tokens used: 156
```

**Validation Criteria:**
- [ ] Chain executes all steps
- [ ] Conditional logic works
- [ ] Data flows between agents
- [ ] Execution time is tracked

### 7. Deployment

**Feature**: Cloud deployment pipeline

**Validation Steps:**
```bash
# 1. Check deployment readiness
pbt ready prompts/sentiment-classifier.prompt.yaml \
  tests/sentiment.test.yaml --threshold 0.9

# 2. Configure deployment
cat > deployment.yaml << EOF
provider: supabase
environment: staging
config:
  project_url: ${SUPABASE_URL}
  service_key: ${SUPABASE_KEY}
  
prompts:
  - sentiment-classifier
  - customer-responder
EOF

# 3. Deploy to staging
pbt deploy --config deployment.yaml --dry-run
pbt deploy --config deployment.yaml

# 4. Verify deployment
pbt deploy status --env staging
```

**Expected Output:**
```
🚀 Deployment Pipeline
════════════════════

Checking readiness...
✅ All tests passing (score: 9.5/10)
✅ Performance benchmarks met
✅ No security issues detected

Deploying to Supabase (staging)...
📦 Packaging prompts...
📤 Uploading to cloud...
🔧 Configuring endpoints...
✅ Health check passed

Deployment Summary:
- Environment: staging
- Prompts deployed: 2
- Endpoints created:
  • https://api.project.supabase.co/prompts/sentiment-classifier
  • https://api.project.supabase.co/prompts/customer-responder
- Status: Active
```

**Validation Criteria:**
- [ ] Readiness checks pass
- [ ] Dry run shows plan
- [ ] Actual deployment succeeds
- [ ] Endpoints are accessible

## Advanced Features Validation

### 8. Internationalization (i18n)

**Validation Steps:**
```bash
# 1. Add languages to prompt
pbt i18n prompts/greeting.prompt.yaml \
  --languages es,fr,ja,ar \
  --auto-translate

# 2. Test different languages
pbt render prompts/greeting.prompt.yaml \
  --language es \
  --variables "name=Maria"
```

**Expected Output:**
```
Adding languages to greeting.prompt.yaml...
✅ Spanish (es) - Auto-translated
✅ French (fr) - Auto-translated
✅ Japanese (ja) - Auto-translated
✅ Arabic (ar) - Auto-translated

Testing Spanish version:
"¡Hola Maria! ¿Cómo estás hoy?"
```

### 9. RAG-Optimized Chunking

**Validation Steps:**
```bash
# 1. Chunk a document
pbt chunk documents/manual.pdf \
  --strategy prompt_aware \
  --max-tokens 500 \
  --overlap 50 \
  --output chunks/

# 2. Verify chunks
ls -la chunks/
pbt chunk verify chunks/
```

**Expected Output:**
```
📄 Document Chunking
════════════════════

Processing: documents/manual.pdf
Strategy: prompt_aware
Document size: 15,234 tokens

Creating chunks...
✅ Created 35 chunks
✅ Average size: 435 tokens
✅ Overlap maintained: 50 tokens
✅ Context preserved in all chunks

Chunks saved to: chunks/
- chunk_001.txt (478 tokens)
- chunk_002.txt (492 tokens)
...
```

### 10. Performance Monitoring

**Validation Steps:**
```bash
# 1. Start monitoring
pbt web --port 8000 &

# 2. Run load test
pbt test tests/*.yaml --parallel --monitor

# 3. View dashboard
open http://localhost:8000/metrics
```

**Expected Output:**
- Dashboard shows real-time metrics
- Request latency graphs
- Token usage tracking
- Cost accumulation
- Error rate monitoring

## Validation Checklist

### Quick Validation Script

```bash
#!/bin/bash
# save as validate_pbt.sh

echo "🔍 PBT Feature Validation"
echo "========================"

# Check installation
echo -n "✓ Installation: "
pbt --version >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

# Check API keys
echo -n "✓ API Keys: "
pbt validate-keys >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

# Test basic operations
echo -n "✓ Project Init: "
pbt init test-project >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "✓ Prompt Generation: "
cd test-project
pbt generate --goal "Test prompt" >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "✓ Testing: "
pbt test prompts/*.yaml >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

echo -n "✓ Optimization: "
pbt optimize prompts/*.yaml --check >/dev/null 2>&1 && echo "PASS" || echo "FAIL"

# Cleanup
cd ..
rm -rf test-project

echo "========================"
echo "Validation complete!"
```

### Manual Validation Checklist

- [ ] **Installation**
  - [ ] `pbt --version` shows correct version
  - [ ] `pbt --help` displays all commands
  - [ ] Tab completion works

- [ ] **Project Management**
  - [ ] Can create new projects
  - [ ] Git integration works
  - [ ] Profile switching works

- [ ] **Prompt Operations**
  - [ ] Generate prompts with AI
  - [ ] Render with variables
  - [ ] Convert Python code

- [ ] **Testing**
  - [ ] Basic tests pass
  - [ ] Comprehensive evaluation works
  - [ ] Model comparison functions

- [ ] **Optimization**
  - [ ] Token reduction works
  - [ ] Quality is preserved
  - [ ] Multiple strategies available

- [ ] **Advanced Features**
  - [ ] Chains execute properly
  - [ ] i18n adds languages
  - [ ] Chunking preserves context

- [ ] **Deployment**
  - [ ] Can deploy to cloud
  - [ ] Health checks pass
  - [ ] Rollback works

## Troubleshooting Validation Failures

### Common Issues

1. **API Key Issues**
   ```bash
   # Verify keys are set
   env | grep API_KEY
   
   # Test keys directly
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
   ```

2. **Import Errors**
   ```bash
   # Reinstall with all dependencies
   pip install --force-reinstall prompt-build-tool[all]
   ```

3. **Permission Errors**
   ```bash
   # Check file permissions
   ls -la ~/.pbt/
   chmod -R 755 ~/.pbt/
   ```

### Getting Help

If validation fails:
1. Run `pbt doctor --verbose`
2. Check logs in `~/.pbt/logs/`
3. Report issues with validation output

## Summary

Complete validation ensures:
- ✅ All core features work
- ✅ Integrations are functional
- ✅ Performance meets expectations
- ✅ Error handling is robust
- ✅ Documentation matches reality