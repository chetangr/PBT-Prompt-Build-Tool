#!/bin/bash

echo "🚀 Installing PBT (Prompt Build Tool)"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install PBT
echo "📦 Installing PBT..."

# Option 1: Install from local directory (development)
if [ -f "setup.py" ]; then
    echo "🔧 Installing from local directory..."
    pip install -e .
    
# Option 2: Install from PyPI (when published)
else
    echo "🔧 Installing from PyPI..."
    pip install prompt-build-tool
fi

# Verify installation
echo "🔍 Verifying installation..."
if command -v pbt &> /dev/null; then
    echo "✅ PBT installed successfully!"
    echo ""
    echo "📋 Quick start:"
    echo "  pbt --help          # Show all commands"
    echo "  pbt init            # Initialize new project"
    echo "  pbt generate --goal 'Your prompt goal'"
    echo ""
    echo "🔑 Next steps:"
    echo "1. Set up API keys in .env file"
    echo "2. Visit: https://docs.promptbuildtool.com"
    
    # Show version
    pbt --version
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi