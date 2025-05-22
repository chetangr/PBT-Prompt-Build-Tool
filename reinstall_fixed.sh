#!/bin/bash

echo "🔧 Reinstalling PBT with .env loading fixes"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Run from PBT project root."
    exit 1
fi

echo "📦 Upgrading pip..."
pip3 install --upgrade pip

echo "📦 Installing python-dotenv (required for .env loading)..."
pip3 install python-dotenv

echo "📦 Reinstalling PBT with fixes..."
pip3 install --force-reinstall -e ".[all]"

echo ""
echo "🧪 Testing the fix..."
python3 test_env_fix.py

echo ""
echo "✅ PBT reinstalled with automatic .env loading!"
echo ""
echo "🚀 Now users can simply:"
echo "1. Create .env file: echo 'ANTHROPIC_API_KEY=sk-ant-your-key' > .env"
echo "2. Run PBT commands: pbt generate --goal 'test'"
echo "3. No manual environment setup needed!"
echo ""
echo "💡 Test it:"
echo "   cd /path/to/your/project"
echo "   echo 'ANTHROPIC_API_KEY=your-real-key' > .env"
echo "   pbt generate --goal 'Summarize customer feedback' --variables 'feedback'"