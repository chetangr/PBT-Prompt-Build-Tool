#!/bin/bash

echo "🚀 Installing PBT (Prompt Build Tool) - System Installation"
echo "=========================================================="

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

echo "📦 Upgrading pip..."
pip3 install --upgrade pip

echo "📦 Installing build tools..."
pip3 install build wheel setuptools

echo "📦 Installing PBT globally..."
pip3 install -e ".[all]"

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
    echo "🔑 Required API Keys:"
    echo "===================="
    echo ""
    echo "📍 ANTHROPIC_API_KEY (Required)"
    echo "   • Get from: https://console.anthropic.com"
    echo "   • Used for: Prompt generation, evaluation, Claude judge"
    echo "   • Cost: Pay-per-use (~$0.01-0.10 per prompt)"
    echo ""
    echo "📍 OPENAI_API_KEY (Required)" 
    echo "   • Get from: https://platform.openai.com/api-keys"
    echo "   • Used for: GPT-4 prompt generation and comparison"
    echo "   • Cost: Pay-per-use (~$0.03-0.12 per prompt)"
    echo ""
    echo "📍 SUPABASE_URL & SUPABASE_KEY (Optional - for database features)"
    echo "   • Get from: https://supabase.com (free tier available)"
    echo "   • Used for: Storing prompts, evaluations, user data"
    echo "   • Cost: Free up to 500MB, then ~$25/month"
    echo ""
    echo "📍 STRIPE_SECRET_KEY (Optional - for marketplace)"
    echo "   • Get from: https://dashboard.stripe.com"
    echo "   • Used for: Payment processing in marketplace"
    echo "   • Cost: 2.9% + 30¢ per transaction"
    echo ""
    echo "📍 SLACK_WEBHOOK_URL (Optional - for notifications)"
    echo "   • Get from: https://api.slack.com/messaging/webhooks"
    echo "   • Used for: Slack notifications when prompts are created/tested"
    echo "   • Cost: Free"
    echo ""
    echo "📍 DISCORD_WEBHOOK_URL (Optional - for notifications)"
    echo "   • Get from: Discord server settings > Integrations > Webhooks"
    echo "   • Used for: Discord notifications"
    echo "   • Cost: Free"
    echo ""
    echo "🔧 Setup Instructions:"
    echo "====================="
    echo "1. Create a new project:"
    echo "   mkdir my-prompts && cd my-prompts"
    echo "   pbt init --name 'My Prompts'"
    echo ""
    echo "2. Add your API keys to .env file:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Add your actual API keys"
    echo ""
    echo "3. Generate your first prompt:"
    echo "   pbt generate --goal 'Summarize customer feedback'"
    echo ""
    echo "4. Test the prompt:"
    echo "   pbt test your_prompt.yaml"
    echo ""
    echo "5. Start the web server (optional):"
    echo "   pbt serve"
    echo ""
    echo "💡 Minimum to get started:"
    echo "   Just ANTHROPIC_API_KEY is enough for basic prompt generation and testing!"
    
else
    echo "❌ Installation failed. Checking for issues..."
    echo ""
    echo "Trying to diagnose the problem..."
    
    # Check if package is installed
    python3 -c "import pbt; print('✅ Package imported successfully')" 2>/dev/null || echo "❌ Package import failed"
    
    # Check entry points
    python3 -c "import pkg_resources; print([ep for ep in pkg_resources.iter_entry_points('console_scripts') if 'pbt' in ep.name])" 2>/dev/null
    
    echo ""
    echo "🔧 Try fixing with:"
    echo "   pip3 install --force-reinstall -e ."
    
    exit 1
fi