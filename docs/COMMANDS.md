# PBT Quick Reference

## Command Line Interface

### Project Management
```bash
# Initialize new project
pbt init my-project [--template=default|advanced|enterprise]

# Load existing project
pbt load [project-path]

# Show project status
pbt status
```

### Prompt Operations
```bash
# Generate new prompt
pbt generate "Create a marketing email" --model=claude --style=professional

# Test prompt
pbt test prompts/my_prompt.prompt.yaml [--model=all] [--parallel]

# Render prompt with variables
pbt render prompts/my_prompt.prompt.yaml --vars '{"name": "John", "product": "Widget"}'

# Compare models
pbt compare prompts/my_prompt.prompt.yaml --models=claude,gpt-4,gpt-3.5

# Optimize prompt for cost/performance
pbt optimize prompts/my_prompt.prompt.yaml --target=cost|performance|quality
```

### Evaluation & Testing
```bash
# Run auto-generated tests
pbt test --auto-generate --count=10 prompts/my_prompt.prompt.yaml

# Run specific test types
pbt test --type=functional,safety,performance prompts/my_prompt.prompt.yaml

# Generate evaluation report
pbt evaluate prompts/my_prompt.prompt.yaml --output=json|html|markdown

# Batch test multiple prompts
pbt test prompts/ --recursive --parallel
```

### Advanced Features
```bash
# Chain multiple prompts
pbt chain create my-chain --prompts=prompt1,prompt2,prompt3

# Chunk text with prompt awareness
pbt chunk input.txt --prompt=prompts/summarizer.prompt.yaml --size=1000

# RAG optimization
pbt rag optimize --embeddings=openai --vector-db=qdrant

# Internationalization
pbt i18n extract prompts/ --languages=es,fr,de,ja
```

### Integration Commands
```bash
# Deploy to cloud
pbt deploy --platform=render|fly.io --env=production

# Sync with Notion
pbt notion sync --database-id=xyz --direction=pull|push|bidirectional

# Publish to marketplace
pbt marketplace publish --name="My PromptPack" --price=9.99

# Generate visual content
pbt visual create prompts/my_prompt.prompt.yaml --type=diagram|video|thumbnail
```

## File Structure

### Project Layout
```
my-project/
├── pbt.yaml                 # Project configuration
├── .env                     # Environment variables
├── prompts/                 # Prompt definitions
│   ├── *.prompt.yaml
│   └── chains/              # Multi-step prompt chains
├── tests/                   # Test definitions
│   ├── *.test.yaml
│   └── auto-generated/      # AI-generated tests
├── evaluations/            # Evaluation reports
│   ├── *.evaluation.json
│   └── comparisons/        # Model comparison results
├── chunks/                 # Text chunking configurations
├── outputs/               # Generated content
│   ├── rendered/          # Rendered prompts
│   ├── responses/         # Model responses
│   └── reports/          # Evaluation reports
└── logs/                 # Application logs
```

### Prompt File Format (.prompt.yaml)
```yaml
name: "Text-Summarizer"
version: "1.2.0"
model: "claude"
description: "Summarizes text content with customizable length"

template: |
  Summarize the following text in {{ length }} sentences:
  
  Text: {{ text }}
  
  Requirements:
  - Focus on key points
  - Use clear, concise language
  - Maintain original tone: {{ tone }}

variables:
  text:
    type: string
    description: "Text content to summarize"
    required: true
  length:
    type: integer
    description: "Number of sentences in summary"
    default: 3
    min: 1
    max: 10
  tone:
    type: string
    description: "Desired tone for summary"
    default: "neutral"
    options: ["neutral", "formal", "casual", "academic"]

metadata:
  tags: ["summarization", "content"]
  author: "team@company.com"
  created: "2024-01-15"
  updated: "2024-01-20"
  version_notes: "Added tone control"
  
settings:
  max_tokens: 500
  temperature: 0.3
  safety_level: "high"
  cache_responses: true
```

### Test File Format (.test.yaml)
```yaml
prompt_file: "prompts/summarizer.prompt.yaml"
description: "Tests for text summarization prompt"

test_cases:
  - name: "short_article"
    inputs:
      text: "Machine learning is transforming industries..."
      length: 2
      tone: "neutral"
    expected_criteria:
      - "Contains 2 sentences"
      - "Mentions 'machine learning'"
      - "No factual errors"
    quality_thresholds:
      min_score: 0.8
      max_length: 200
      
  - name: "technical_content"
    inputs:
      text: "Quantum computing utilizes quantum mechanics..."
      length: 3
      tone: "academic"
    expected_criteria:
      - "Academic tone maintained"
      - "Technical accuracy preserved"
      - "3 sentences exactly"

evaluation_criteria:
  correctness: 0.4    # 40% weight
  clarity: 0.3        # 30% weight
  completeness: 0.2   # 20% weight
  style: 0.1          # 10% weight
```

## Configuration Reference

