# PBT Troubleshooting Guide

## Quick Diagnosis

### System Check Commands
```bash
# Check PBT version and installation
pbt --version
pbt status

# Verify Python environment
python --version
pip list | grep prompt-build-tool

# Check configuration
pbt config validate
pbt config show

# Test connectivity
pbt integrations status
```

### Log Analysis
```bash
# View recent logs
pbt logs --tail=50 --level=error

# Debug mode
export LOG_LEVEL=DEBUG
pbt test prompts/my_prompt.yaml --verbose

# Check specific component logs
tail -f logs/pbt_core.log
tail -f logs/pbt_evaluator.log
tail -f logs/pbt_integrations.log
```

## Common Issues and Solutions

### 🔧 Installation Problems

#### Issue: "Command not found: pbt"
**Symptoms**: 
- `pbt: command not found` after installation
- `pip install` appears successful

**Causes**:
- Python binary not in PATH
- Installation in wrong environment
- Shell not refreshed

**Solutions**:
```bash
# Verify installation
pip show prompt-build-tool

# Check if installed in user directory
ls ~/.local/bin/pbt

# Add to PATH if needed
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Alternative: Use python module
python -m pbt --version

# Reinstall if necessary
pip uninstall prompt-build-tool
pip install prompt-build-tool
```

#### Issue: "Module not found" errors
**Symptoms**:
- `ModuleNotFoundError: No module named 'pbt'`
- Import errors when running commands

**Solutions**:
```bash
# Check Python environment
which python
which pip

# Reinstall with force
pip install --upgrade --force-reinstall prompt-build-tool

# Check virtual environment
python -c "import sys; print(sys.path)"

# Use specific Python version
python3.11 -m pip install prompt-build-tool
```

#### Issue: Dependency conflicts
**Symptoms**:
- Package dependency resolution failures
- Version conflicts during installation

**Solutions**:
```bash
# Create clean virtual environment
python -m venv pbt-env
source pbt-env/bin/activate  # Linux/Mac
# or pbt-env\Scripts\activate  # Windows

# Install in clean environment
pip install prompt-build-tool

# Check for conflicts
pip check

# Update all packages
pip install --upgrade pip setuptools wheel
```

### 🔐 Authentication Issues

#### Issue: "Invalid API key" errors
**Symptoms**:
- `AuthenticationError: Invalid API key`
- `401 Unauthorized` responses
- API calls failing consistently

**Diagnosis**:
```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Verify key format
pbt auth check
```

**Solutions**:
```bash
# Set API keys correctly
export ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
export OPENAI_API_KEY=sk-your-actual-key-here

# Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Test specific provider
pbt integrations test anthropic
pbt integrations test openai

# Refresh configuration
pbt config reload
```

#### Issue: "Rate limit exceeded"
**Symptoms**:
- `RateLimitError: Too many requests`
- Requests failing intermittently
- 429 HTTP status codes

**Solutions**:
```bash
# Use sequential processing
pbt test prompts/ --parallel=false

# Add delays between requests
pbt test prompts/ --delay=2

# Reduce batch size
pbt test prompts/ --batch-size=5

# Use local models for development
export OLLAMA_BASE_URL=http://localhost:11434
pbt test prompts/ --model=ollama
```

### 📁 File and Path Issues

#### Issue: "File not found" errors
**Symptoms**:
- `FileNotFoundError: No such file or directory`
- Commands failing to find prompt files
- Incorrect path resolution

**Diagnosis**:
```bash
# Check current directory
pwd
ls -la

# Verify file paths
find . -name "*.prompt.yaml"
find . -name "pbt.yaml"

# Check project structure
pbt status
```

**Solutions**:
```bash
# Use absolute paths
pbt test /full/path/to/prompts/my_prompt.yaml

# Navigate to project directory
cd /path/to/your/pbt/project
pbt test prompts/my_prompt.yaml

# Check file permissions
ls -la prompts/
chmod 644 prompts/*.yaml

# Initialize project if missing
pbt init . --force
```

#### Issue: YAML parsing errors
**Symptoms**:
- `YAMLError: could not parse file`
- Syntax errors in configuration files
- Invalid YAML structure

**Diagnosis**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('pbt.yaml'))"
python -c "import yaml; yaml.safe_load(open('prompts/my_prompt.yaml'))"

# Check file encoding
file prompts/my_prompt.yaml
```

**Solutions**:
```bash
# Fix YAML syntax
# Common issues:
# - Missing quotes around strings with special characters
# - Incorrect indentation (use spaces, not tabs)
# - Missing colons after keys

# Validate configuration
pbt config validate --strict

# Example fix:
# Wrong:
name: My-Prompt's Test
# Right:
name: "My-Prompt's Test"

