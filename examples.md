# PBT Command Examples

This guide provides comprehensive examples for all PBT (Prompt Build Tool) commands.

## Table of Contents

1. [Project Management](#project-management)
2. [Prompt Generation](#prompt-generation)
3. [Testing Commands](#testing-commands)
4. [Conversion Commands](#conversion-commands)
5. [Comparison & Analysis](#comparison--analysis)
6. [Optimization](#optimization)
7. [Multi-Agent Chains](#multi-agent-chains)
8. [Chunking & RAG](#chunking--rag)
9. [Deployment & Publishing](#deployment--publishing)
10. [Utility Commands](#utility-commands)

---

## Project Management

### `pbt init` - Initialize a new project

```bash
# Basic initialization
pbt init

# Initialize with project name
pbt init --name my-ai-prompts

# Initialize in specific directory
pbt init --directory ./projects/new-prompts --name customer-service

# Initialize with template
pbt init --template chatbot
```

**Creates structure:**
```
my-ai-prompts/
├── prompts/
├── tests/
├── evaluations/
├── pbt.yaml
└── .env.example
```

---

## Prompt Generation

### `pbt generate` - AI-powered prompt generation

```bash
# Basic generation
pbt generate --goal "Summarize customer feedback into actionable insights"
```

**Input:**
```bash
pbt generate --goal "Summarize customer feedback into actionable insights"
```

**Output:**
```
🤖 Generating prompt for: Summarize customer feedback into actionable insights
✅ Generation complete!

✅ Generated prompt saved to: customer-feedback-summarizer.prompt.yaml
✅ Generated 6 test cases: tests/customer-feedback-summarizer.test.jsonl

Preview:
┌──────────────── Generated Prompt ───────────────┐
│  1 │ name: Customer-Feedback-Summarizer         │
│  2 │ version: 1.0                                │
│  3 │ model: claude                               │
│  4 │ template: |                                 │
│  5 │   Analyze the following customer feedback   │
│  6 │   and provide actionable insights:          │
│  7 │                                             │
│  8 │   Feedback: {{ feedback_text }}             │
│  9 │                                             │
│ 10 │   Please provide:                           │
│ 11 │   1. Key themes (3-5 bullet points)        │
│ 12 │   2. Sentiment analysis                     │
│ 13 │   3. Recommended actions                    │
│ 14 │                                             │
│ 15 │ variables:                                  │
│ 16 │   feedback_text:                            │
│ 17 │     type: string                            │
│ 18 │     description: Raw customer feedback      │
└─────────────────────────────────────────────────┘
```

```bash
# Specify model and style
pbt generate --goal "Extract key points from meetings" --model gpt-4 --style concise
```

**Input:**
```bash
pbt generate --goal "Extract key points from meetings" --model gpt-4 --style concise
```

**Output:**
```
🤖 Generating prompt for: Extract key points from meetings
✅ Generation complete!

✅ Generated prompt saved to: meeting-key-points-extractor.prompt.yaml
✅ Generated 6 test cases: tests/meeting-key-points-extractor.test.jsonl
```

```bash
# With custom variables
pbt generate --goal "Translate text between languages" --variables "source_text,target_language,tone"
```

**Input:**
```bash
pbt generate --goal "Translate text between languages" --variables "source_text,target_language,tone"
```

**Output:**
```
🤖 Generating prompt for: Translate text between languages
✅ Generation complete!

✅ Generated prompt saved to: text-translator.prompt.yaml
✅ Generated 6 test cases: tests/text-translator.test.jsonl

Preview:
┌──────────────── Generated Prompt ───────────────┐
│  1 │ name: Text-Translator                       │
│  2 │ version: 1.0                                │
│  3 │ model: claude                               │
│  4 │ template: |                                 │
│  5 │   Translate the following text from         │
│  6 │   {{ source_language }} to {{ target_lang  │
│  7 │   uage }} with a {{ tone }} tone:           │
│  8 │                                             │
│  9 │   Text: {{ source_text }}                   │
│ 10 │                                             │
│ 11 │ variables:                                  │
│ 12 │   source_text:                              │
│ 13 │     type: string                            │
│ 14 │   target_language:                          │
│ 15 │     type: string                            │
│ 16 │   tone:                                     │
│ 17 │     type: string                            │
└─────────────────────────────────────────────────┘
```

**Other examples:**

```bash
# Generate without tests
pbt generate --goal "Answer FAQ questions" --no-tests

# Custom output location
pbt generate --goal "Review code quality" --output prompts/code_reviewer.yaml

# Specify number of test cases
pbt generate --goal "Classify support tickets" --num-tests 10
```

### `pbt gentests` - Generate test cases for existing prompts

```bash
# Generate tests for a prompt
pbt gentests agents/summarizer.prompt.yaml

# Custom number of tests
pbt gentests prompts/translator.yaml --num-tests 15

# Specify output file
pbt gentests analyzer.yaml --output tests/custom_analyzer_tests.jsonl

# Overwrite existing tests
pbt gentests classifier.yaml --overwrite
```

---

## Testing Commands

### `pbt test` - Run tests on prompts

```bash
# Run specific test file
pbt test tests/test_summarizer.yaml
```

**Input:**
```bash
pbt test tests/test_summarizer.yaml
```

**Output:**
```
📋 Running test file: tests/test_summarizer.yaml
🧪 Running test cases from: tests/test_summarizer.yaml

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                              Test Results                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Test Case: short_text_summary
Input: {"text": "AI is transforming industries rapidly"}
Expected Keywords: ["AI", "transform", "industries"]
Result: ✅ PASSED
Score: 9.2/10

Test Case: long_text_summary  
Input: {"text": "Machine learning models require large datasets..."}
Expected Keywords: ["machine learning", "datasets", "models"]
Result: ✅ PASSED
Score: 8.7/10

Test Case: technical_content
Input: {"text": "Neural networks use backpropagation for training"}
Expected Keywords: ["neural networks", "backpropagation"] 
Result: ✅ PASSED
Score: 8.9/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 3/3 tests passed (100%)
Average Score: 8.9/10
Saved results to: evaluations/test_summarizer_results.json
```

```bash
# Auto-generate and run tests
pbt test agents/email_writer.prompt.yaml --num-tests 5
```

**Input:**
```bash
pbt test agents/email_writer.prompt.yaml --num-tests 5
```

**Output:**
```
📁 Auto-generating tests for prompt: agents/email_writer.prompt.yaml
🤖 Generating 5 test cases for email_writer prompt...
✅ Generated test cases saved to: tests/email_writer_auto.jsonl

🧪 Running generated test cases...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          Auto-Generated Test Results                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Test 1: formal_business_email
Input: {"recipient": "CEO", "topic": "Q4 Results", "tone": "formal"}
Output Length: 245 words
Quality Score: 9.1/10 ✅

Test 2: casual_team_update  
Input: {"recipient": "team", "topic": "project status", "tone": "casual"}
Output Length: 189 words
Quality Score: 8.6/10 ✅

Test 3: urgent_notification
Input: {"recipient": "stakeholders", "topic": "system outage", "tone": "urgent"}
Output Length: 156 words  
Quality Score: 9.3/10 ✅

Test 4: thank_you_email
Input: {"recipient": "client", "topic": "collaboration", "tone": "grateful"}
Output Length: 203 words
Quality Score: 8.9/10 ✅

Test 5: follow_up_email
Input: {"recipient": "prospect", "topic": "meeting recap", "tone": "professional"}
Output Length: 221 words
Quality Score: 8.7/10 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 5/5 tests passed (100%)
Average Score: 8.9/10
Results saved to: evaluations/email_writer_auto_results.json
```

```bash
# Test with specific model
pbt test prompts/chatbot.yaml --model gpt-4
```

**Input:**
```bash
pbt test prompts/chatbot.yaml --model gpt-4
```

**Output:**
```
📁 Auto-generating tests for prompt: prompts/chatbot.yaml
🤖 Using model: gpt-4 for testing
✅ Generated 5 test cases and running with GPT-4...

Summary: 5/5 tests passed (100%)
Average Score: 9.1/10 (GPT-4)
```

**Other examples:**

```bash
# Test without saving results
pbt test analyzer.yaml --no-save

# Specify test type
pbt test critic.yaml --test-type edge_case --num-tests 10
```

### `pbt testjsonl` - Run JSONL format tests

```bash
# Basic JSONL testing
pbt testjsonl prompts/summarizer.yaml tests/cases.jsonl

# With different model
pbt testjsonl translator.yaml test_data.jsonl --model claude

# Without saving results
pbt testjsonl analyzer.yaml tests.jsonl --no-save
```

**Example JSONL test file:**
```jsonl
{"test_name": "short_text", "inputs": {"text": "AI is transforming industries"}, "expected_keywords": ["AI", "transform", "industries"], "quality_criteria": "Should be concise and clear"}
{"test_name": "long_text", "inputs": {"text": "Machine learning models require large datasets..."}, "expected_keywords": ["machine learning", "datasets"], "quality_criteria": "Should summarize key points"}
```

### `pbt testcomp` - Comprehensive multi-aspect testing

```bash
# Full comprehensive testing
pbt testcomp summarizer.prompt.yaml tests/comprehensive.yaml
```

**Input:**
```bash
pbt testcomp summarizer.prompt.yaml tests/comprehensive.yaml
```

**Output:**
```
🧪 Running comprehensive evaluation on: summarizer.prompt.yaml
📊 Evaluating across 6 aspects: correctness, faithfulness, style_tone, safety, stability, model_quality

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        Comprehensive Test Results                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Test: accuracy_test
Input: {"text": "Climate change affects global weather patterns"}
Expected: "Climate change impacts global weather"

✅ Correctness: 8.5/10   (Captures main ideas accurately)
✅ Faithfulness: 9.0/10  (Stays true to original content)
✅ Style/Tone: 7.5/10    (Concise but could be more engaging)
✅ Safety: 9.5/10        (No harmful content detected)
✅ Stability: 8.0/10     (Consistent across 5 runs)
✅ Model Quality: 8.7/10 (High coherence and relevance)

Test: complex_content_test
Input: {"text": "Machine learning algorithms process data..."}
Expected: "ML algorithms analyze data for patterns"

✅ Correctness: 9.1/10   
✅ Faithfulness: 8.8/10  
✅ Style/Tone: 8.2/10    
✅ Safety: 9.8/10        
✅ Stability: 8.5/10     
✅ Model Quality: 9.0/10 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              OVERALL SCORES                              
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Correctness:    8.8/10 ✅ EXCELLENT
📊 Faithfulness:   8.9/10 ✅ EXCELLENT  
📊 Style/Tone:     7.9/10 ✅ GOOD
📊 Safety:         9.7/10 ✅ EXCELLENT
📊 Stability:      8.3/10 ✅ GOOD
📊 Model Quality:  8.9/10 ✅ EXCELLENT

🎯 OVERALL GRADE: 8.7/10 (PRODUCTION READY)

💡 Recommendations:
   • Consider improving style consistency for better user engagement
   • All safety and correctness metrics exceed production thresholds
   • Stability is good but could benefit from more diverse test cases

📄 Full report saved to: evaluations/comprehensive_test_results.json
```

```bash
# Test specific aspects only
pbt testcomp chatbot.yaml tests.yaml --aspects correctness,safety,stability
```

**Input:**
```bash
pbt testcomp chatbot.yaml tests.yaml --aspects correctness,safety,stability
```

**Output:**
```
🧪 Running targeted evaluation on: chatbot.yaml
📊 Evaluating 3 aspects: correctness, safety, stability

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          Focused Test Results                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Correctness:    9.2/10 ✅ EXCELLENT
✅ Safety:         9.8/10 ✅ EXCELLENT
✅ Stability:      8.6/10 ✅ GOOD

🎯 FOCUSED GRADE: 9.2/10 (PRODUCTION READY)
```

```bash
# JSON output format
pbt testcomp prompt.yaml tests.yaml --format json
```

**Input:**
```bash
pbt testcomp prompt.yaml tests.yaml --format json
```

**Output:**
```json
{
  "test_name": "comprehensive_evaluation",
  "timestamp": "2024-01-15T10:30:00Z",
  "prompt_file": "prompt.yaml",
  "overall_score": 8.7,
  "grade": "PRODUCTION_READY",
  "aspects": {
    "correctness": {"score": 8.8, "status": "EXCELLENT"},
    "faithfulness": {"score": 8.9, "status": "EXCELLENT"},
    "style_tone": {"score": 7.9, "status": "GOOD"},
    "safety": {"score": 9.7, "status": "EXCELLENT"},
    "stability": {"score": 8.3, "status": "GOOD"},
    "model_quality": {"score": 8.9, "status": "EXCELLENT"}
  },
  "recommendations": [
    "Consider improving style consistency for better user engagement",
    "All safety and correctness metrics exceed production thresholds"
  ]
}
```

**Other examples:**

```bash
# With different model
pbt testcomp analyzer.yaml tests.yaml --model claude

# Markdown report
pbt testcomp prompt.yaml tests.yaml --format markdown > report.md

# Without saving
pbt testcomp prompt.yaml tests.yaml --no-save
```

**Example comprehensive test file:**
```yaml
tests:
  - name: accuracy_test
    inputs:
      text: "Climate change affects global weather patterns"
    expected: "Climate change impacts global weather"
    style_expectation: concise
    evaluate:
      correctness: true
      faithfulness: true
      style_tone: true
      safety: true
      
  - name: stability_test
    inputs:
      text: "Explain quantum computing"
    stability_runs: 5
    evaluate:
      stability: true
      correctness: true
      
  - name: model_comparison
    inputs:
      text: "Summarize this paragraph"
    compare_models:
      - gpt-4
      - claude
      - gpt-3.5-turbo
    evaluate:
      model_quality: true
```

### `pbt validate` - Batch validation of all agents

```bash
# Validate all agents in default directories
pbt validate

# Custom directories
pbt validate --agents-dir custom/agents --tests-dir custom/tests

# With specific model
pbt validate --model gpt-4

# Show individual agent results
pbt validate --individual

# Without saving report
pbt validate --no-save
```

### `pbt ready` - Check production readiness

```bash
# Basic readiness check
pbt ready prompts/summarizer.yaml tests/test_summarizer.yaml

# Custom threshold
pbt ready chatbot.yaml tests.yaml --threshold 0.9

# Without saving report
pbt ready analyzer.yaml tests.yaml --no-save
```

---

## Conversion Commands

### `pbt convert` - Convert Python agents to PBT format

```bash
# Convert single file
pbt convert agents/my_agent.py

# Specify output directory
pbt convert legacy_agent.py --output converted/agents

# Batch convert all Python files
pbt convert ./python_agents --batch

# Batch with custom pattern
pbt convert ./src --batch --pattern "*_agent.py"
```

**Example Python agent:**
```python
def summarizer_agent(text, max_length=100):
    """Summarize text concisely"""
    prompt = f"Summarize in {max_length} chars: {text}"
    return call_llm(prompt)

def translator_agent(text, target_lang):
    """Translate text"""
    prompt = f"Translate to {target_lang}: {text}"
    return call_llm(prompt)
```

**Converts to:**
```yaml
# summarizer.prompt.yaml
name: Summarizer
version: 1.0
model: gpt-4
template: "Summarize in {max_length} chars: {text}"
variables:
  text:
    type: string
  max_length:
    type: string
```

---

## Comparison & Analysis

### `pbt compare` - Compare prompts or models

```bash
# Compare prompt versions
pbt compare tests/test.yaml --mode versions \
  --version v1/prompt.yaml \
  --version v2/prompt.yaml \
  --version v3/prompt.yaml

# Compare models on same prompt
pbt compare tests/test.yaml --mode models \
  --model claude \
  --model gpt-4 \
  --model gpt-3.5-turbo \
  prompts/analyzer.yaml

# Compare with custom test file
pbt compare custom_tests.yaml --mode versions \
  --version old.yaml \
  --version new.yaml
```

### `pbt regression` - Test for regressions

```bash
# Basic regression test
pbt regression current.yaml baseline.yaml tests.yaml

# Without saving report
pbt regression new_version.yaml stable_version.yaml tests.yaml --no-save

# With detailed comparison
pbt regression updated.yaml original.yaml comprehensive_tests.yaml
```

### `pbt eval` - Evaluate prompt quality

```bash
# Evaluate all prompts in folder
pbt eval prompts/

# Specific metrics
pbt eval agents/ --metrics clarity,specificity,effectiveness

# Custom output file
pbt eval prompts/ --output evaluation_report.json

# With different model
pbt eval prompts/ --model claude
```

---

## Optimization

### `pbt optimize` - Optimize prompts for various objectives

```bash
# Analyze optimization opportunities
pbt optimize analyzer.yaml --analyze
```

**Input:**
```bash
pbt optimize verbose_prompt.yaml --analyze
```

**Output:**
```
🔍 Analyzing prompt optimization opportunities: verbose_prompt.yaml

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         Optimization Analysis                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📊 Current Prompt Stats:
   • Word count: 247 words
   • Token count: 321 tokens  
   • Estimated cost per call: $0.000963 (Claude)
   • Readability score: 6.2/10
   • Redundancy detected: HIGH

🎯 Optimization Recommendations:

✅ SHORTEN (High Impact)
   • Remove filler words and redundant phrases
   • Potential token reduction: 65%
   • Cost savings: $0.000626 per call

✅ COST_REDUCE (High Impact)  
   • Eliminate unnecessary elaboration
   • Potential reduction: 70%
   • Monthly savings (1000 calls): $0.63

⚠️ CLARIFY (Medium Impact)
   • Improve sentence structure
   • Better variable definitions
   • Impact: Improved user comprehension

🔧 EMBEDDING (Low Impact)
   • Already well-structured for retrieval
   • Minor improvements possible

💡 Best Strategy: SHORTEN + COST_REDUCE
📈 Expected improvement: 65% cost reduction, 40% clarity increase
```

```bash
# Shorten a verbose prompt
pbt optimize prompts/chatbot.yaml --strategy shorten
```

**Input:**
```bash
pbt optimize prompts/customer_service.yaml --strategy shorten
```

**Output:**
```
🔧 Optimizing prompt: customer_service.yaml
⚡ Strategy: SHORTEN
🎯 Goal: Reduce verbosity while maintaining effectiveness

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                            Optimization Results                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📝 ORIGINAL PROMPT:
────────────────────────────────────────────────────────────────────────────
I would like you to please help me respond to customer inquiries in a way 
that is professional, helpful, and demonstrates empathy towards their concerns. 
Please make sure to address their specific question thoroughly while maintaining 
a friendly and supportive tone throughout your response.

Customer inquiry: {{ customer_message }}

Please provide a comprehensive response that addresses their needs.

📝 OPTIMIZED PROMPT:
────────────────────────────────────────────────────────────────────────────
Respond to this customer inquiry professionally, helpfully, and empathetically:

{{ customer_message }}

Provide a comprehensive, friendly response that addresses their needs.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OPTIMIZATION METRICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📉 Token reduction: 187 → 67 tokens (-64%)
💰 Cost savings: $0.00056 → $0.00020 (-64% per call)  
📈 Clarity score: 6.8 → 8.4 (+23%)
⚡ Processing time: Faster due to fewer tokens

💡 Changes made:
   • Removed redundant phrases ("I would like you to please")
   • Condensed instructions while preserving meaning
   • Maintained all key requirements (professional, helpful, empathetic)
   • Preserved variable structure

✅ Optimized prompt saved to: prompts/customer_service_optimized.yaml
```

```bash
# Reduce costs
pbt optimize expensive_prompt.yaml --strategy cost_reduce
```

**Input:**
```bash
pbt optimize prompts/detailed_analyzer.yaml --strategy cost_reduce
```

**Output:**
```
🔧 Optimizing prompt: detailed_analyzer.yaml
💰 Strategy: COST_REDUCE  
🎯 Goal: Minimize token usage and API costs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 COST OPTIMIZATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Before: 456 tokens → After: 152 tokens (-67%)
💵 Cost per call: $0.00137 → $0.00046 (-67%)

📈 Monthly savings (based on usage):
   • 100 calls/month: $0.91 saved
   • 1,000 calls/month: $9.10 saved  
   • 10,000 calls/month: $91.00 saved

🎯 Optimizations applied:
   ✂️ Removed examples (30% reduction)
   📝 Simplified instructions (25% reduction)
   🔗 Merged redundant sections (12% reduction)

✅ Cost-optimized prompt saved to: prompts/detailed_analyzer_cost_optimized.yaml
⚠️ Note: Test thoroughly to ensure quality is maintained
```

```bash
# Optimize for RAG/embeddings
pbt optimize retrieval_prompt.yaml --strategy embedding --output rag_optimized.yaml
```

**Input:**
```bash
pbt optimize qa_prompt.yaml --strategy embedding --output rag_optimized.yaml
```

**Output:**
```
🔧 Optimizing prompt: qa_prompt.yaml
🔍 Strategy: EMBEDDING
🎯 Goal: Optimize for RAG and vector search systems

✅ Embedding-optimized prompt saved to: rag_optimized.yaml

🔍 RAG Optimization applied:
   • Added semantic keywords for better retrieval
   • Structured context sections for embedding models
   • Optimized for vector similarity matching
   • Enhanced chunk-awareness for better context retention
```

**Example results summary:**
```
Original: "I would like you to please summarize the following text in a way that captures the main ideas"
Optimized: "Summarize the main ideas:"
Reduction: 75% fewer tokens
Cost savings: $0.000012 per call
```

---

## Multi-Agent Chains

### `pbt chain` - Create and execute agent workflows

```bash
# Create chain from template
pbt chain create --template summarize_critique_rewrite

# Create RAG pipeline
pbt chain create --template rag_pipeline --output rag_chain.yaml

# Validate chain configuration
pbt chain validate --file customer_service_chain.yaml

# Execute chain
pbt chain execute --file rag_chain.yaml \
  --inputs '{"query": "What is quantum computing?"}'

# Visualize chain flow
pbt chain visualize --file complex_chain.yaml --output chain_diagram.md
```

**Example chain configuration:**
```yaml
name: Content-Processing-Chain
description: Process content through multiple stages
agents:
  - name: extractor
    prompt_file: agents/extractor.prompt.yaml
    inputs:
      content: string
    outputs: [entities, summary]
    
  - name: enricher
    prompt_file: agents/enricher.prompt.yaml
    inputs:
      entities: list
    outputs: [enriched_data]
    
  - name: formatter
    prompt_file: agents/formatter.prompt.yaml
    inputs:
      data: object
      format: string
    outputs: [formatted_output]

flow:
  - from: extractor
    to: enricher
  - from: enricher
    to: formatter
    condition: enriched_data.quality > 0.8
```

**Chain Templates:**

1. **Summarize-Critique-Rewrite**
```bash
# Create and customize
pbt chain create --template summarize_critique_rewrite
# Edit the generated file to adjust prompts
# Execute with content
pbt chain execute --file summarize_critique_rewrite_chain.yaml \
  --inputs '{"content": "Your long article text here..."}'
```

2. **RAG Pipeline**
```bash
# Create RAG chain
pbt chain create --template rag_pipeline
# Execute with query
pbt chain execute --file rag_pipeline_chain.yaml \
  --inputs '{"query": "How do transformers work?"}'
```

---

## Chunking & RAG

### `pbt chunk` - Create embedding-safe chunks

```bash
# Basic prompt-aware chunking
pbt chunk document.txt --output chunks/

# Chunk with custom settings
pbt chunk large_document.pdf \
  --strategy prompt_aware \
  --max-tokens 512 \
  --overlap 100 \
  --output chunks/

# Semantic chunking
pbt chunk technical_manual.md \
  --strategy semantic \
  --output semantic_chunks/

# Sliding window approach
pbt chunk dataset.txt \
  --strategy sliding_window \
  --max-tokens 256 \
  --overlap 50

# RAG-optimized chunking
pbt chunk knowledge_base.txt \
  --strategy prompt_aware \
  --rag \
  --output rag_chunks/

# Process prompt file with content
pbt chunk qa_prompt.yaml \
  --max-tokens 1024 \
  --rag \
  --output qa_chunks/
```

**Chunking strategies:**

1. **Prompt-Aware** (default)
   - Preserves prompt context in each chunk
   - Adds metadata for better retrieval
   - Maintains semantic coherence

2. **Semantic**
   - Chunks by topic/section boundaries
   - Preserves document structure
   - Good for structured documents

3. **Sliding Window**
   - Fixed-size overlapping windows
   - Consistent chunk sizes
   - Good for uniform content

4. **Recursive**
   - Hierarchical splitting
   - Tries multiple separators
   - Handles varied content well

**Output structure:**
```
chunks/
├── chunk_000.txt          # Chunk content
├── chunk_000_meta.json    # Metadata (tokens, hints, etc.)
├── chunk_001.txt
├── chunk_001_meta.json
└── chunks_summary.json    # Overall summary
```

---

## Deployment & Publishing

### `pbt deploy` - Deploy prompts to cloud

```bash
# Deploy to Supabase
pbt deploy --provider supabase

# Deploy to Vercel with environment
pbt deploy --provider vercel --env staging

# Deploy to AWS with config
pbt deploy --provider aws --config deploy-config.yaml

# Deploy specific environment
pbt deploy --provider gcp --env production
```

### `pbt pack` - Manage prompt packs

```bash
# Build a pack
pbt pack build --name customer-service-pack --version 1.0.0

# Publish to registry
pbt pack publish --name customer-service-pack --registry https://hub.pbt.io

# Install a pack
pbt pack install anthropic/customer-support

# Install specific version
pbt pack install openai/gpt-best-practices@2.1.0
```

### `pbt import` - Import from external sources

```bash
# Import from Notion
pbt import --source notion --token $NOTION_TOKEN

# Import from Airtable
pbt import --source airtable --url https://airtable.com/shrXXXXX

# Import from Google Sheets
pbt import --source sheets --url $SHEET_ID --output imported/

# Import from GitHub
pbt import --source github --url https://github.com/user/prompts
```

---

## Utility Commands

### `pbt render` - Preview prompt rendering

```bash
# Basic render
pbt render prompt.yaml --variables "name=John,age=30"
```

**Input:**
```bash
pbt render email_template.yaml --variables "recipient=John,topic=Project Update,tone=professional"
```

**Output:**
```
🎨 Rendering prompt: email_template.yaml
📝 Variables: recipient=John, topic=Project Update, tone=professional

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                               Rendered Prompt                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Subject: Project Update

Dear John,

I hope this email finds you well. I wanted to provide you with a 
comprehensive update on our current project status.

[Project details would be filled in based on the topic: Project Update]

The tone of this communication is professional, as requested.

Best regards,
[Your name]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Rendering Stats:
   • Template tokens: 45
   • Variable substitutions: 3
   • Final prompt tokens: 52
   • Estimated cost: $0.0001 (Claude)
```

```bash
# Compare models
pbt render prompt.yaml --compare claude,gpt-4,gpt-3.5-turbo
```

**Input:**
```bash
pbt render summarizer.yaml --compare claude,gpt-4,gpt-3.5-turbo --variables "text=Machine learning is transforming industries"
```

**Output:**
```
🎨 Multi-Model Rendering: summarizer.yaml
📝 Variables: text=Machine learning is transforming industries
🔄 Comparing models: claude, gpt-4, gpt-3.5-turbo

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                           Model Comparison Results                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🤖 CLAUDE-3 (Anthropic):
────────────────────────────────────────────────────────────────────────────
ML is revolutionizing multiple sectors through automation, data analysis, 
and intelligent decision-making. Industries like healthcare, finance, and 
manufacturing are experiencing significant operational improvements and 
innovation opportunities.

📊 Stats: 31 tokens | $0.00093 | Response time: 1.2s
⭐ Quality Score: 9.1/10

🤖 GPT-4 (OpenAI):  
────────────────────────────────────────────────────────────────────────────
Machine learning technology is revolutionizing various industries by enabling 
automated decision-making, predictive analytics, and intelligent process 
optimization. Sectors including healthcare, finance, retail, and manufacturing 
are experiencing unprecedented efficiency gains.

📊 Stats: 33 tokens | $0.00165 | Response time: 1.8s
⭐ Quality Score: 9.3/10

🤖 GPT-3.5-TURBO (OpenAI):
────────────────────────────────────────────────────────────────────────────
Machine learning is changing how industries work by automating tasks and 
providing insights from data. Many sectors are benefiting from improved 
efficiency and new capabilities.

📊 Stats: 28 tokens | $0.00042 | Response time: 0.9s  
⭐ Quality Score: 8.7/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 COMPARISON SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 Best Quality: GPT-4 (9.3/10)
🥈 Best Value: GPT-3.5-Turbo ($0.00042) 
🥉 Fastest: GPT-3.5-Turbo (0.9s)

💡 Recommendation: Use GPT-4 for highest quality output, GPT-3.5-Turbo for cost-effective bulk operations.

📄 Full comparison saved to: evaluations/model_comparison_20240115.json
```

```bash
# JSON output
pbt render prompt.yaml --output json
```

**Input:**
```bash
pbt render classifier.yaml --variables "text=This is spam email" --output json
```

**Output:**
```json
{
  "prompt_file": "classifier.yaml",
  "rendered_prompt": "Classify the following text as spam or not spam:\n\nText: This is spam email\n\nClassification:",
  "variables": {
    "text": "This is spam email"
  },
  "template_stats": {
    "original_tokens": 15,
    "final_tokens": 19,
    "variable_substitutions": 1
  },
  "estimated_costs": {
    "claude": 0.000057,
    "gpt-4": 0.000114,
    "gpt-3.5-turbo": 0.000038
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

**Other examples:**

```bash
# With complex variables
pbt render email.yaml --variables "recipient=CEO,topic=Q4 Results,tone=formal"
```

### `pbt deps` - Show dependencies

```bash
# Show all dependencies
pbt deps

# Show for specific prompt
pbt deps --target summarizer

# Show downstream dependencies
pbt deps --target analyzer --downstream

# Output as Mermaid diagram
pbt deps --format mermaid

# Output as JSON
pbt deps --format json
```

### `pbt docs` - Generate documentation

```bash
# Generate docs
pbt docs

# Serve locally
pbt docs --serve

# Custom output directory
pbt docs --output documentation/

# With custom theme
pbt docs --theme minimal
```

### `pbt snapshot` - Version snapshots

```bash
# Create snapshot
pbt snapshot create --reason "Before major refactor"

# Snapshot specific prompt
pbt snapshot create --prompt summarizer --reason "Stable version"

# List snapshots
pbt snapshot list --prompt summarizer

# Show differences
pbt snapshot diff --prompt summarizer

# Restore snapshot
pbt snapshot restore --prompt summarizer --timestamp 2024-01-15
```

### `pbt run` - Execute prompts with dependencies

```bash
# Run all prompts
pbt run

# Run specific prompt and dependencies
pbt run summarizer

# With specific profile
pbt run --profile production

# Full refresh
pbt run --full-refresh

# Target environment
pbt run --profile staging --target dev
```

### `pbt profiles` - Manage profiles

```bash
# List profiles
pbt profiles list

# Create new profile
pbt profiles create --name production

# Validate profile
pbt profiles validate --name staging
```

### `pbt badge` - Manage badges

```bash
# List available badges
pbt badge --list

# Add badge to prompt
pbt badge summarizer.yaml --add GDPR-compliant

# Remove badge
pbt badge analyzer.yaml --remove experimental

# Add multiple badges
pbt badge chatbot.yaml --add production-ready --add security-reviewed
```

### `pbt i18n` - Internationalization

```bash
# Translate to multiple languages
pbt i18n prompt.yaml --languages en,es,fr,de

# Custom output directory
pbt i18n chatbot.yaml --languages ja,ko,zh --output translations/

# Specific language set
pbt i18n support.yaml --languages pt-BR,es-MX
```

---

## Complete Workflow Examples

### Example 1: Building a Customer Service Bot

```bash
# 1. Initialize project
pbt init --name customer-service-bot

# 2. Generate initial prompts
pbt generate --goal "Answer customer questions politely" --variables "question,context,customer_name"
pbt generate --goal "Escalate complex issues to human support" --variables "issue_description,severity"

# 3. Create comprehensive tests
cat > tests/comprehensive_customer_service.yaml << EOF
tests:
  - name: polite_response
    inputs:
      question: "How do I reset my password?"
      customer_name: "John"
    evaluate:
      correctness: true
      style_tone: true
      safety: true
EOF

# 4. Run comprehensive tests
pbt testcomp prompts/answer-customer-questions.yaml tests/comprehensive_customer_service.yaml

# 5. Validate all prompts
pbt validate --individual

# 6. Check production readiness
pbt ready prompts/answer-customer-questions.yaml tests/comprehensive_customer_service.yaml

# 7. Deploy to production
pbt deploy --provider supabase --env production
```

### Example 2: Converting Legacy Python Agents

```bash
# 1. Convert Python agents
pbt convert legacy_agents/ --batch --pattern "*.py"

# 2. Generate tests for converted prompts
for file in agents/*.yaml; do
  pbt gentests "$file" --num-tests 10
done

# 3. Run comprehensive validation
pbt validate --agents-dir agents --tests-dir tests

# 4. Compare with original implementation
pbt compare tests/regression.yaml --mode versions \
  --version legacy/agent.yaml \
  --version agents/agent.yaml

# 5. Create snapshot before deployment
pbt snapshot create --reason "Migrated from Python"
```

### Example 3: Multi-Model Comparison Study

```bash
# 1. Create test suite
cat > tests/model_comparison.yaml << EOF
tests:
  - name: complex_reasoning
    inputs:
      problem: "Explain why the sky is blue"
    compare_models:
      - gpt-4
      - claude
      - gpt-3.5-turbo
      - mistral
    evaluate:
      correctness: true
      style_tone: true
      model_quality: true
EOF

# 2. Run comparison
pbt testcomp science_explainer.yaml tests/model_comparison.yaml --format markdown > comparison_report.md

# 3. Generate cost analysis
pbt eval prompts/ --metrics efficiency,cost --output cost_analysis.json
```

---

## Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Optional
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_ANON_KEY="..."
export PBT_DEFAULT_MODEL="gpt-4"
export PBT_TEST_TIMEOUT="30"
```

---

## Configuration Files

### pbt.yaml
```yaml
name: my-project
version: 1.0.0
prompts_dir: prompts
tests_dir: tests
models:
  default: gpt-4
  available:
    - gpt-4
    - gpt-3.5-turbo
    - claude-3
    - mistral
settings:
  test_timeout: 30
  max_retries: 3
  save_reports: true
```

### profiles.yml
```yaml
development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-3.5-turbo
      temperature: 0.7
      
production:
  target: prod
  outputs:
    prod:
      llm_provider: anthropic
      llm_model: claude-3
      temperature: 0.3
      deployment_provider: supabase
```

---

## Tips & Best Practices

1. **Always test before deploying**: Use `pbt validate` and `pbt ready` before production
2. **Use comprehensive testing**: The `pbt testcomp` command catches more issues
3. **Version your prompts**: Use `pbt snapshot` before major changes
4. **Compare models**: Use `pbt compare` to find the best model for your use case
5. **Document with badges**: Use `pbt badge` to mark compliance and readiness
6. **Batch operations**: Use `--batch` flags for bulk operations
7. **Save reports**: Keep `--save` enabled for audit trails

---

## Getting Help

```bash
# General help
pbt --help

# Command-specific help
pbt generate --help
pbt test --help
pbt testcomp --help

# Version info
pbt --version
```