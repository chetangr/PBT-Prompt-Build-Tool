# 🏗️ Architecture Deep Dive

## Overview

PBT follows a modular, plugin-based architecture designed for extensibility, scalability, and maintainability. This document provides a comprehensive look at the system's design, components, and architectural decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (Typer + Click + Rich)                   │
├─────────────────────────────────────────────────────────────┤
│                      Command Layer                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │ Project │ │ Prompt  │ │ Testing │ │ Deploy  │ ...     │
│  │ Commands│ │Commands │ │Commands │ │Commands │         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
├─────────────────────────────────────────────────────────────┤
│                       Core Engine                           │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │   Prompt    │ │   Testing    │ │ Optimization │       │
│  │   Runtime   │ │  Framework   │ │   Engine     │       │
│  └─────────────┘ └──────────────┘ └──────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                    Provider Layer                           │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           │
│  │OpenAI│ │Claude│ │Mistral│ │ Azure│ │Local │ ...       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘           │
├─────────────────────────────────────────────────────────────┤
│                    Storage Layer                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │   File   │ │    Git   │ │   Cloud  │ │   Cache  │     │
│  │  System  │ │ Version  │ │  Storage │ │  System  │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Interface Layer

```python
# pbt/cli/main.py
@app.command()
def test(
    prompt_file: Path,
    test_file: Optional[Path] = None,
    num_tests: int = 10,
    model: Optional[str] = None,
    verbose: bool = False
):
    """
    Typer-based CLI with:
    - Type hints for validation
    - Rich output formatting
    - Progress bars and spinners
    - Interactive prompts
    """
    with console.status("Running tests..."):
        results = TestRunner(prompt_file).run(
            test_file=test_file,
            num_tests=num_tests,
            model=model
        )
    display_results(results, verbose)
```

**Key Features:**
- **Type Safety**: Full type hints with runtime validation
- **Rich UI**: Color output, tables, progress bars
- **Auto-completion**: Shell completion for all commands
- **Help System**: Auto-generated from docstrings

### 2. Command Layer

```python
# Command structure
pbt/
├── cli/
│   ├── commands/
│   │   ├── project.py      # init, profiles, deps
│   │   ├── prompt.py       # generate, render, convert
│   │   ├── testing.py      # test, testcomp, eval
│   │   ├── optimization.py # optimize, analyze
│   │   ├── deployment.py   # deploy, pack, snapshot
│   │   └── workflow.py     # chain, chunk, i18n
│   └── main.py            # Entry point
```

**Command Pattern:**
```python
class Command(ABC):
    @abstractmethod
    def execute(self, context: Context) -> Result:
        pass
    
    @abstractmethod
    def validate(self, args: Dict) -> ValidationResult:
        pass
```

### 3. Core Engine

#### Prompt Runtime

```python
# pbt/runtime.py
class PromptRunner:
    """Central execution engine for prompts"""
    
    def __init__(self, prompt_file: Path):
        self.prompt = PromptLoader.load(prompt_file)
        self.provider = ProviderFactory.create(self.prompt.model)
        self.cache = CacheManager()
        
    def run(self, variables: Dict, **kwargs) -> Result:
        # Variable validation
        validated_vars = self.validate_variables(variables)
        
        # Template rendering
        rendered = self.render_template(validated_vars)
        
        # Cache check
        cache_key = self.generate_cache_key(rendered)
        if cached := self.cache.get(cache_key):
            return cached
            
        # Execute via provider
        result = self.provider.complete(rendered, **kwargs)
        
        # Post-processing
        result = self.post_process(result)
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
```

#### Testing Framework

```python
# pbt/testing/framework.py
class TestFramework:
    """Comprehensive testing system"""
    
    def __init__(self):
        self.evaluators = {
            'correctness': CorrectnessEvaluator(),
            'faithfulness': FaithfulnessEvaluator(),
            'style_tone': StyleToneEvaluator(),
            'safety': SafetyEvaluator(),
            'stability': StabilityEvaluator(),
            'model_quality': ModelQualityEvaluator()
        }
        
    def run_comprehensive_test(
        self,
        prompt: Prompt,
        test_suite: TestSuite,
        aspects: List[str]
    ) -> TestResults:
        results = TestResults()
        
        for test_case in test_suite:
            # Run test
            output = prompt.run(test_case.inputs)
            
            # Evaluate each aspect
            for aspect in aspects:
                evaluator = self.evaluators[aspect]
                score = evaluator.evaluate(
                    output,
                    test_case.expected,
                    test_case.criteria
                )
                results.add_score(aspect, score)
                
        return results
```