# Use online YAML validator for complex files
# Copy file content to yamllint.com
```

### 🌐 Network and Connectivity Issues

#### Issue: Connection timeouts
**Symptoms**:
- `TimeoutError: Request timed out`
- Long delays before errors
- Intermittent connection failures

**Solutions**:
```bash
# Increase timeout
export HTTP_TIMEOUT=60
pbt test prompts/ --timeout=60

# Check network connectivity
ping api.anthropic.com
ping api.openai.com

# Use proxy if needed
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Test specific endpoints
curl -I https://api.anthropic.com/v1/messages
```

#### Issue: SSL/TLS errors
**Symptoms**:
- `SSLError: certificate verify failed`
- TLS handshake failures
- Certificate validation errors

**Solutions**:
```bash
# Update certificates
# macOS:
brew install ca-certificates

# Ubuntu:
sudo apt-get update && sudo apt-get install ca-certificates

# Check certificate bundle
python -c "import ssl; print(ssl.get_default_verify_paths())"

# Temporary workaround (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

### 💾 Database and Storage Issues

#### Issue: Database connection failures
**Symptoms**:
- `ConnectionError: Unable to connect to database`
- Supabase authentication failures
- PostgreSQL connection timeouts

**Diagnosis**:
```bash
# Test database connectivity
pbt integrations test supabase
pbt integrations test postgresql

# Check connection string
echo $DATABASE_URL
echo $SUPABASE_URL
```

**Solutions**:
```bash
# Verify credentials
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-anon-key
export DATABASE_URL=postgresql://user:pass@host:port/db

# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check firewall/network access
telnet your-db-host 5432

# Use connection pooling
export DATABASE_POOL_SIZE=10
export DATABASE_MAX_OVERFLOW=20
```

#### Issue: Vector database performance
**Symptoms**:
- Slow similarity searches
- High memory usage during vector operations
- Qdrant connection timeouts

**Solutions**:
```bash
# Optimize vector operations
pbt vector optimize --collection=prompts

# Reduce vector dimensions
export VECTOR_DIMENSIONS=512

# Use approximate search
pbt vector search --approximate=true

# Check Qdrant status
curl http://localhost:6333/health

# Restart Qdrant if needed
docker restart qdrant-container
```

### 🏃‍♂️ Performance Issues

#### Issue: Slow prompt testing
**Symptoms**:
- Tests taking very long to complete
- High CPU usage during evaluation
- Memory consumption growing over time

**Diagnosis**:
```bash
# Monitor resource usage
top -p $(pgrep -f pbt)
htop

# Check test performance
pbt test prompts/ --profile

# Analyze bottlenecks
pbt status --include-resources
```

**Solutions**:
```bash
# Enable caching
export MODEL_CACHE_ENABLED=true
export CACHE_TTL=3600

# Use parallel processing (if not rate limited)
pbt test prompts/ --parallel=true --workers=4

# Optimize prompt files
pbt optimize prompts/ --target=performance

# Clear cache if growing too large
pbt cache clear --older-than=7d

# Use local models for development
docker run -d -p 11434:11434 ollama/ollama
ollama pull llama2:7b
export OLLAMA_BASE_URL=http://localhost:11434
```

#### Issue: High memory usage
**Symptoms**:
- System becoming unresponsive
- Out of memory errors
- Swap usage increasing

**Solutions**:
```bash
# Reduce batch size
export BATCH_SIZE=5
pbt test prompts/ --batch-size=5

# Use streaming for large operations
pbt test prompts/ --stream=true

# Clear memory caches
pbt cache clear
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Monitor memory usage
pbt status --memory-usage
```

### 🔗 Integration Issues

#### Issue: Slack notifications not working
**Symptoms**:
- No messages appearing in Slack
- Webhook errors in logs
- Authentication failures

**Diagnosis**:
```bash
# Test Slack integration
pbt integrations test slack

# Check webhook URL
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  $SLACK_WEBHOOK_URL
```

**Solutions**:
```bash
# Verify Slack configuration
export SLACK_TOKEN=xoxb-your-token
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
export SLACK_CHANNEL=#pbt-notifications

# Test direct API call
pbt slack send "Test notification"

# Check bot permissions in Slack workspace
# Ensure bot has chat:write scope
```

#### Issue: Notion sync failures
**Symptoms**:
- Pages not syncing to Notion
- Authentication errors with Notion API
- Database operations failing

**Solutions**:
```bash
# Verify Notion integration
export NOTION_TOKEN=secret_your-integration-token
export NOTION_DATABASE_ID=your-database-id

# Test Notion connectivity
pbt integrations test notion

# Refresh Notion integration
pbt notion refresh-auth

# Check integration permissions in Notion
# Ensure integration has read/write access to databases
```

### 🚀 Deployment Issues

#### Issue: Render deployment failures
**Symptoms**:
- Build failures during deployment
- Service not starting correctly
- Environment variable issues

