# 🔄 DBT-like Features in PBT

PBT brings the power of DBT (Data Build Tool) to prompt engineering, providing infrastructure-grade tools for managing prompt dependencies, versioning, and deployment.

## 📋 Table of Contents

1. [Dependency Management (DAG)](#dependency-management-dag)
2. [Profiles & Environments](#profiles--environments)
3. [Snapshots & Version Control](#snapshots--version-control)
4. [Documentation Generation](#documentation-generation)
5. [Run Results & Metrics](#run-results--metrics)
6. [Manifest & Metadata](#manifest--metadata)

## 🔗 Dependency Management (DAG)

### Define Dependencies

Just like DBT, PBT allows you to define dependencies between prompts using the `ref()` function:

```yaml
# prompts/sentiment_analyzer.yaml
name: sentiment_analyzer
version: 1.0.0
depends_on:
  - ref('data_cleaner')  # This prompt depends on data_cleaner
variables:
  - feedback_text
template: |
  Analyze sentiment of: {{ feedback_text }}
```

### Visualize Dependencies

```bash
# Show all dependencies
pbt deps

# Show dependencies for specific prompt
pbt deps --target sentiment_analyzer

# Export as Mermaid diagram
pbt deps --format mermaid

# Show downstream dependencies
pbt deps --target data_cleaner --downstream
```

### Execution Order

PBT automatically resolves dependencies and executes prompts in the correct order:

```bash
# Run all prompts in dependency order
pbt run

# Run specific prompt and its dependencies
pbt run sentiment_analyzer
```

## 👤 Profiles & Environments

### Configure Multiple Environments

Create `profiles.yml` to manage different environments:

```yaml
# profiles.yml
config:
  active_profile: development

development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-4
      temperature: 0.7
      deployment_provider: supabase
      supabase_url: ${SUPABASE_URL}

production:
  target: prod
  outputs:
    prod:
      llm_provider: anthropic
      llm_model: claude-3-opus
      temperature: 0.3
      deployment_provider: supabase
      supabase_url: ${SUPABASE_PROD_URL}
```

### Profile Commands

```bash
# List all profiles
pbt profiles list

# Create new profile
pbt profiles create --name staging

# Validate profile configuration
pbt profiles validate --name production

# Run with specific profile
pbt run --profile production --target prod
```

## 📸 Snapshots & Version Control

### Track Prompt Changes Over Time

```bash
# Create snapshot of all prompts
pbt snapshot create --reason "Before major refactor"

# Snapshot specific prompt
pbt snapshot create --prompt customer_analyzer --reason "Fixing edge case"

# List snapshots
pbt snapshot list --prompt customer_analyzer

# Compare versions
pbt snapshot diff --prompt customer_analyzer

# Restore previous version
pbt snapshot restore --prompt customer_analyzer --timestamp 2024-01-15T10:30:00
```

### Automatic Change Detection

Snapshots include:
- Full prompt content
- Version numbers
- Checksums for integrity
- Metadata and tags
- Timestamp and reason

## 📚 Documentation Generation

### Auto-Generate Documentation

```bash
# Generate documentation for all prompts
pbt docs

# Specify output directory
pbt docs --output docs/prompts

# Serve documentation locally
pbt docs --serve
```

### Generated Documentation Includes:

1. **Index Page**
   - All prompts grouped by tags
   - Quick navigation
   - Project metadata

2. **Individual Prompt Pages**
   - Description and version
   - Variables documentation
   - Examples with inputs/outputs
   - Dependencies
   - Model configuration

3. **Lineage Diagram**
   - Visual dependency graph
   - Mermaid format
   - Interactive navigation

## 📊 Run Results & Metrics

### Track Execution History

```bash
# View latest run results
cat .pbt/run_results.json

# Run with full tracking
pbt run --profile production
```

### Run Results Include:

```json
{
  "run_id": "20240115_103045_123456",
  "project_name": "customer-analytics",
  "started_at": "2024-01-15T10:30:45Z",
  "elapsed_time": 45.3,
  "success": true,
  "results": [
    {
      "unique_id": "data_cleaner",
      "status": "success",
      "execution_time": 2.1
    }
  ]
}
```

### Export Metrics

```python
from pbt.core.run_results import RunResultsManager

manager = RunResultsManager(Path.cwd())
metrics = manager.export_metrics()

# Metrics include:
# - Success rate
# - Average duration
# - Failure reasons
# - Performance trends
```

## 📋 Manifest & Metadata

### Generate Project Manifest

The manifest provides a complete snapshot of your project:

```python
from pbt.core.manifest import Manifest

manifest = Manifest(Path.cwd())
manifest.load_prompts()
manifest.to_json(Path("manifest.json"))
```

### Manifest Contains:

```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "pbt_version": "0.1.0",
    "project_name": "my-prompts"
  },
  "prompts": {
    "data_cleaner": {
      "version": "1.0.0",
      "checksum": "abc123...",
      "depends_on": [],
      "tags": ["utility"]
    }
  }
}
```

### Freshness Validation

```python
# Check if prompts have changed without version update
stale = manifest.validate_freshness()
for prompt in stale:
    print(f"{prompt['name']} has uncommitted changes")
```

## 🔄 Materialization Strategies

Configure how prompts are materialized:

```yaml
# prompts/my_prompt.yaml
config:
  materialized: table      # Always rebuild
  # OR
  materialized: view       # Lightweight reference
  # OR
  materialized: incremental # Only process new data
  unique_key: prompt_id
```

## 🎯 Best Practices

1. **Use Semantic Versioning**: Update versions when prompts change
2. **Document Dependencies**: Use `ref()` to make dependencies explicit
3. **Profile Per Environment**: Separate dev/staging/prod configurations
4. **Regular Snapshots**: Snapshot before major changes
5. **Test in Lower Environments**: Use profiles to test safely
6. **Monitor Run Results**: Track performance over time

## 🚀 Example Workflow

```bash
# 1. Initialize project
pbt init my-analytics-prompts

# 2. Create profiles
cat > profiles.yml << EOF
development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-4
EOF

# 3. Generate prompt with dependencies
pbt generate --goal "Clean customer data" --output prompts/data_cleaner.yaml
pbt generate --goal "Analyze sentiment" --output prompts/sentiment.yaml

# 4. Add dependency
# Edit sentiment.yaml to add: depends_on: [ref('data_cleaner')]

# 5. View dependencies
pbt deps --format mermaid

# 6. Run with dependency resolution
pbt run sentiment --profile development

# 7. Create snapshot
pbt snapshot create --reason "Initial version"

# 8. Generate documentation
pbt docs --serve

# 9. Deploy to production
pbt run --profile production --full-refresh
```

## 🔧 Integration with CI/CD

```yaml
# .github/workflows/pbt.yml
name: PBT Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PBT
        run: pip install prompt-build-tool
      
      - name: Validate profiles
        run: pbt profiles validate
      
      - name: Run tests
        run: pbt test --profile ci
      
      - name: Generate docs
        run: pbt docs --output public/
      
      - name: Deploy to staging
        if: github.ref == 'refs/heads/main'
        run: pbt run --profile staging
```

## 🤝 Contributing

The DBT-like features in PBT are designed to bring software engineering best practices to prompt engineering. We welcome contributions to expand these capabilities!