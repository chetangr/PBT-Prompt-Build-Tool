# 📡 API Documentation

## Overview

PBT provides both a Python API for programmatic access and a REST API for remote operations. This document covers both interfaces comprehensively.

## Python API

### Core Classes

#### PromptRunner

The main class for executing prompts programmatically.

```python
from pbt import PromptRunner

class PromptRunner:
    """Execute prompts with variable substitution and model selection."""
    
    def __init__(self, prompt_file: Union[str, Path]):
        """
        Initialize a PromptRunner.
        
        Args:
            prompt_file: Path to the prompt YAML file
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt file is invalid
        """
    
    def run(
        self, 
        variables: Dict[str, Any],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> PromptResult:
        """
        Execute the prompt with given variables.
        
        Args:
            variables: Dictionary of variable values
            model: Override default model
            temperature: Override temperature setting
            max_tokens: Override max tokens
            **kwargs: Additional provider-specific parameters
            
        Returns:
            PromptResult object containing output and metadata
            
        Example:
            >>> runner = PromptRunner("greeting.prompt.yaml")
            >>> result = runner.run({"name": "Alice"})
            >>> print(result.output)
            "Hello Alice! How can I help you today?"
        """
    
    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render the prompt template without executing.
        
        Args:
            variables: Dictionary of variable values
            
        Returns:
            Rendered prompt string
        """
    
    def validate_variables(self, variables: Dict[str, Any]) -> ValidationResult:
        """
        Validate variables against prompt schema.
        
        Returns:
            ValidationResult with is_valid and errors
        """
```

#### PromptResult

Result object returned by prompt execution.

```python
@dataclass
class PromptResult:
    """Result from prompt execution."""
    
    output: str
    """The generated text output"""
    
    model: str
    """Model used for generation"""
    
    tokens_used: int
    """Total tokens consumed"""
    
    cost: float
    """Estimated cost in USD"""
    
    latency: float
    """Execution time in seconds"""
    
    metadata: Dict[str, Any]
    """Additional metadata from provider"""
    
    cached: bool = False
    """Whether result was from cache"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
    
    def to_json(self) -> str:
        """Convert to JSON string."""
```

#### TestRunner

Execute tests programmatically.

```python
from pbt.testing import TestRunner

class TestRunner:
    """Run prompt tests and evaluations."""
    
    def __init__(self, prompt_file: Union[str, Path]):
        """Initialize test runner for a prompt."""
    
    def run_test_file(
        self,
        test_file: Union[str, Path],
        verbose: bool = False
    ) -> TestResults:
        """
        Run tests from a test file.
        
        Args:
            test_file: Path to test YAML file
            verbose: Show detailed output
            
        Returns:
            TestResults object
        """
    
    def run_single_test(
        self,
        inputs: Dict[str, Any],
        expected: Any,
        test_name: str = "test"
    ) -> TestResult:
        """Run a single test case."""
    
    def run_comprehensive_test(
        self,
        test_file: Union[str, Path],
        aspects: List[str] = None
    ) -> ComprehensiveResults:
        """Run 6-aspect comprehensive evaluation."""
```

#### Chain

Multi-agent workflow orchestration.

```python
from pbt.chains import Chain

class Chain:
    """Execute multi-agent workflows."""
    
    def __init__(self, chain_file: Union[str, Path]):
        """Load chain definition from file."""
    
    def execute(
        self,
        initial_inputs: Dict[str, Any],
        max_steps: int = 10
    ) -> ChainResult:
        """
        Execute the chain with given inputs.
        
        Args:
            initial_inputs: Starting variables
            max_steps: Maximum steps to prevent loops
            
        Returns:
            ChainResult with all step outputs
        """
    
    def visualize(self) -> str:
        """Generate Mermaid diagram of chain flow."""
    
    def validate(self) -> ValidationResult:
        """Validate chain configuration."""
```

### Utility Functions

#### Optimization

```python
from pbt.optimization import optimize_prompt

def optimize_prompt(
    prompt_file: Union[str, Path],
    strategy: str = "balanced",
    target_reduction: float = 0.3,
    preserve_quality: float = 0.95
) -> OptimizationResult:
    """
    Optimize a prompt file.
    
    Args:
        prompt_file: Path to prompt file
        strategy: One of "cost_reduce", "clarity", "balanced"
        target_reduction: Target token reduction (0.0-1.0)
        preserve_quality: Minimum quality to maintain (0.0-1.0)
        
    Returns:
        OptimizationResult with optimized prompt and metrics
        
    Example:
        >>> result = optimize_prompt("verbose.yaml", strategy="cost_reduce")
        >>> print(f"Reduced tokens by {result.reduction_percentage}%")
    """
```

#### Model Comparison

```python
from pbt.comparison import compare_models

def compare_models(
    prompt_file: Union[str, Path],
    models: List[str],
    test_inputs: List[Dict[str, Any]],
    metrics: List[str] = ["quality", "cost", "speed"]
) -> ComparisonResult:
    """
    Compare prompt performance across models.
    
    Args:
        prompt_file: Prompt to test
        models: List of model names
        test_inputs: Test cases
        metrics: Metrics to evaluate
        
    Returns:
        ComparisonResult with model rankings
    """
```

### Advanced Usage

#### Custom Providers

```python
from pbt.providers import Provider, register_provider

class CustomProvider(Provider):
    """Implement custom LLM provider."""
    
    def complete(self, prompt: str, **kwargs) -> str:
        # Your implementation
        return "response"
    
    def validate_api_key(self) -> bool:
        # Validate credentials
        return True

# Register the provider
register_provider("custom-model", CustomProvider)

# Use it
runner = PromptRunner("prompt.yaml")
result = runner.run({"var": "value"}, model="custom-model")
```

#### Custom Evaluators

```python
from pbt.testing.evaluators import Evaluator, register_evaluator

class DomainSpecificEvaluator(Evaluator):
    """Custom evaluation logic."""
    
    def evaluate(
        self,
        output: str,
        expected: Any,
        criteria: Dict[str, Any]
    ) -> float:
        # Your evaluation logic
        score = calculate_domain_score(output, expected)
        return score  # 0.0 to 10.0

# Register evaluator
register_evaluator("domain_specific", DomainSpecificEvaluator)

# Use in tests
test_config = {
    "evaluators": ["domain_specific"],
    "criteria": {"threshold": 0.8}
}
```

#### Event Handlers

```python
from pbt.events import on_event

@on_event("prompt.executed")
def log_execution(event_data):
    print(f"Prompt executed: {event_data['prompt_name']}")
    print(f"Tokens used: {event_data['tokens_used']}")

@on_event("test.failed")
def alert_on_failure(event_data):
    send_alert(f"Test failed: {event_data['test_name']}")

# Events are automatically triggered during execution
```

## REST API

### Base URL

```
https://api.promptbuildtool.com/v1
# or self-hosted
http://localhost:8000/api/v1
```

### Authentication

All API requests require authentication via API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.promptbuildtool.com/v1/prompts
```

### Endpoints

#### Prompts

##### List Prompts
```http
GET /prompts

Query Parameters:
- page (int): Page number (default: 1)
- limit (int): Items per page (default: 20)
- search (string): Search term
- tags (string): Comma-separated tags

Response:
{
  "prompts": [
    {
      "id": "prompt_123",
      "name": "customer-classifier",
      "version": "1.2.0",
      "description": "Classify customer intents",
      "tags": ["classification", "customer-service"],
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

##### Get Prompt
```http
GET /prompts/{prompt_id}

Response:
{
  "id": "prompt_123",
  "name": "customer-classifier",
  "version": "1.2.0",
  "content": {
    "template": "Classify the following message...",
    "variables": {
      "message": {
        "type": "string",
        "required": true
      }
    },
    "model": "gpt-4",
    "temperature": 0.3
  },
  "metadata": {
    "author": "john@example.com",
    "tags": ["classification"],
    "performance": {
      "avg_tokens": 150,
      "avg_latency": 1.2
    }
  }
}
```

##### Create Prompt
```http
POST /prompts

Request Body:
{
  "name": "new-prompt",
  "content": {
    "template": "Your prompt template here",
    "variables": {
      "input": {
        "type": "string"
      }
    },
    "model": "gpt-4"
  },
  "tags": ["new", "example"]
}

Response:
{
  "id": "prompt_456",
  "name": "new-prompt",
  "version": "1.0.0",
  "created_at": "2024-01-25T12:00:00Z"
}
```

##### Execute Prompt
```http
POST /prompts/{prompt_id}/execute

Request Body:
{
  "variables": {
    "message": "I need help with my order"
  },
  "model": "gpt-4",  // optional override
  "temperature": 0.5  // optional override
}

Response:
{
  "output": "I'd be happy to help with your order...",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  },
  "cost": 0.00495,
  "latency": 1.234,
  "model": "gpt-4",
  "cached": false
}
```

#### Testing

##### Run Tests
```http
POST /tests/run

Request Body:
{
  "prompt_id": "prompt_123",
  "test_suite": "comprehensive",
  "test_cases": [
    {
      "name": "test_1",
      "inputs": {"message": "Hello"},
      "expected": "greeting"
    }
  ]
}

Response:
{
  "test_run_id": "run_789",
  "status": "completed",
  "summary": {
    "total": 10,
    "passed": 9,
    "failed": 1,
    "score": 9.0
  },
  "results": [
    {
      "test_name": "test_1",
      "status": "passed",
      "score": 10.0,
      "output": "greeting",
      "latency": 0.523
    }
  ]
}
```

##### Get Test Results
```http
GET /tests/runs/{run_id}

Response:
{
  "test_run_id": "run_789",
  "prompt_id": "prompt_123",
  "started_at": "2024-01-25T14:00:00Z",
  "completed_at": "2024-01-25T14:05:00Z",
  "status": "completed",
  "results": {...}
}
```

#### Optimization

##### Optimize Prompt
```http
POST /optimize

Request Body:
{
  "prompt_id": "prompt_123",
  "strategy": "cost_reduce",
  "constraints": {
    "max_reduction": 0.5,
    "preserve_quality": 0.9
  }
}

Response:
{
  "optimization_id": "opt_234",
  "original": {
    "tokens": 250,
    "cost_per_call": 0.0075
  },
  "optimized": {
    "tokens": 150,
    "cost_per_call": 0.0045,
    "reduction": 0.4
  },
  "quality_score": 0.95,
  "suggestions": [
    "Removed redundant instructions",
    "Combined similar examples",
    "Simplified variable descriptions"
  ]
}
```

#### Chains

##### Execute Chain
```http
POST /chains/{chain_id}/execute

Request Body:
{
  "inputs": {
    "customer_message": "I need urgent help!"
  },
  "max_steps": 5
}

Response:
{
  "execution_id": "exec_567",
  "status": "completed",
  "steps": [
    {
      "agent": "classifier",
      "output": {"intent": "support", "urgency": "high"},
      "latency": 0.8
    },
    {
      "agent": "router",
      "output": {"route": "priority_support"},
      "latency": 0.3
    }
  ],
  "total_latency": 1.1,
  "total_cost": 0.0023
}
```

### Webhooks

Configure webhooks to receive events:

```http
POST /webhooks

Request Body:
{
  "url": "https://your-app.com/webhook",
  "events": ["prompt.executed", "test.completed", "optimization.finished"],
  "secret": "your-webhook-secret"
}
```

Webhook Payload Example:
```json
{
  "event": "test.completed",
  "timestamp": "2024-01-25T15:00:00Z",
  "data": {
    "test_run_id": "run_890",
    "prompt_id": "prompt_123",
    "score": 9.5,
    "passed": true
  },
  "signature": "sha256=..."
}
```

### Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid prompt template",
    "details": {
      "field": "template",
      "reason": "Missing required variable placeholder"
    }
  },
  "request_id": "req_abc123"
}
```

Common Error Codes:
- `AUTHENTICATION_ERROR`: Invalid or missing API key
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_ERROR`: Too many requests
- `PROVIDER_ERROR`: LLM provider error
- `INTERNAL_ERROR`: Server error

### Rate Limits

Default rate limits:
- 100 requests per minute per API key
- 1000 requests per hour per API key
- 10 concurrent requests per API key

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706189460
```

## SDK Examples

### Python SDK

```python
from pbt import Client

# Initialize client
client = Client(api_key="your-api-key")

# List prompts
prompts = client.prompts.list(tags=["production"])

# Execute prompt
result = client.prompts.execute(
    prompt_id="prompt_123",
    variables={"message": "Hello"},
    model="gpt-4"
)

# Run tests
test_results = client.tests.run(
    prompt_id="prompt_123",
    test_suite="comprehensive"
)

# Optimize
optimization = client.optimize(
    prompt_id="prompt_123",
    strategy="cost_reduce"
)
```

### JavaScript/TypeScript SDK

```typescript
import { PBTClient } from '@promptbuildtool/sdk';

// Initialize client
const client = new PBTClient({
  apiKey: 'your-api-key'
});

// Execute prompt
const result = await client.prompts.execute('prompt_123', {
  variables: { message: 'Hello' },
  model: 'gpt-4'
});

// Run comprehensive test
const testResults = await client.tests.runComprehensive('prompt_123');

// Execute chain
const chainResult = await client.chains.execute('chain_456', {
  inputs: { query: 'Help needed' }
});
```

### cURL Examples

```bash
# List prompts
curl -X GET \
  -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.promptbuildtool.com/v1/prompts?tags=production"

# Execute prompt
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {"message": "Hello"},
    "model": "gpt-4"
  }' \
  "https://api.promptbuildtool.com/v1/prompts/prompt_123/execute"

# Run tests
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "prompt_123",
    "test_suite": "basic"
  }' \
  "https://api.promptbuildtool.com/v1/tests/run"
```

## Best Practices

### API Usage

1. **Use caching**: Cache prompt results when possible
2. **Batch operations**: Group multiple operations
3. **Handle errors gracefully**: Implement exponential backoff
4. **Monitor usage**: Track API calls and costs
5. **Use webhooks**: For async operations

### Security

1. **Rotate API keys**: Regular key rotation
2. **Use environment variables**: Never hardcode keys
3. **Validate inputs**: Always validate user inputs
4. **Use HTTPS**: Always use encrypted connections
5. **Implement rate limiting**: Protect your endpoints

### Performance

1. **Use appropriate models**: Don't use GPT-4 for simple tasks
2. **Optimize prompts**: Reduce token usage
3. **Implement caching**: Cache common responses
4. **Use streaming**: For long responses
5. **Monitor latency**: Track and optimize slow calls

## Support

- **Documentation**: https://docs.promptbuildtool.com
- **API Status**: https://status.promptbuildtool.com
- **Support**: support@promptbuildtool.com
- **Discord**: https://discord.gg/pbt