# 🛠️ Detailed Setup Instructions

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Environment Setup](#environment-setup)
4. [Project Initialization](#project-initialization)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Setup](#advanced-setup)

## Prerequisites

### System Requirements

#### Hardware
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 1GB free space
- **Network**: Stable internet connection

#### Software
- **Operating System**: 
  - macOS 10.15+
  - Ubuntu 20.04+
  - Windows 10+ (WSL2 recommended)
- **Python**: 3.8 - 3.11
- **pip**: 20.0+
- **Git**: 2.0+

### Check Prerequisites

```bash
# Check Python version
python --version
# or
python3 --version

# Should output: Python 3.8.x or higher

# Check pip
pip --version
# or
pip3 --version

# Check git
git --version
```

## Installation Methods

### Method 1: pip (Recommended)

```bash
# Install latest stable version
pip install prompt-build-tool

# Or with all optional dependencies
pip install prompt-build-tool[all]

# Verify installation
pbt --version
```

### Method 2: pipx (Isolated Environment)

```bash
# Install pipx first
python -m pip install --user pipx
python -m pipx ensurepath

# Install PBT
pipx install prompt-build-tool

# Verify
pbt --version
```

### Method 3: From Source

```bash
# Clone repository
git clone https://github.com/prompt-build-tool/pbt.git
cd pbt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or with all dependencies
pip install -e ".[all]"
```

### Method 4: Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone and install
git clone https://github.com/prompt-build-tool/pbt.git
cd pbt
poetry install
```

### Method 5: Docker

```bash
# Pull official image
docker pull promptbuildtool/pbt:latest

# Run with current directory mounted
docker run -it -v $(pwd):/workspace \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  promptbuildtool/pbt:latest
```

## Environment Setup

### Step 1: API Keys

#### Create .env file
```bash
# Navigate to your project directory
cd ~/my-pbt-projects

# Create .env from template
curl -o .env https://raw.githubusercontent.com/prompt-build-tool/pbt/main/.env.example

# Or create manually
touch .env
```

#### Add your API keys
```bash
# Edit .env file
nano .env  # or vim, code, etc.
```

Add at least one LLM provider:
```bash
# Required (choose at least one)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx

# Optional providers
MISTRAL_API_KEY=xxxxx
COHERE_API_KEY=xxxxx
```

### Step 2: Shell Configuration

#### Bash/Zsh
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(_PBT_COMPLETE=bash_source pbt)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

#### Fish
```bash
# Add to ~/.config/fish/config.fish
set -gx PATH $HOME/.local/bin $PATH
pbt --install-completion fish
```

#### PowerShell
```powershell
# Add to $PROFILE
Add-Content $PROFILE '$env:Path += ";$env:USERPROFILE\.local\bin"'
pbt --install-completion powershell
```

### Step 3: Global Configuration

```bash
# Create global config directory
mkdir -p ~/.pbt

# Set default configuration
cat > ~/.pbt/config.yaml << EOF
defaults:
  model: gpt-4
  temperature: 0.7
  max_tokens: 1000
  
profiles:
  development:
    model: gpt-3.5-turbo
    temperature: 0.7
    
  production:
    model: gpt-4
    temperature: 0.3
    
cache:
  enabled: true
  ttl: 3600
  directory: ~/.pbt/cache
EOF
```

## Project Initialization

### Step 1: Create New Project

```bash
# Basic initialization
pbt init my-first-project

# With template
pbt init my-chatbot --template chatbot

# With git
pbt init my-project --git

# Full options
pbt init my-advanced-project \
  --template enterprise \
  --git \
  --profile production \
  --models gpt-4,claude-3
```

### Step 2: Project Structure

After initialization:
```
my-first-project/
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── pbt.yaml            # Project configuration
├── profiles.yml        # Environment profiles
├── prompts/            # Prompt files
│   └── example.prompt.yaml
├── tests/              # Test files
│   └── example.test.yaml
├── chains/             # Chain workflows
├── docs/               # Documentation
└── README.md           # Project README
```

### Step 3: Configure Project

Edit `pbt.yaml`:
```yaml
name: my-first-project
version: 1.0.0
description: My first PBT project

models:
  default: gpt-4
  available:
    - gpt-4
    - gpt-3.5-turbo
    - claude-3
    - mistral-large

settings:
  test_timeout: 30
  parallel_tests: 5
  auto_save: true
  
optimization:
  auto_optimize: true
  target_reduction: 0.3
  preserve_quality: 0.95
```

## Configuration

### Profile Configuration

Edit `profiles.yml`:
```yaml
# Development environment
development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-3.5-turbo
      temperature: 0.7
      max_tokens: 1000
      cache_enabled: true
      
# Staging environment
staging:
  target: staging
  outputs:
    staging:
      llm_provider: anthropic
      llm_model: claude-3
      temperature: 0.5
      max_tokens: 2000
      monitoring: true
      
# Production environment
production:
  target: prod
  outputs:
    prod:
      llm_provider: openai
      llm_model: gpt-4
      temperature: 0.3
      max_tokens: 1500
      monitoring: true
      alerting: true
      backup_model: claude-3
```

### Advanced Configuration

```yaml
# Advanced pbt.yaml
name: enterprise-project
version: 2.0.0

# Model configuration with fallbacks
models:
  primary:
    provider: openai
    model: gpt-4
    fallback: gpt-3.5-turbo
    
  secondary:
    provider: anthropic
    model: claude-3
    fallback: claude-2
    
  embeddings:
    provider: openai
    model: text-embedding-3-large

# Performance settings
performance:
  max_concurrent_requests: 10
  request_timeout: 30
  retry_attempts: 3
  retry_delay: 5
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60

# Security settings
security:
  api_key_rotation: 90  # days
  encrypt_cache: true
  sanitize_logs: true
  allowed_domains:
    - "*.mycompany.com"
    - "api.trusted-partner.com"

# Monitoring
monitoring:
  provider: datadog
  metrics:
    - latency
    - token_usage
    - error_rate
    - cost
  alerts:
    - metric: error_rate
      threshold: 0.05
      action: page
    - metric: latency_p95
      threshold: 3000
      action: notify

# Deployment
deployment:
  environments:
    - name: development
      auto_deploy: false
      approval_required: false
      
    - name: staging
      auto_deploy: true
      approval_required: false
      tests_required: true
      
    - name: production
      auto_deploy: false
      approval_required: true
      tests_required: true
      min_test_score: 9.0
```

## Verification

### Step 1: Basic Verification

```bash
# Check installation
pbt --version

# Check environment
pbt doctor

# Output should show:
# ✅ Python version: 3.10.0
# ✅ PBT version: 1.0.0
# ✅ Git: installed
# ✅ API keys: configured
# ✅ Network: connected
```

### Step 2: API Key Verification

```bash
# Validate all configured keys
pbt validate-keys

# Test specific provider
pbt validate-keys --provider openai

# Output:
# ✅ OPENAI_API_KEY: Valid (GPT-4 access confirmed)
# ✅ ANTHROPIC_API_KEY: Valid (Claude-3 access confirmed)
```

### Step 3: Full System Test

```bash
# Run complete verification
pbt doctor --comprehensive

# This checks:
# - Installation integrity
# - All dependencies
# - API connectivity
# - File permissions
# - Cache functionality
# - Network latency
```

### Step 4: Test Run

```bash
# Generate a test prompt
pbt generate --goal "Test prompt that says hello"

# Render it
pbt render prompts/test-prompt.prompt.yaml

# Run tests
pbt test prompts/test-prompt.prompt.yaml
```

## Troubleshooting

### Common Issues

#### 1. Command Not Found
```bash
# Fix: Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use python module
python -m pbt.cli.main --help
```

#### 2. Permission Denied
```bash
# Fix: Install with --user
pip install --user prompt-build-tool

# Or fix permissions
chmod +x ~/.local/bin/pbt
```

#### 3. Import Errors
```bash
# Fix: Reinstall with all dependencies
pip uninstall prompt-build-tool
pip install prompt-build-tool[all] --force-reinstall
```

#### 4. API Key Issues
```bash
# Debug: Check environment
env | grep API_KEY

# Fix: Export directly
export OPENAI_API_KEY="sk-..."

# Or use .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Platform-Specific Issues

#### macOS
```bash
# SSL Certificate issues
pip install --upgrade certifi

# Xcode tools needed
xcode-select --install
```

#### Linux
```bash
# Missing system packages
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# Permission issues
sudo usermod -a -G docker $USER  # If using Docker
```

#### Windows
```bash
# Use WSL2 for best experience
wsl --install

# Or fix path issues
setx PATH "%PATH%;%USERPROFILE%\.local\bin"
```

## Advanced Setup

### 1. Corporate Proxy

```bash
# Set proxy environment
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# Configure pip
pip config set global.proxy http://proxy.company.com:8080
```

### 2. Custom Installation Location

```bash
# Install to specific directory
pip install --target /opt/pbt prompt-build-tool

# Add to Python path
export PYTHONPATH="/opt/pbt:$PYTHONPATH"
export PATH="/opt/pbt/bin:$PATH"
```

### 3. Development Setup

```bash
# Clone repository
git clone https://github.com/prompt-build-tool/pbt.git
cd pbt

# Create development environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=pbt
```

### 4. Multi-User Setup

```bash
# System-wide installation (requires sudo)
sudo pip install prompt-build-tool

# Create shared configuration
sudo mkdir -p /etc/pbt
sudo cp config.yaml /etc/pbt/

# Set permissions
sudo chmod 644 /etc/pbt/config.yaml

# User overrides in ~/.pbt/config.yaml
```

### 5. CI/CD Setup

```yaml
# .github/workflows/pbt.yml
name: PBT CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install PBT
        run: |
          pip install prompt-build-tool
          pbt --version
          
      - name: Run Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pbt test prompts/*.yaml
          pbt validate --comprehensive
```

## Next Steps

After successful setup:

1. **Follow the Getting Started guide** to create your first prompt
2. **Read the Quick Reference** for common commands
3. **Explore Examples** in the documentation
4. **Join the Community** on Discord for support

## Quick Setup Script

Save this as `setup-pbt.sh`:

```bash
#!/bin/bash
# Quick PBT Setup Script

echo "🚀 Setting up PBT..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Install PBT
echo "📦 Installing PBT..."
pip install --user prompt-build-tool

# Create project directory
echo "📁 Creating project directory..."
mkdir -p ~/pbt-projects
cd ~/pbt-projects

# Initialize first project
echo "🎉 Initializing first project..."
pbt init my-first-project

# Create .env file
echo "🔑 Setting up environment..."
cd my-first-project
cp .env.example .env
echo "⚠️  Please edit .env and add your API keys"

# Done
echo "✅ Setup complete!"
echo "📍 Your project is at: ~/pbt-projects/my-first-project"
echo "📝 Next: Edit .env and add your API keys"
```

Make it executable and run:
```bash
chmod +x setup-pbt.sh
./setup-pbt.sh
```