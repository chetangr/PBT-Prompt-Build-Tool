#!/bin/bash

echo "🚀 Installing PBT (Prompt Build Tool) - Local Development"
echo "========================================================"

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: setup.py or pyproject.toml not found"
    echo "Please run this script from the PBT project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing build tools..."
pip install build wheel setuptools

echo "📦 Installing PBT in development mode..."
pip install -e ".[all]"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if command -v pbt &> /dev/null; then
    echo "✅ PBT installed successfully!"
    echo ""
    
    # Show version
    echo "📋 Version:"
    pbt --version
    
    echo ""
    echo "📋 Available commands:"
    pbt --help
    
    echo ""
    echo "🔑 Quick start:"
    echo "  1. Create a test project:"
    echo "     mkdir test-project && cd test-project"
    echo "     pbt init --name 'Test Project'"
    echo ""
    echo "  2. Add API keys to .env file"
    echo ""
    echo "  3. Generate a prompt:"
    echo "     pbt generate --goal 'Summarize text'"
    echo ""
    echo "  4. Test the prompt:"
    echo "     pbt test your_prompt.yaml"
    echo ""
    echo "💡 To use PBT in future sessions:"
    echo "   source venv/bin/activate"
    
else
    echo "❌ Installation failed. Checking for issues..."
    echo ""
    echo "Trying to diagnose the problem..."
    
    # Check if package is installed
    python -c "import pbt; print('✅ Package imported successfully')" 2>/dev/null || echo "❌ Package import failed"
    
    # Check entry points
    python -c "import pkg_resources; print([ep for ep in pkg_resources.iter_entry_points('console_scripts') if 'pbt' in ep.name])" 2>/dev/null
    
    exit 1
fi