### 4. Provider Layer

```python
# pbt/providers/base.py
class Provider(ABC):
    """Base provider interface"""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        pass
        
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
        
    @abstractmethod
    def validate_api_key(self) -> bool:
        pass

# pbt/providers/openai.py
class OpenAIProvider(Provider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def complete(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=kwargs.get('model', 'gpt-4'),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000)
        )
        return response.choices[0].message.content
```

**Provider Factory:**
```python
class ProviderFactory:
    _providers = {
        'gpt-4': OpenAIProvider,
        'claude-3': AnthropicProvider,
        'mistral': MistralProvider,
        # ... more providers
    }
    
    @classmethod
    def create(cls, model: str) -> Provider:
        provider_class = cls._providers.get(model)
        if not provider_class:
            raise ValueError(f"Unknown model: {model}")
        return provider_class()
```

### 5. Storage Layer

#### File System Storage

```python
# pbt/storage/filesystem.py
class FileSystemStorage:
    """Local file system operations"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        
    def read_prompt(self, path: Path) -> Dict:
        with open(self.base_path / path) as f:
            return yaml.safe_load(f)
            
    def write_prompt(self, path: Path, data: Dict):
        with open(self.base_path / path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)
```

#### Version Control Integration

```python
# pbt/storage/git.py
class GitVersionControl:
    """Git integration for version control"""
    
    def __init__(self, repo_path: Path):
        self.repo = git.Repo(repo_path)
        
    def create_snapshot(self, message: str) -> str:
        """Create git commit snapshot"""
        self.repo.index.add("*")
        commit = self.repo.index.commit(message)
        return commit.hexsha
        
    def diff_prompts(self, file_path: Path, ref1: str, ref2: str) -> str:
        """Get diff between versions"""
        return self.repo.git.diff(ref1, ref2, file_path)
```

## Design Patterns

### 1. Plugin Architecture

```python
# pbt/plugins/base.py
class Plugin(ABC):
    """Base plugin interface"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def register(self, app: Application):
        pass

# pbt/plugins/manager.py
class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        
    def load_plugin(self, plugin_path: str):
        """Dynamic plugin loading"""
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        plugin = module.Plugin()
        self.plugins[plugin.name] = plugin
        plugin.register(self.app)
```

### 2. Chain of Responsibility

```python
# pbt/middleware/chain.py
class Middleware(ABC):
    def __init__(self, next_handler: Optional['Middleware'] = None):
        self.next = next_handler
        
    @abstractmethod
    def handle(self, request: Request) -> Response:
        pass
        
    def call_next(self, request: Request) -> Response:
        if self.next:
            return self.next.handle(request)
        return Response()

# Example: Rate limiting middleware
class RateLimitMiddleware(Middleware):
    def handle(self, request: Request) -> Response:
        if self.is_rate_limited(request):
            return Response(error="Rate limit exceeded")
        return self.call_next(request)
```

### 3. Strategy Pattern

```python
# pbt/optimization/strategies.py
class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize(self, prompt: Prompt) -> Prompt:
        pass

class CostReductionStrategy(OptimizationStrategy):
    def optimize(self, prompt: Prompt) -> Prompt:
        # Remove redundancy
        # Shorten instructions
        # Compress examples
        return optimized_prompt

class ClarityStrategy(OptimizationStrategy):
    def optimize(self, prompt: Prompt) -> Prompt:
        # Improve structure
        # Add clarity markers
        # Simplify language
        return optimized_prompt
```

### 4. Observer Pattern

```python
# pbt/events/system.py
class EventSystem:
    def __init__(self):
        self._observers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event: str, callback: Callable):
        self._observers.setdefault(event, []).append(callback)
        
    def emit(self, event: str, data: Any):
        for callback in self._observers.get(event, []):
            callback(data)

# Usage
event_system = EventSystem()
event_system.subscribe('test.complete', lambda data: print(f"Test finished: {data}"))
event_system.emit('test.complete', {'status': 'passed', 'score': 9.5})
```

## Data Flow

### 1. Prompt Execution Flow

```
User Input → CLI Parser → Command Handler → Prompt Loader
    ↓                                           ↓
Variable Validation ← Template Renderer ← Prompt Data
    ↓
Cache Check → Cache Hit → Return Result
    ↓ (miss)
Provider Selection → API Call → Response
    ↓
Post-Processing → Cache Store → Return Result
```

### 2. Testing Flow

```
Test Suite → Test Runner → For Each Test:
                               ↓
                          Load Prompt
                               ↓
                          Render with Test Input
                               ↓
                          Execute via Provider
                               ↓
                          Evaluate Output
                               ↓
                          Score Calculation
                               ↓
                          Aggregate Results
```

## Scalability Architecture

### 1. Horizontal Scaling

```python
# pbt/scaling/distributed.py
class DistributedExecutor:
    """Distribute work across multiple workers"""
    
    def __init__(self, worker_count: int = 4):
        self.executor = ProcessPoolExecutor(max_workers=worker_count)
        self.queue = Queue()
        
    async def execute_batch(self, tasks: List[Task]) -> List[Result]:
        futures = []
        for task in tasks:
            future = self.executor.submit(self.process_task, task)
            futures.append(future)
            
        results = []
        for future in as_completed(futures):
            results.append(future.result())
            
        return results
```

### 2. Caching Strategy

```python
# pbt/cache/manager.py
class CacheManager:
    """Multi-level caching system"""
    
    def __init__(self):
        self.memory_cache = LRUCache(maxsize=1000)
        self.disk_cache = DiskCache(path=".pbt/cache")
        self.redis_cache = RedisCache() if redis_available else None
        
    def get(self, key: str) -> Optional[Any]:
        # L1: Memory
        if value := self.memory_cache.get(key):
            return value
            
        # L2: Disk
        if value := self.disk_cache.get(key):
            self.memory_cache.set(key, value)
            return value
            
        # L3: Redis
        if self.redis_cache and (value := self.redis_cache.get(key)):
            self.memory_cache.set(key, value)
            self.disk_cache.set(key, value)
            return value
            
        return None
```

### 3. Queue System

```python
# pbt/queue/manager.py
class QueueManager:
    """Async task queue for long-running operations"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.workers = []
        
    async def start_workers(self, count: int = 4):
        for i in range(count):
            worker = asyncio.create_task(self.worker(f"worker-{i}"))
            self.workers.append(worker)
            
    async def worker(self, name: str):
        while True:
            task = await self.queue.get()
            try:
                await self.process_task(task)
            except Exception as e:
                logger.error(f"{name} error: {e}")
            finally:
                self.queue.task_done()
```

## Security Architecture

### 1. API Key Management

```python
# pbt/security/keys.py
class SecureKeyManager:
    """Secure API key storage and retrieval"""
    
    def __init__(self):
        self.keyring = keyring.get_keyring()
        
    def store_key(self, service: str, key: str):
        # Encrypt before storing
        encrypted = self.encrypt(key)
        self.keyring.set_password("pbt", service, encrypted)
        
    def get_key(self, service: str) -> str:
        encrypted = self.keyring.get_password("pbt", service)
        return self.decrypt(encrypted) if encrypted else None
```

### 2. Input Validation

```python
# pbt/security/validation.py
class InputValidator:
    """Validate and sanitize all inputs"""
    
    @staticmethod
    def validate_prompt_file(path: Path) -> Path:
        # Path traversal prevention
        resolved = path.resolve()
        if not resolved.is_relative_to(Path.cwd()):
            raise SecurityError("Path traversal detected")
            
        # File type validation
        if resolved.suffix not in ['.yaml', '.yml']:
            raise ValueError("Invalid file type")
            
        return resolved
```

## Performance Optimizations

### 1. Lazy Loading

```python
# pbt/utils/lazy.py
class LazyProperty:
    """Decorator for lazy property evaluation"""
    
    def __init__(self, func):
        self.func = func
        
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

# Usage
class Prompt:
    @LazyProperty
    def compiled_template(self):
        return jinja2.Template(self.template)
```

### 2. Connection Pooling

```python
# pbt/providers/pool.py
class ConnectionPool:
    """Reuse API connections"""
    
    def __init__(self, provider_class, size=10):
        self.pool = Queue(maxsize=size)
        self.provider_class = provider_class
        
        # Pre-populate pool
        for _ in range(size):
            self.pool.put(self.provider_class())
            
    def acquire(self) -> Provider:
        return self.pool.get()
        
    def release(self, provider: Provider):
        self.pool.put(provider)
```

## Error Handling

### 1. Graceful Degradation

```python
# pbt/errors/handlers.py
class ErrorHandler:
    """Centralized error handling with fallbacks"""
    
    @staticmethod
    def with_fallback(primary_func, fallback_func):
        def wrapper(*args, **kwargs):
            try:
                return primary_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Primary failed: {e}, using fallback")
                return fallback_func(*args, **kwargs)
        return wrapper
```

### 2. Circuit Breaker

```python
# pbt/resilience/circuit_breaker.py
class CircuitBreaker:
    """Prevent cascading failures"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'closed'  # closed, open, half_open
        
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure > self.timeout:
                self.state = 'half_open'
            else:
                raise CircuitOpenError()
                
        try:
            result = func(*args, **kwargs)
            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.state = 'open'
            raise e
```

## Testing Architecture

### 1. Test Isolation

```python
# pbt/testing/isolation.py
class TestIsolation:
    """Ensure tests don't interfere with each other"""
    
    def __init__(self):
        self.original_env = {}
        
    def __enter__(self):
        self.original_env = os.environ.copy()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ.clear()
        os.environ.update(self.original_env)
```

### 2. Mock System

```python
# pbt/testing/mocks.py
class MockProvider(Provider):
    """Mock provider for testing"""
    
    def __init__(self, responses: Dict[str, str]):
        self.responses = responses
        self.call_history = []
        
    def complete(self, prompt: str, **kwargs) -> str:
        self.call_history.append((prompt, kwargs))
        return self.responses.get(prompt, "Mock response")
```

## Monitoring & Observability

### 1. Metrics Collection

```python
# pbt/monitoring/metrics.py
class MetricsCollector:
    """Collect and export metrics"""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        
    def increment(self, metric: str, value: int = 1):
        self.counters[metric] += value
        
    @contextmanager
    def timer(self, metric: str):
        start = time.time()
        yield
        self.timers[metric].append(time.time() - start)
        
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        for name, value in self.counters.items():
            lines.append(f"pbt_{name}_total {value}")
        for name, times in self.timers.items():
            avg_time = sum(times) / len(times)
            lines.append(f"pbt_{name}_seconds {avg_time}")
        return "\n".join(lines)
```

### 2. Structured Logging

```python
# pbt/logging/structured.py
class StructuredLogger:
    """JSON structured logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
        
    def with_context(self, **kwargs):
        """Add context to all future logs"""
        self.context.update(kwargs)
        return self
        
    def info(self, message: str, **kwargs):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "info",
            "message": message,
            **self.context,
            **kwargs
        }
        self.logger.info(json.dumps(data))
```

## Future Architecture Considerations

### 1. Microservices Architecture
- Separate services for testing, optimization, deployment
- API Gateway for routing
- Service mesh for communication

### 2. Event-Driven Architecture
- Event streaming with Kafka/Pulsar
- CQRS pattern for read/write separation
- Event sourcing for audit trail

### 3. Cloud-Native Design
- Kubernetes operators
- Serverless functions
- Multi-region deployment

### 4. AI-Native Features
- Embedded AI for optimization
- Predictive scaling
- Intelligent caching

## Summary

PBT's architecture is designed to be:
- **Modular**: Easy to extend and maintain
- **Scalable**: Handles growth from single user to enterprise
- **Resilient**: Graceful failure handling
- **Performant**: Optimized for speed and efficiency
- **Secure**: Built-in security at every layer

The architecture supports the tool's mission of bringing infrastructure-grade engineering practices to prompt development.