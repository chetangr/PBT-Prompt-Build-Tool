# PBT (Prompt Build Tool) - Complete Setup and Usage Instructions

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Core Concepts](#core-concepts)
5. [Prompt Development Workflow](#prompt-development-workflow)
6. [Testing and Quality Assurance](#testing-and-quality-assurance)
7. [Model Comparison and Optimization](#model-comparison-and-optimization)
8. [Advanced Features](#advanced-features)
9. [Team Collaboration](#team-collaboration)
10. [Production Deployment](#production-deployment)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys for LLM providers (Anthropic, OpenAI, etc.)

### Option 1: Install from PyPI (Recommended)

```bash
pip install prompt-build-tool
```

### Option 2: Install from Source

```bash
git clone https://github.com/your-org/prompt-build-tool
cd prompt-build-tool
pip install -e .
```

### Option 3: Use Install Scripts

**For local development:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-org/pbt/main/install_local.sh | bash
```

**For system-wide installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-org/pbt/main/install_system.sh | bash
```

### Verify Installation

```bash
pbt --version
```

You should see output like:
```
PBT (Prompt Build Tool) version 1.0.0

To get started:
1. pbt init - Initialize new project
2. Add ANTHROPIC_API_KEY to .env file
3. pbt generate --goal 'Your prompt goal'

Need API keys? See: API_KEYS.md
```

---

## Getting Started

### 1. Set Up API Keys

Before using PBT, you need API keys from LLM providers. See our [API_KEYS.md](API_KEYS.md) guide for detailed setup instructions.

**Required for basic functionality:**
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com)

**Optional for extended functionality:**
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com)
- `MISTRAL_API_KEY` - Get from [Mistral AI](https://console.mistral.ai)

### 2. Initialize Your First Project

```bash
# Create a new project directory
mkdir my-ai-prompts
cd my-ai-prompts

# Initialize PBT project
pbt init --name "My AI Prompts"
```

This creates the following structure:
```
my-ai-prompts/
├── prompts/              # Your prompt files (.prompt.yaml)
├── tests/                # Test cases and results
├── evaluations/          # Evaluation reports
├── pbt.yaml             # Project configuration
└── .env.example         # Environment variables template
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Add your API keys to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
MISTRAL_API_KEY=your-key-here

# Optional: Set default preferences
PBT_DEFAULT_MODEL=claude
PBT_TEST_TIMEOUT=30
```

### 4. Generate Your First Prompt

```bash
# Generate a prompt using AI
pbt generate --goal "Summarize customer feedback into actionable insights"
```

This will:
- Create `customer-feedback-summarizer.prompt.yaml`
- Generate test cases in `tests/customer-feedback-summarizer.test.jsonl`
- Display a preview of the generated prompt

### 5. Test Your Prompt

```bash
# Run tests on your prompt
pbt test customer-feedback-summarizer.prompt.yaml
```

---

## Project Structure

### Core Files

- **`pbt.yaml`** - Project configuration file
- **`.env`** - Environment variables (API keys, settings)
- **`prompts/`** - Directory containing all prompt files
- **`tests/`** - Test cases and test data
- **`evaluations/`** - Test results and evaluation reports

### Prompt File Structure

Prompt files use the `.prompt.yaml` extension and follow this structure:

```yaml
name: Customer-Feedback-Summarizer
version: 1.0
model: claude
description: "Analyzes customer feedback and provides actionable insights"

template: |
  Analyze the following customer feedback and provide actionable insights:
  
  Feedback: {{ feedback_text }}
  
  Please provide:
  1. Key themes (3-5 bullet points)
  2. Sentiment analysis (positive/negative/neutral)
  3. Recommended actions
  
variables:
  feedback_text:
    type: string
    description: "Raw customer feedback to analyze"
    required: true

metadata:
  tags: ["customer-service", "analysis", "feedback"]
  author: "team@company.com"
  created: "2024-01-15"
  gdpr_compliant: true
```

### Test File Structure

Test files can be in YAML or JSONL format:

**YAML format (`tests/test_summarizer.yaml`):**
```yaml
prompt_file: prompts/summarizer.prompt.yaml
test_cases:
  - name: "short_feedback"
    inputs:
      feedback_text: "Great product, fast shipping!"
    expected_keywords: ["positive", "product", "shipping"]
    quality_criteria: "Should identify positive sentiment"
    
  - name: "negative_feedback"
    inputs:
      feedback_text: "Product arrived damaged, poor packaging"
    expected_keywords: ["negative", "damaged", "packaging"]
    quality_criteria: "Should identify issues and suggest improvements"
```

**JSONL format (`tests/cases.jsonl`):**
```jsonl
{"test_name": "positive_case", "inputs": {"feedback_text": "Amazing service!"}, "expected_keywords": ["positive"], "quality_criteria": "Should detect positive sentiment"}
{"test_name": "negative_case", "inputs": {"feedback_text": "Poor quality product"}, "expected_keywords": ["negative", "quality"], "quality_criteria": "Should identify quality issues"}
```

---

## Core Concepts

### 1. Prompt Templates

PBT uses Jinja2-style templating for dynamic prompts:

```yaml
template: |
  Translate the following text from {{ source_language }} to {{ target_language }}:
  
  Text: {{ text }}
  
  Translation:
```

### 2. Variables

Variables define the inputs your prompt expects:

```yaml
variables:
  text:
    type: string
    description: "Text to translate"
    required: true
    
  source_language:
    type: string
    description: "Source language"
    default: "auto-detect"
    
  target_language:
    type: string
    description: "Target language"
    required: true
    enum: ["English", "Spanish", "French", "German"]
```

### 3. Models

PBT supports multiple LLM providers:

- **Claude** (`claude`, `claude-3`, `claude-instant`)
- **OpenAI** (`gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo`)
- **Mistral** (`mistral-large`, `mistral-medium`, `mistral-small`)

### 4. Evaluation Aspects

PBT evaluates prompts across six key aspects:

1. **Correctness** - Does the output match expectations?
2. **Faithfulness** - Does it stay true to the input?
3. **Style/Tone** - Is the writing style appropriate?
4. **Safety** - Is the content safe and appropriate?
5. **Stability** - Is the output consistent across runs?
6. **Model Quality** - Overall coherence and relevance

---

## Prompt Development Workflow

### Phase 1: Planning and Generation

1. **Define your goal** - What should the prompt accomplish?
2. **Generate initial prompt** - Use `pbt generate` for AI assistance
3. **Review and refine** - Edit the generated prompt as needed

```bash
# Generate initial prompt
pbt generate --goal "Create professional email responses" \
  --variables "recipient,topic,tone" \
  --style "professional"

# Review the generated file
cat professional-email-generator.prompt.yaml
```

### Phase 2: Testing and Validation

1. **Create test cases** - Define expected inputs/outputs
2. **Run basic tests** - Verify functionality
3. **Comprehensive evaluation** - Multi-aspect testing

```bash
# Generate test cases
pbt gentests professional-email-generator.prompt.yaml --num-tests 10

# Run basic tests
pbt test professional-email-generator.prompt.yaml

# Comprehensive evaluation
pbt testcomp professional-email-generator.prompt.yaml tests/comprehensive.yaml
```

### Phase 3: Optimization

1. **Analyze performance** - Review test results
2. **Optimize for cost/clarity** - Use optimization tools
3. **Compare models** - Find the best model for your use case

```bash
# Analyze optimization opportunities
pbt optimize professional-email-generator.prompt.yaml --analyze

# Optimize for cost
pbt optimize professional-email-generator.prompt.yaml \
  --strategy cost_reduce \
  --output optimized/email-generator-optimized.yaml

# Compare across models
pbt render professional-email-generator.prompt.yaml \
  --compare claude,gpt-4,gpt-3.5-turbo
```

### Phase 4: Production Readiness

1. **Final validation** - Ensure production readiness
2. **Create snapshots** - Version control for prompts
3. **Deploy** - Push to production environment

```bash
# Check production readiness
pbt ready professional-email-generator.prompt.yaml tests/comprehensive.yaml

# Create snapshot
pbt snapshot create --prompt professional-email-generator \
  --reason "Production release v1.0"

# Deploy to production
pbt deploy --provider supabase --env production
```

---

## Testing and Quality Assurance

### Test Types

1. **Functional Tests** - Basic input/output validation
2. **Edge Case Tests** - Boundary conditions and error cases  
3. **Performance Tests** - Speed and efficiency metrics
4. **Comprehensive Tests** - Multi-aspect evaluation

### Creating Effective Test Cases

**Good test cases:**
- Cover common use cases
- Include edge cases
- Test different input lengths
- Verify error handling
- Check consistency

**Example comprehensive test:**
```yaml
tests:
  - name: "standard_business_email"
    inputs:
      recipient: "client"
      topic: "project update"
      tone: "professional"
    expected_qualities:
      - "professional language"
      - "clear structure"
      - "appropriate greeting/closing"
    evaluate:
      correctness: true
      style_tone: true
      safety: true
      
  - name: "edge_case_long_topic"
    inputs:
      recipient: "team"
      topic: "very long topic with multiple complex requirements and detailed specifications that need to be addressed"
      tone: "casual"
    stability_runs: 5
    evaluate:
      stability: true
      correctness: true
```

### Automated Testing Pipeline

Set up continuous testing for your prompts:

```bash
# Test all prompts in project
pbt validate

# Run comprehensive tests on all prompts
for prompt in prompts/*.yaml; do
  pbt testcomp "$prompt" tests/comprehensive.yaml
done

# Check for regressions
pbt regression current_version.yaml baseline_version.yaml tests/regression.yaml
```

---

## Model Comparison and Optimization

### Comparing Models

```bash
# Compare specific models
pbt render summarizer.yaml \
  --compare claude,gpt-4,gpt-3.5-turbo \
  --variables "text=Sample text to summarize"

# Test across models
pbt compare tests/comparison.yaml --mode models \
  --model claude \
  --model gpt-4 \
  --model gpt-3.5-turbo \
  summarizer.yaml
```

### Optimization Strategies

1. **SHORTEN** - Reduce verbosity while maintaining effectiveness
2. **CLARIFY** - Improve clarity and specificity
3. **COST_REDUCE** - Minimize token usage for cost savings
4. **EMBEDDING** - Optimize for RAG and vector search

```bash
# Analyze optimization opportunities
pbt optimize verbose_prompt.yaml --analyze

# Apply specific strategy
pbt optimize verbose_prompt.yaml --strategy cost_reduce

# Bulk optimization
for file in prompts/*.yaml; do
  pbt optimize "$file" --strategy shorten --output "optimized/$(basename $file)"
done
```

### Cost Analysis

Track and optimize your prompt costs:

```bash
# Evaluate costs across prompts
pbt eval prompts/ --metrics efficiency,cost --output cost_analysis.json

# Compare costs between versions
pbt compare costs original_prompt.yaml optimized_prompt.yaml
```

---

## Advanced Features

### Multi-Agent Chains

Create complex workflows with multiple connected prompts:

```yaml
# customer_service_chain.yaml
name: Customer-Service-Chain
description: "Complete customer service workflow"

agents:
  - name: intent_classifier
    prompt_file: prompts/classify_intent.yaml
    inputs:
      message: string
    outputs: [intent, urgency_level]
    
  - name: response_generator
    prompt_file: prompts/generate_response.yaml
    inputs:
      intent: string
      urgency_level: number
      original_message: string
    outputs: [response]
    
  - name: quality_checker
    prompt_file: prompts/check_quality.yaml
    inputs:
      response: string
    outputs: [quality_score, suggestions]

flow:
  - from: intent_classifier
    to: response_generator
    
  - from: response_generator
    to: quality_checker
    condition: urgency_level > 3
```

Execute chains:
```bash
# Execute the chain
pbt chain execute --file customer_service_chain.yaml \
  --inputs '{"message": "My order is late and I need it urgently!"}'
```

### Prompt-Aware Chunking

Optimize content for RAG systems:

```bash
# Chunk documents for better retrieval
pbt chunk knowledge_base.md \
  --strategy prompt_aware \
  --max-tokens 512 \
  --overlap 100 \
  --rag \
  --output chunks/

# Chunk with custom prompt context
pbt chunk qa_content.txt \
  --prompt-context prompts/qa_system.yaml \
  --output qa_chunks/
```

### Internationalization

Support multiple languages:

```bash
# Translate prompt to multiple languages
pbt i18n customer_support.yaml --languages en,es,fr,de,ja

# Test translated prompts
pbt test customer_support_es.yaml --model claude
```

### Metadata and SEO

Add rich metadata to prompts:

```yaml
metadata:
  tags: ["customer-service", "multilingual", "production"]
  description: "Customer service prompt with multilingual support"
  keywords: ["support", "help", "assistance"]
  author: "team@company.com"
  version: "2.1.0"
  gdpr_compliant: true
  safety_reviewed: true
  languages: ["en", "es", "fr"]
  use_cases: ["customer-support", "help-desk"]
```

---

## Team Collaboration

### Project Configuration

Configure team settings in `pbt.yaml`:

```yaml
name: "Customer Service AI"
version: "2.0.0"
description: "AI-powered customer service prompts"

team:
  organization: "acme-corp"
  contact: "ai-team@acme-corp.com"
  
models:
  default: claude
  available:
    - claude
    - gpt-4
    - gpt-3.5-turbo
    
environments:
  development:
    model: gpt-3.5-turbo
    temperature: 0.8
  staging:
    model: claude
    temperature: 0.5
  production:
    model: claude
    temperature: 0.3
    
quality_gates:
  min_test_coverage: 0.8
  min_comprehensive_score: 8.0
  required_aspects: ["correctness", "safety", "stability"]
```

### Version Control

Use git with PBT snapshots for comprehensive versioning:

```bash
# Create prompt snapshot
pbt snapshot create --prompt customer_service \
  --reason "Added multilingual support"

# Show snapshot history
pbt snapshot list --prompt customer_service

# Compare snapshots
pbt snapshot diff --prompt customer_service \
  --from 2024-01-01 --to 2024-01-15

# Restore previous version
pbt snapshot restore --prompt customer_service \
  --timestamp 2024-01-10
```

### Code Review Process

1. **Create feature branch** for prompt changes
2. **Run tests** before committing
3. **Use snapshots** to track changes
4. **Require reviews** for production prompts

```bash
# Pre-commit testing
pbt validate
pbt testcomp changed_prompt.yaml tests/comprehensive.yaml

# Create snapshot for review
pbt snapshot create --reason "Feature: Added emotion detection"

# Submit for review with test results
git add .
git commit -m "Add emotion detection to customer service prompt

- Comprehensive test score: 8.7/10
- All safety checks passed  
- Token usage optimized (-15%)
"
```

---

## Production Deployment

### Deployment Options

1. **Cloud Providers** - Supabase, Vercel, AWS, GCP
2. **Container Deployments** - Docker, Kubernetes
3. **API Integrations** - Direct API deployment
4. **Prompt Packs** - Packaged distributions

### Supabase Deployment

```bash
# Set up Supabase deployment
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

# Deploy to Supabase
pbt deploy --provider supabase --env production

# Deploy specific prompts
pbt deploy --provider supabase \
  --prompts "customer_service,email_generator" \
  --env production
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["pbt", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

Build and deploy:
```bash
# Build Docker image
docker build -t my-pbt-app .

# Run container
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  my-pbt-app
```

### Environment Management

Use profiles for different environments:

```yaml
# profiles.yml
development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-3.5-turbo
      temperature: 0.7
      max_tokens: 1000
      
staging:
  target: staging
  outputs:
    staging:
      llm_provider: anthropic
      llm_model: claude
      temperature: 0.5
      max_tokens: 800
      
production:
  target: prod
  outputs:
    prod:
      llm_provider: anthropic
      llm_model: claude
      temperature: 0.3
      max_tokens: 500
      rate_limit: 100
```

Deploy to specific environment:
```bash
pbt deploy --profile production --provider supabase
```

---

## Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: Anthropic API key not found
```
**Solution:**
```bash
# Check if .env file exists and has correct key
cat .env | grep ANTHROPIC_API_KEY

# Reload environment
source .env
```

**2. File Not Found Errors**
```
Error: Could not locate file: summarizer.yaml
```
**Solution:**
```bash
# Use full path or auto-locate
pbt test prompts/summarizer.prompt.yaml

# Or let PBT find it
pbt test summarizer
```

**3. Test Failures**
```
Error: Test failed with score 6.2/10 (below threshold 7.0)
```
**Solution:**
```bash
# Analyze the failure
pbt testcomp prompt.yaml tests.yaml --format json

# Optimize the prompt
pbt optimize prompt.yaml --strategy clarify
```

**4. Model Connection Issues**
```
Error: Connection timeout to Claude API
```
**Solution:**
```bash
# Check API status
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages

# Try different model
pbt test prompt.yaml --model gpt-3.5-turbo

# Increase timeout
export PBT_TEST_TIMEOUT=60
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Enable verbose mode
pbt --verbose test prompt.yaml

# Check configuration
pbt --verbose init --name test-project
```

### Getting Help

```bash
# General help
pbt --help

# Command-specific help
pbt test --help
pbt generate --help

# Check version and status
pbt --version
```

---

## Best Practices

### 1. Prompt Design

**DO:**
- Use clear, specific instructions
- Include examples when helpful
- Define variables with good descriptions
- Test with diverse inputs
- Optimize for your specific use case

**DON'T:**
- Use overly verbose instructions
- Include contradictory requirements
- Assume model knowledge without context
- Skip edge case testing
- Optimize prematurely

### 2. Testing Strategy

**Comprehensive Testing:**
- Test common cases (80% of usage)
- Include edge cases (boundary conditions)
- Verify error handling
- Check consistency across runs
- Validate safety and appropriateness

**Test Organization:**
```
tests/
├── unit/              # Basic functionality tests
├── integration/       # Multi-prompt workflow tests
├── comprehensive/     # Full evaluation tests
├── regression/        # Prevent quality degradation
└── performance/       # Speed and cost tests
```

### 3. Version Control

**Branching Strategy:**
- `main` - Production-ready prompts
- `develop` - Integration branch
- `feature/*` - Individual features
- `hotfix/*` - Critical fixes

**Commit Guidelines:**
```bash
# Good commit messages
git commit -m "Add sentiment analysis to customer service prompt

- Improves emotion detection accuracy by 15%
- Comprehensive test score: 8.9/10
- Cost impact: +$0.0002 per call
- Tested on 500 customer messages"

# Tag releases
git tag -a v1.2.0 -m "Customer service prompt v1.2.0"
```

### 4. Performance Optimization

**Monitor Key Metrics:**
- Token usage and costs
- Response times
- Quality scores
- Error rates

**Optimization Workflow:**
1. Baseline measurement
2. Identify bottlenecks
3. Apply targeted optimizations
4. Measure improvements
5. A/B test in production

### 5. Security and Compliance

**API Key Management:**
- Never commit API keys to git
- Use environment variables
- Rotate keys regularly
- Use different keys for environments

**Data Privacy:**
- Mark GDPR-compliant prompts
- Avoid logging sensitive data
- Use data anonymization when possible
- Regular security reviews

**Content Safety:**
- Test for harmful outputs
- Use safety evaluation aspects
- Implement content filters
- Monitor for bias

### 6. Team Collaboration

**Documentation:**
- Document prompt purpose and use cases
- Include usage examples
- Maintain changelog
- Use clear variable names

**Code Review:**
- Review prompt changes like code
- Require tests for new prompts
- Check performance impact
- Validate safety implications

**Knowledge Sharing:**
- Regular team reviews of prompts
- Share optimization techniques
- Document lessons learned
- Cross-train on different models

---

## Next Steps

1. **Start Small** - Begin with simple prompts and gradually increase complexity
2. **Join the Community** - Participate in discussions and share learnings
3. **Contribute** - Help improve PBT by reporting issues and suggesting features
4. **Scale Up** - Move from individual prompts to complex multi-agent systems

### Resources

- **GitHub Repository**: [https://github.com/your-org/prompt-build-tool](https://github.com/your-org/prompt-build-tool)
- **Documentation**: [examples.md](examples.md) for command examples
- **API Keys Guide**: [API_KEYS.md](API_KEYS.md) for setup instructions
- **Community**: Join our Discord/Slack for support and discussions

### Support

- **Issues**: Report bugs and feature requests on GitHub
- **Email**: Contact support@pbt.ai for enterprise support
- **Documentation**: Check this guide and examples.md for answers

Happy prompt building! 🚀