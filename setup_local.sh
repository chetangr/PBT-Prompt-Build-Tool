#!/bin/bash

echo "🚀 Setting up PBT (Prompt Build Tool) locally..."

# Check if Python 3.9+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📍 Found Python $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip to avoid issues
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies with specific versions to avoid conflicts
echo "📦 Installing dependencies..."
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install supabase==1.2.0
pip install anthropic==0.3.11
pip install openai==0.28.1
pip install stripe==7.8.0
pip install requests==2.31.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6
pip install python-dotenv==1.0.0
pip install markdownify==0.11.6
pip install PyYAML==6.0.1
pip install urllib3==1.26.18
pip install certifi==2023.11.17

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before starting!"
fi

# Make CLI executable
chmod +x cli/pbt.py

echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Edit .env with your API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)"
echo "2. Set up Supabase database using backend/db/schema.sql"
echo "3. Start the backend: cd backend && uvicorn main:app --reload"
echo "4. Test the setup: python test_local.py"
echo ""
echo "💡 To activate the virtual environment in future sessions:"
echo "   source venv/bin/activate"