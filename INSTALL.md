# 🚀 PBT Installation Guide

## Local Development Installation

Since PBT is not yet published to PyPI, follow these steps to install it locally:

### Option 1: Automated Installation (Recommended)

```bash
cd /Users/chetangrandhe/Desktop/PBT-Prompt-Build-Tool
./install_local.sh
```

### Option 2: Manual Installation

```bash
# 1. Navigate to project directory
cd /Users/chetangrandhe/Desktop/PBT-Prompt-Build-Tool

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip and install build tools
pip install --upgrade pip
pip install build wheel setuptools

# 4. Install PBT in development mode
pip install -e ".[all]"

# 5. Verify installation
pbt --version
pbt --help
```

### Option 3: Build and Install Wheel

```bash
# 1. Build the wheel
cd /Users/chetangrandhe/Desktop/PBT-Prompt-Build-Tool
python -m build

# 2. Install the wheel
pip install dist/prompt_build_tool-0.1.0-py3-none-any.whl[all]
```

## Verification

After installation, verify PBT is working:

```bash
# Check version
pbt --version

# Show help
pbt --help

# Create test project
mkdir test-pbt && cd test-pbt
pbt init --name "Test Project"
```

## Next Steps

1. **Configure API Keys**: Copy `.env.example` to `.env` and add your API keys
2. **Generate Prompts**: `pbt generate --goal "Your prompt goal"`
3. **Test Prompts**: `pbt test your_prompt.yaml`
4. **Start Server**: `pbt serve`

## Troubleshooting

### "pbt command not found"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Or reinstall in development mode
pip install -e .
```

### Import Errors

```bash
# Install all dependencies
pip install -e ".[all]"

# Or install specific extras
pip install -e ".[server]"  # For server functionality
pip install -e ".[dev]"     # For development tools
```

### CLI Not Working

```bash
# Check if entry points are registered
python -c "import pkg_resources; print([ep.name for ep in pkg_resources.iter_entry_points('console_scripts') if 'pbt' in ep.name])"

# Should output: ['pbt', 'prompt-build-tool']
```

## Publishing to PyPI (For Maintainers)

When ready to publish:

```bash
# 1. Update version in pbt/__version__.py
# 2. Build distribution
python -m build

# 3. Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# 4. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ prompt-build-tool

# 5. Upload to PyPI
python -m twine upload dist/*
```

Then users can install with:
```bash
pip install prompt-build-tool[all]
```