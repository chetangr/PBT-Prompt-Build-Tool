# PBT Studio - Web UI Guide

## Overview

PBT Studio is a modern web interface for the Prompt Build Tool that provides a visual, interactive way to compare Language Learning Models (LLMs) side by side. Similar to dbt Cloud's interface, it offers an intuitive experience for prompt engineering, testing, and optimization.

## Features

### 🎯 Core Capabilities

1. **Multi-Model Comparison**
   - Compare prompts across multiple LLMs simultaneously
   - Real-time streaming responses
   - Side-by-side output visualization

2. **Automatic Scoring**
   - Provide expected outputs for automatic evaluation
   - Multiple evaluation metrics (exact match, word overlap, etc.)
   - Visual score indicators

3. **Performance Metrics**
   - Response time tracking
   - Token usage monitoring
   - Cost estimation per model
   - Quality score calculation

4. **Smart Recommendations**
   - Best model for quality
   - Fastest response time
   - Most cost-effective option
   - Balanced recommendation

## Getting Started

### Installation

First, ensure you have the web dependencies installed:

```bash
# Install PBT with web UI support
pip install 'prompt-build-tool[web]'

# Or install web dependencies separately
pip install fastapi uvicorn aiohttp pydantic
```

### Launching the Web UI

Start the web interface with a single command:

```bash
# Start with default settings (port 8080)
pbt web

# Custom port
pbt web --port 3000

# Bind to all interfaces (for network access)
pbt web --host 0.0.0.0

# Don't open browser automatically
pbt web --no-open
```

The web UI will automatically open in your default browser at `http://localhost:8080`.

## Using the Interface

### 1. Prompt Configuration

#### Basic Prompt
Enter your prompt in the main text area. Use double curly braces for variables:

```
Summarize the following text in {{num_sentences}} sentences:

{{text}}

Focus on the key points and maintain the original tone.
```

#### Variables
Variables are automatically detected from your prompt. You can:
- Add custom variables with the "+ Add" button
- Set variable values for testing
- Remove variables you don't need

#### Expected Output (Optional)
Provide an expected output to enable automatic scoring:
- Helps evaluate model accuracy
- Enables quality scoring
- Useful for regression testing

### 2. Model Selection

Choose which models to compare:
- **Claude** - Anthropic's flagship model
- **GPT-4** - OpenAI's most capable model
- **GPT-3.5 Turbo** - Fast and cost-effective
- **Mistral** - Open-source alternative
- **Claude 3** - Latest Claude version
- **GPT-4 Turbo** - Optimized GPT-4

### 3. Advanced Settings

Fine-tune your comparison:
- **Temperature** (0-2): Controls randomness (0.7 default)
- **Max Tokens**: Maximum response length (1000 default)

### 4. Running Comparisons

Click "Compare Models" to:
1. Send your prompt to all selected models
2. See real-time progress updates
3. Get detailed results with metrics
4. Receive smart recommendations

## Understanding Results

### Model Response Cards

Each model's response includes:
- **Model Name** and version
- **Quality Score** (if expected output provided)
- **Response Time** in seconds
- **Cost Estimate** in USD
- **Token Count** for the response
- **Full Output** with syntax highlighting

### Performance Metrics

Summary statistics across all models:
- **Average Response Time** - Overall speed comparison
- **Total Cost** - Combined cost for all models
- **Average Tokens** - Output length comparison
- **Average Score** - Quality comparison (if applicable)

### Recommendations

Smart suggestions based on your priorities:
- 🏆 **Best Quality** - Highest scoring model
- ⚡ **Best Speed** - Fastest response time
- 💰 **Best Cost** - Most economical option
- ⚖️ **Balanced** - Best overall value

## Advanced Features

### Real-time Streaming

The web UI uses WebSocket connections for:
- Live progress updates
- Streaming responses as they generate
- Reduced perceived latency
- Better user experience

### Export Options

Export your comparison results:
- **JSON** - Complete data for analysis
- **Markdown** - Formatted report for documentation
- **Share** - Generate shareable link (coming soon)

### Saved Prompts

Save frequently used prompts:
- Store prompt templates
- Save variable configurations
- Quick access to common tests
- Build a prompt library

