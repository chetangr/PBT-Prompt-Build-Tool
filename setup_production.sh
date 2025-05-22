#!/bin/bash

echo "🚀 Setting up PBT (Prompt Build Tool) - Production Ready"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "📍 $python_version"

# Check if we need to create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Verify critical dependencies
echo "🔍 Verifying installations..."
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import anthropic; print('✅ Anthropic installed')"
python -c "import openai; print('✅ OpenAI installed')"
python -c "import supabase; print('✅ Supabase installed')"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your actual API keys:"
    echo "   - ANTHROPIC_API_KEY (get from console.anthropic.com)"
    echo "   - OPENAI_API_KEY (get from platform.openai.com)"
    echo "   - SUPABASE_URL and SUPABASE_KEY (get from supabase.com)"
    echo ""
fi

# Make CLI executable
chmod +x cli/pbt.py

echo "✅ Production setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Set up Supabase database:"
echo "   - Create project at supabase.com"
echo "   - Run SQL from backend/db/schema.sql in Supabase SQL editor"
echo "   - Run: python backend/db/seed_prompts.py"
echo "3. Start the backend:"
echo "   cd backend && uvicorn main:app --reload --port 8000"
echo "4. Test the setup:"
echo "   python test_local.py"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🧪 Test CLI: python cli/pbt.py --help"