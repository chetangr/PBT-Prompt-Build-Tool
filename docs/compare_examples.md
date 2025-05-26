# PBT Compare Command Examples

## Overview

The `pbt compare` command allows you to compare prompt performance across multiple Language Learning Models (LLMs) to help you:
- Find the best model for your use case
- Optimize for cost, quality, or speed
- Understand model-specific behaviors
- Make data-driven decisions about model selection

## Basic Usage

### Simple Comparison
Compare a prompt across default models (Claude, GPT-4, GPT-3.5):

```bash
pbt compare prompts/summarizer.prompt.yaml
```

### Compare Specific Models
Choose which models to compare:

```bash
pbt compare prompts/email_writer.prompt.yaml --models "claude,gpt-4,gpt-3.5-turbo,mistral"
```

### With Variables
Provide variables for prompt rendering:

```bash
pbt compare prompts/translator.prompt.yaml --vars '{"text": "Hello world", "target_language": "Spanish"}'
```

## Output Formats

### Table Format (Default)
```bash
pbt compare prompts/summarizer.prompt.yaml

🔍 Comparing models for prompt: prompts/summarizer.prompt.yaml
📊 Models to compare: claude, gpt-4, gpt-3.5-turbo

📊 Model Comparison Results:

┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Model           ┃ Response Time ┃ Tokens   ┃ Cost     ┃ Quality Score┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ claude          │ 0.45s        │ 450      │ $0.0036  │ 9.2/10       │
│ gpt-4           │ 1.20s        │ 380      │ $0.0114  │ 9.0/10       │
│ gpt-3.5-turbo   │ 0.35s        │ 320      │ $0.0006  │ 7.5/10       │
└─────────────────┴──────────────┴──────────┴──────────┴──────────────┘

💡 Recommendations:
🏆 Best Quality: claude
⚡ Best Speed: gpt-3.5-turbo
💰 Best Cost: gpt-3.5-turbo
⚖️ Balanced: claude
```

### JSON Format
For programmatic processing:

```bash
pbt compare prompts/summarizer.prompt.yaml --output json

{
  "prompt_file": "prompts/summarizer.prompt.yaml",
  "models": ["claude", "gpt-4", "gpt-3.5-turbo"],
  "variables": {},
  "results": {
    "claude": {
      "output": "The text discusses machine learning's transformative impact...",
      "stats": {
        "tokens": 450,
        "cost": 0.0036,
        "response_time": 0.45,
        "quality_score": 9.2
      }
    },
    "gpt-4": {
      "output": "Machine learning technology is revolutionizing...",
      "stats": {
        "tokens": 380,
        "cost": 0.0114,
        "response_time": 1.20,
        "quality_score": 9.0
      }
    }
  },
  "recommendations": {
    "best_quality": "claude",
    "best_speed": "gpt-3.5-turbo",
    "best_cost": "gpt-3.5-turbo",
    "balanced": "claude"
  }
}
```

### Markdown Format
For documentation:

```bash
pbt compare prompts/summarizer.prompt.yaml --output markdown
```

## Real-World Examples

### 1. Customer Email Response Comparison

```bash
# Create a customer service prompt
cat > prompts/customer_email.prompt.yaml << EOF
name: "Customer-Email-Response"
version: "1.0"
model: "claude"
description: "Professional customer service email responses"

template: |
  Write a professional customer service email response.
  
  Customer complaint: {{ complaint }}
  Customer name: {{ name }}
  Issue type: {{ issue_type }}
  
  Requirements:
  - Acknowledge the issue
  - Apologize appropriately
  - Provide solution or next steps
  - Professional and empathetic tone

variables:
  complaint:
    type: string
    description: "Customer's complaint"
    required: true
  name:
    type: string
    description: "Customer's name"
    required: true
  issue_type:
    type: string
    description: "Type of issue"
    default: "general"
EOF

# Compare models with specific scenario
pbt compare prompts/customer_email.prompt.yaml \
  --vars '{
    "complaint": "My order arrived damaged and customer service has been unresponsive for 3 days",
    "name": "Sarah Johnson",
    "issue_type": "shipping"
  }' \
  --models "claude,gpt-4,gpt-3.5-turbo"
```

### 2. Code Generation Comparison

```bash
# Create a code generation prompt
cat > prompts/code_generator.prompt.yaml << EOF
name: "Code-Generator"
version: "1.0"
model: "claude"
description: "Generate code snippets based on requirements"

template: |
  Generate {{ language }} code for the following requirement:
  
  {{ requirement }}
  
  Requirements:
  - Include error handling
  - Add helpful comments
  - Follow {{ language }} best practices
  - Make it production-ready

variables:
  language:
    type: string
    description: "Programming language"
    required: true
  requirement:
    type: string
    description: "What the code should do"
    required: true
EOF

# Compare code generation capabilities
pbt compare prompts/code_generator.prompt.yaml \
  --vars '{
    "language": "Python",
    "requirement": "Function to validate email addresses using regex with comprehensive test cases"
  }' \
  --models "claude-3,gpt-4,gpt-3.5-turbo,mistral"
```

### 3. Multi-Language Translation Comparison

```bash
# Compare translation quality across models
pbt compare prompts/translator.prompt.yaml \
  --vars '{
    "text": "The rapid advancement of artificial intelligence is reshaping industries worldwide.",
    "source_language": "English",
    "target_language": "Japanese"
  }' \
  --models "claude,gpt-4,gpt-3.5-turbo" \
  --output markdown > translation_comparison.md
```

### 4. Creative Writing Comparison

```bash
# Create a creative writing prompt
cat > prompts/story_writer.prompt.yaml << EOF
name: "Story-Writer"
version: "1.0"
model: "claude"
description: "Generate creative story beginnings"

template: |
  Write the opening paragraph of a {{ genre }} story that includes:
  - Setting: {{ setting }}
  - Main character: {{ character }}
  - Mood: {{ mood }}
  
  Make it engaging and atmospheric.

variables:
  genre:
    type: string
    description: "Story genre"
    options: ["mystery", "sci-fi", "fantasy", "thriller"]
  setting:
    type: string
    description: "Where the story takes place"
  character:
    type: string
    description: "Brief character description"
  mood:
    type: string
    description: "Overall mood/atmosphere"
EOF

# Compare creative outputs
pbt compare prompts/story_writer.prompt.yaml \
  --vars '{
    "genre": "mystery",
    "setting": "Victorian London",
    "character": "A retired detective with a secret",
    "mood": "dark and suspenseful"
  }'
```

## Advanced Usage

### Batch Comparison
Compare multiple prompts in sequence:

```bash
# Create a comparison script
for prompt in prompts/*.prompt.yaml; do
  echo "Comparing: $prompt"
  pbt compare "$prompt" --models "claude,gpt-4" --output json > "evaluations/compare_$(basename $prompt .prompt.yaml).json"
done
```

### Cost Analysis
Focus on cost-optimized models:

```bash
# Compare only cost-effective models
pbt compare prompts/bulk_processor.prompt.yaml \
  --models "gpt-3.5-turbo,mistral,claude-instant" \
  --vars '{"items": 1000}' \
  --output json | jq '.results | to_entries | sort_by(.value.stats.cost) | .[0]'
```

### Quality-Focused Comparison
For high-stakes applications:

```bash
# Compare top-tier models only
pbt compare prompts/legal_document.prompt.yaml \
  --models "claude-3,gpt-4,gpt-4-turbo" \
  --vars '{"document_type": "contract", "jurisdiction": "California"}'
```

### Performance Testing
Compare response times under load:

```bash
# Run multiple comparisons to test consistency
for i in {1..5}; do
  echo "Run $i:"
  pbt compare prompts/api_response.prompt.yaml \
    --models "claude,gpt-3.5-turbo" \
    --output json | jq '.results | map_values(.stats.response_time)'
done
```

## Integration with Other Commands

### Compare Then Test
Find the best model, then run comprehensive tests:

```bash
# Step 1: Compare models
pbt compare prompts/classifier.prompt.yaml --models "claude,gpt-4,gpt-3.5-turbo"

# Step 2: Test the recommended model
pbt test prompts/classifier.prompt.yaml --model claude --auto-generate
```

### Compare and Optimize
Use comparison results to optimize prompts:

```bash
# Compare baseline
pbt compare prompts/analyzer.prompt.yaml --vars '{"data": "sample text"}'

# Optimize for cost
pbt optimize prompts/analyzer.prompt.yaml --target cost

# Compare optimized version
pbt compare prompts/analyzer_optimized.prompt.yaml --vars '{"data": "sample text"}'
```

## Understanding Results

### Quality Score Interpretation
- **9-10**: Exceptional quality, production-ready
- **7-8**: Good quality, minor improvements possible
- **5-6**: Acceptable, needs refinement
- **Below 5**: Poor quality, significant issues

### Cost Considerations
- **Input tokens**: Charged for prompt + variables
- **Output tokens**: Charged for model response
- **Total cost**: Input + output token costs

### Response Time Factors
- Model complexity
- Prompt length
- Server location
- Current load

## Tips and Best Practices

### 1. Use Representative Variables
```bash
# Good: Real-world scenario
pbt compare prompts/summarizer.prompt.yaml \
  --vars '{"text": "$(cat sample_documents/real_article.txt)"}'

# Bad: Too simple
pbt compare prompts/summarizer.prompt.yaml \
  --vars '{"text": "This is a test."}'
```

### 2. Compare Relevant Models
```bash
# For cost-sensitive applications
pbt compare prompts/bulk_processor.prompt.yaml \
  --models "gpt-3.5-turbo,claude-instant,mistral"

# For quality-critical applications
pbt compare prompts/medical_advisor.prompt.yaml \
  --models "claude-3,gpt-4,gpt-4-turbo"
```

### 3. Save and Track Results
```bash
# Save with timestamp
pbt compare prompts/analyzer.prompt.yaml \
  --save-results \
  --output json > "comparisons/analyzer_$(date +%Y%m%d_%H%M%S).json"

# Track improvements over time
git add comparisons/
git commit -m "Model comparison results for analyzer prompt"
```

### 4. Use for A/B Testing
```bash
# Compare different prompt versions
pbt compare prompts/email_v1.prompt.yaml --vars '{"scenario": "complaint"}'
pbt compare prompts/email_v2.prompt.yaml --vars '{"scenario": "complaint"}'
```

### 5. Automate Decision Making
```bash
# Script to automatically select best model
BEST_MODEL=$(pbt compare prompts/processor.prompt.yaml --output json | \
  jq -r '.recommendations.balanced')

echo "Deploying with model: $BEST_MODEL"
pbt deploy --model "$BEST_MODEL"
```

## Troubleshooting

### Common Issues

1. **"Model not available" error**
   ```bash
   # Check available models
   pbt models list
   
   # Use only available models
   pbt compare prompts/test.prompt.yaml --models "claude,gpt-3.5-turbo"
   ```

2. **Variables not rendering**
   ```bash
   # Ensure JSON is properly formatted
   pbt compare prompts/test.prompt.yaml \
     --vars "{\"key\": \"value\"}"  # Escape quotes in bash
   ```

3. **Comparison taking too long**
   ```bash
   # Reduce number of models
   pbt compare prompts/test.prompt.yaml \
     --models "claude,gpt-3.5-turbo"  # Skip slower models
   ```

## Next Steps

1. **Regular Comparisons**: Set up weekly model comparisons to track performance changes
2. **Cost Monitoring**: Use comparison data to optimize your model selection strategy
3. **Quality Benchmarks**: Establish quality thresholds for different use cases
4. **Integration Testing**: Combine with `pbt test` for comprehensive validation

The compare command is a powerful tool for making informed decisions about model selection. Use it regularly to ensure you're using the best model for each specific use case while optimizing for your priorities (cost, quality, or speed).