### History

Access previous comparisons:
- Review past results
- Track improvements over time
- Reload previous configurations
- Compare changes

## Example Workflows

### 1. Quick Model Comparison

```javascript
// Example prompt for customer service
Write a professional response to this customer complaint:

{{complaint}}

Requirements:
- Acknowledge the issue
- Apologize appropriately 
- Provide a solution
- Professional tone
```

Variables:
- `complaint`: "My order arrived damaged and support hasn't responded in 3 days"

### 2. Quality Testing with Expected Output

```javascript
// Prompt
Translate the following to {{language}}:
{{text}}

// Variables
language: "Spanish"
text: "Hello, how are you?"

// Expected Output
"Hola, ¿cómo estás?"
```

### 3. Cost Optimization Analysis

Compare models for bulk processing:
1. Select cost-effective models (GPT-3.5, Claude Instant, Mistral)
2. Use a representative prompt
3. Analyze cost vs. quality trade-offs
4. Choose optimal model for your use case

## API Integration

The web UI exposes a REST API for programmatic access:

### Compare Models
```bash
POST /api/compare
Content-Type: application/json

{
  "prompt": "Your prompt here",
  "models": ["claude", "gpt-4"],
  "variables": {"key": "value"},
  "expected_output": "Optional expected result"
}
```

### Get Available Models
```bash
GET /api/models
```

### Save Prompt
```bash
POST /api/prompts/save
Content-Type: application/json

{
  "name": "My Prompt",
  "description": "Description",
  "prompt": "Template",
  "variables": {},
  "models": ["claude"]
}
```

## Deployment Options

### Local Development
Default setup for personal use:
```bash
pbt web
```

### Team Access
Share with your team:
```bash
# Bind to all interfaces
pbt web --host 0.0.0.0 --port 8080

# Access from other machines
http://your-ip-address:8080
```

### Production Deployment

Using Docker:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install prompt-build-tool[web]
EXPOSE 8080
CMD ["pbt", "web", "--host", "0.0.0.0"]
```

Using Docker Compose:
```yaml
version: '3.8'
services:
  pbt-studio:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./prompts:/app/prompts
```

## Configuration

### Environment Variables
Set API keys for model access:
```bash
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key
export MISTRAL_API_KEY=your-key
```

### Custom Styling
The UI uses CSS variables for theming. Modify `/static/styles.css`:
```css
:root {
  --primary-color: #2563eb;
  --bg-primary: #ffffff;
  --text-primary: #1e293b;
}
```

## Troubleshooting

### Common Issues

#### "Web UI dependencies not installed"
```bash
pip install fastapi uvicorn aiohttp pydantic
```

#### "Port already in use"
```bash
# Use a different port
pbt web --port 8081
```

#### "Cannot connect to models"
- Check API keys are set correctly
- Verify network connectivity
- Ensure models are available in your region

### Debug Mode
Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
pbt web
```

## Best Practices

### 1. Prompt Design
- Use clear variable names
- Provide detailed instructions
- Test with edge cases
- Include examples in prompts

### 2. Model Selection
- Start with 2-3 models
- Include a baseline model
- Consider cost vs. quality needs
- Test with your actual use cases

### 3. Evaluation
- Provide realistic expected outputs
- Use multiple test cases
- Consider subjective quality
- Track improvements over time

### 4. Cost Management
- Monitor token usage
- Set max token limits
- Use appropriate models for tasks
- Cache results when possible

## Future Enhancements

### Planned Features
- Prompt version control
- A/B testing framework
- Batch processing UI
- Collaborative editing
- Custom evaluation metrics
- Integration with PBT CLI
- Prompt marketplace
- Team workspaces

### Community Contributions
We welcome contributions! Areas of interest:
- Additional model integrations
- Custom themes
- Evaluation plugins
- Export formats
- Visualization improvements

## Conclusion

PBT Studio brings visual, interactive prompt engineering to your browser. It's designed to make model comparison intuitive, efficient, and data-driven. Whether you're optimizing for quality, speed, or cost, the web UI provides the insights you need to make informed decisions.

Start exploring with:
```bash
pbt web
```

Happy prompt engineering! 🚀