# 🔧 Troubleshooting PBT Local Setup

## Common Issues and Solutions

### 1. **API Connection Errors**

**Problem**: `Cannot connect to API` or `Connection refused`
```bash
❌ Cannot connect to API. Make sure backend is running on port 8000
```

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:8000/

# Start backend if not running
cd backend
uvicorn main:app --reload --port 8000

# Check if port 8000 is already in use
lsof -i :8000
# If something else is using port 8000, kill it or use different port
uvicorn main:app --reload --port 8001
```

### 2. **Missing Dependencies**

**Problem**: `ModuleNotFoundError` for Python packages
```bash
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn supabase anthropic openai stripe

# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **API Key Issues**

**Problem**: Prompt generation fails with authentication errors
```bash
❌ Prompt generation failed: 401
Error: Invalid API key
```

**Solutions**:
```bash
# Check your .env file has valid keys
cat .env | grep API_KEY

# Get API keys from:
# - Anthropic: https://console.anthropic.com
# - OpenAI: https://platform.openai.com/api-keys

# Make sure .env is in the right location (project root)
ls -la .env
```

### 4. **Supabase Database Issues**

**Problem**: Database connection or table errors
```bash
❌ relation "prompt_packs" does not exist
```

**Solutions**:
```bash
# 1. Create Supabase project at supabase.com
# 2. Run the schema SQL in Supabase SQL editor:
cat backend/db/schema.sql

# 3. Verify tables exist in Supabase dashboard
# 4. Check your Supabase URL and key in .env

# 5. Seed database with sample data
cd backend
python db/seed_prompts.py
```

### 5. **Import Errors**

**Problem**: Python import issues
```bash
ModuleNotFoundError: No module named 'routes'
```

**Solutions**:
```bash
# Make sure you're in the backend directory
cd backend
python -m uvicorn main:app --reload

# Or run from project root with module path
python -m backend.main

# Add __init__.py files if missing
touch backend/__init__.py
touch backend/routes/__init__.py
```

### 6. **CORS Issues (Frontend)**

**Problem**: Browser blocks API requests
```bash
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS
```

**Solutions**:
The backend already includes CORS middleware, but if you still have issues:
```python
# In backend/main.py, make sure CORS is configured:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. **Port Conflicts**

**Problem**: Port already in use
```bash
ERROR: Address already in use
```

**Solutions**:
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001

# Update BASE_URL in test scripts if using different port
```

### 8. **CLI Issues**

**Problem**: CLI commands not working
```bash
python: can't open file 'cli/pbt.py': [Errno 2] No such file or directory
```

**Solutions**:
```bash
# Make sure you're in project root
pwd  # Should show .../PBT-Prompt-Build-Tool

# Make CLI executable
chmod +x cli/pbt.py

# Run with full path
python /Users/chetangrandhe/Desktop/PBT-Prompt-Build-Tool/cli/pbt.py --help

# Add to PATH for easier access
export PATH=$PATH:/Users/chetangrandhe/Desktop/PBT-Prompt-Build-Tool/cli
```

## 🧪 Quick Health Check

Run this minimal test to verify everything is working:

```bash
# 1. Check backend is running
curl http://localhost:8000/

# 2. Test prompt packs endpoint
curl http://localhost:8000/api/promptpacks/list

# 3. Run comprehensive tests
python test_local.py

# 4. Test CLI
python cli/pbt.py --help
```

## 📞 Still Having Issues?

1. **Check the logs** in your terminal for detailed error messages
2. **Verify environment variables** with `env | grep -E "(ANTHROPIC|OPENAI|SUPABASE)"`
3. **Test individual components** before running the full system
4. **Use minimal examples** first, then add complexity

## 🚀 Success Indicators

You'll know everything is working when:
- ✅ `curl http://localhost:8000/` returns `{"message": "PBT API is running"}`
- ✅ `python test_local.py` shows all tests passing
- ✅ API docs load at `http://localhost:8000/docs`
- ✅ CLI shows help with `python cli/pbt.py --help`