**Diagnosis**:
```bash
# Check deployment logs
pbt render logs --service-id=your-service-id

# Validate configuration
pbt deploy --dry-run --platform=render
```

**Solutions**:
```bash
# Verify Render configuration
export RENDER_API_KEY=your-api-key
export RENDER_SERVICE_ID=your-service-id

# Test deployment locally
docker build -t pbt-test .
docker run -p 8080:8080 pbt-test

# Check build logs
pbt render logs --build --service-id=your-service-id

# Update environment variables
pbt render env set ANTHROPIC_API_KEY=sk-ant-...
```

#### Issue: Fly.io deployment problems
**Symptoms**:
- App creation failures
- Scaling issues
- Health check failures

**Solutions**:
```bash
# Verify Fly.io setup
flyctl auth whoami
flyctl apps list

# Check app status
flyctl status --app your-app-name

# View logs
flyctl logs --app your-app-name

# Scale app
flyctl scale count 1 --app your-app-name

# Deploy with verbose output
pbt deploy --platform=fly.io --verbose
```

## Advanced Troubleshooting

### Debug Mode Configuration
```bash
# Enable comprehensive debugging
export LOG_LEVEL=DEBUG
export TRACE_ENABLED=true
export METRICS_ENABLED=true

# Component-specific debugging
export PBT_CORE_DEBUG=true
export PBT_INTEGRATIONS_DEBUG=true
export PBT_EVALUATION_DEBUG=true

# Save debug output
pbt test prompts/ --debug > debug.log 2>&1
```

### Performance Profiling
```bash
# Profile memory usage
python -m memory_profiler -m pbt test prompts/

# Profile CPU usage
python -m cProfile -o pbt_profile.prof -m pbt test prompts/
python -c "import pstats; pstats.Stats('pbt_profile.prof').sort_stats('cumulative').print_stats(10)"

# Network profiling
export HTTP_DEBUG=true
pbt test prompts/ --trace-requests
```

### Environment Debugging
```bash
# Check all environment variables
env | grep -E "(PBT|ANTHROPIC|OPENAI|SUPABASE)"

# Validate Python environment
python -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)
import pbt
print('PBT version:', pbt.__version__)
print('PBT location:', pbt.__file__)
"

# Check system resources
df -h  # Disk usage
free -h  # Memory usage
lscpu  # CPU information
```

### Configuration Validation
```bash
# Validate all configuration files
find . -name "*.yaml" -exec pbt config validate {} \;

# Check project structure
pbt project validate --strict

# Verify integration setup
for integration in anthropic openai supabase slack discord; do
  echo "Testing $integration..."
  pbt integrations test $integration
done
```

## Getting Help

### Before Asking for Help
1. **Check this troubleshooting guide** for common solutions
2. **Search existing issues** on GitHub
3. **Enable debug logging** and collect relevant information
4. **Create a minimal reproduction** of the problem

### Information to Include
When reporting issues, always include:

```bash
# System information
pbt --version
python --version
uname -a  # or equivalent on Windows

# Error details
pbt logs --tail=50 --level=error

# Configuration (without secrets)
pbt config show --sanitized

# Reproduction steps
# Minimal example that reproduces the issue
```

### Support Channels
- 🐛 **GitHub Issues**: https://github.com/your-org/pbt/issues
- 💬 **GitHub Discussions**: https://github.com/your-org/pbt/discussions
- 📧 **Email Support**: support@pbt.dev
- 📱 **Discord Community**: https://discord.gg/pbt

### Enterprise Support
For enterprise customers:
- 🎯 **Priority Support**: enterprise@pbt.dev
- 📞 **Phone Support**: Available during business hours
- 👥 **Dedicated Slack Channel**: For enterprise customers
- 🔧 **Custom Integration Help**: Available for enterprise plans

## Prevention and Best Practices

### Regular Maintenance
```bash
# Weekly maintenance routine
pbt cache clear --older-than=7d
pbt logs rotate
pbt config validate
pbt integrations health-check

# Monthly maintenance
pip install --upgrade prompt-build-tool
pbt project optimize
pbt database vacuum  # if using local database
```

### Monitoring Setup
```bash
# Set up monitoring
export METRICS_ENABLED=true
export HEALTH_CHECK_ENABLED=true

# Configure alerts
pbt alerts configure --email=admin@company.com
pbt alerts add --type=error --threshold=10

# Monitor resource usage
pbt monitor start --interval=60
```

### Backup Strategy
```bash
# Backup project data
pbt backup create --include=prompts,tests,evaluations
pbt backup upload --storage=s3 --bucket=my-backups

# Scheduled backups
crontab -e
# Add: 0 2 * * * /usr/local/bin/pbt backup create --auto-cleanup
```

Remember: When in doubt, start with the basics - check your API keys, validate your configuration, and ensure you have network connectivity. Most issues stem from these fundamental requirements.