### Environment Variables
```bash
# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://...

# Database
SUPABASE_URL=https://...
SUPABASE_KEY=...
DATABASE_URL=postgresql://...

# Integrations
SLACK_TOKEN=xoxb-...
DISCORD_TOKEN=...
NOTION_TOKEN=secret_...
STRIPE_SECRET_KEY=sk_...

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

### Project Configuration (pbt.yaml)
```yaml
name: "My Project"
version: "1.0.0"
description: "Project description"

# Directory structure
prompts_dir: "prompts"
tests_dir: "tests"
evaluations_dir: "evaluations"
outputs_dir: "outputs"

# Model configuration
models:
  default: "claude"
  available: ["claude", "gpt-4", "gpt-3.5-turbo"]
  fallback: "gpt-3.5-turbo"

# Default settings
settings:
  test_timeout: 30
  max_retries: 3
  parallel_tests: true
  save_reports: true
  cache_responses: true
  
# Cost optimization
optimization:
  target: "balanced"  # cost|performance|quality|balanced
  max_token_reduction: 0.3
  preserve_examples: true

# Safety settings
safety:
  content_filter: true
  bias_detection: true
  toxicity_threshold: 0.1

# Integrations
integrations:
  supabase:
    enabled: true
    sync_prompts: true
  slack:
    enabled: true
    channel: "#pbt-notifications"
  notion:
    enabled: false
    database_id: ""
```

## API Reference

### Python SDK
```python
from pbt import PBTProject, PromptRenderer, PromptEvaluator

# Load project
project = PBTProject.load("./my-project")

# Render prompt
renderer = PromptRenderer(project)
result = await renderer.render(
    "prompts/summarizer.prompt.yaml",
    variables={"text": "...", "length": 3}
)

# Evaluate prompt
evaluator = PromptEvaluator(project)
report = await evaluator.evaluate(
    "prompts/summarizer.prompt.yaml",
    test_cases=[{"inputs": {...}, "expected": {...}}]
)

# Generate new prompt
from pbt import PromptGenerator
generator = PromptGenerator()
prompt = await generator.generate(
    goal="Create a code review assistant",
    style="professional",
    model="claude"
)
```

### REST API
```bash
# Health check
GET /health

# Render prompt
POST /api/v1/prompts/render
{
  "prompt_file": "prompts/summarizer.prompt.yaml",
  "variables": {"text": "...", "length": 3},
  "model": "claude"
}

# Run tests
POST /api/v1/prompts/test
{
  "prompt_file": "prompts/summarizer.prompt.yaml",
  "test_types": ["functional", "safety"],
  "parallel": true
}

# Compare models
POST /api/v1/prompts/compare
{
  "prompt_file": "prompts/summarizer.prompt.yaml",
  "models": ["claude", "gpt-4"],
  "variables": {"text": "...", "length": 3}
}
```

## Common Workflows

### 1. Creating a New Prompt
```bash
# Generate initial prompt
pbt generate "Email marketing assistant" --style=professional

# Edit the generated prompt file
# Add test cases
pbt test prompts/email_assistant.prompt.yaml --auto-generate

# Optimize for cost
pbt optimize prompts/email_assistant.prompt.yaml --target=cost

# Deploy to production
pbt deploy --platform=render
```

### 2. Batch Testing
```bash
# Test all prompts
pbt test prompts/ --recursive --parallel

# Generate comprehensive evaluation report
pbt evaluate prompts/ --output=html --include-comparisons

# Optimize underperforming prompts
pbt optimize prompts/ --threshold=0.8 --target=quality
```

### 3. Team Collaboration
```bash
# Sync with Notion workspace
pbt notion sync --pull

# Run tests and notify team
pbt test prompts/ && pbt slack notify "Tests completed"

# Publish to marketplace
pbt marketplace publish --name="Sales Prompts Pack" --price=19.99
```

## Troubleshooting

### Common Issues
```bash
# Authentication errors
pbt auth check
pbt auth refresh

# Permission issues
pbt config validate
pbt logs --level=error --tail=50

# Performance issues
pbt cache clear
pbt optimize --target=performance prompts/

# Integration failures
pbt integrations status
pbt integrations test slack
```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
pbt test prompts/my_prompt.prompt.yaml --verbose

# Dry run mode
pbt deploy --dry-run --platform=render

# Validate configuration
pbt config validate --strict
```

## Keyboard Shortcuts (CLI)

- `Ctrl+C` - Cancel current operation
- `Ctrl+D` - Exit interactive mode
- `↑/↓` - Navigate command history
- `Tab` - Auto-complete commands and file paths
- `Ctrl+L` - Clear screen
- `Ctrl+R` - Search command history

## Performance Tips

1. **Use parallel testing**: `--parallel` flag for faster test execution
2. **Enable caching**: Set `cache_responses: true` in configuration
3. **Optimize prompts**: Run `pbt optimize` regularly
4. **Batch operations**: Use directory paths instead of individual files
5. **Monitor costs**: Use `pbt costs analyze` to track usage
6. **Use local models**: Consider Ollama for development and testing