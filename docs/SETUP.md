# PBT Setup Guide

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-org/prompt-build-tool.git
cd prompt-build-tool
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL schema in `backend/db/schema.sql`
3. Enable GitHub OAuth in Supabase Auth settings
4. Update your `.env` with Supabase credentials

### 4. Run the Application

```bash
# Backend API
cd backend
uvicorn main:app --reload --port 8000

# Frontend (if using React)
cd playground
npm install
npm start
```

## 📋 Required API Keys

### LLM Providers
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com)
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com)

### Payments (Optional)
- **Stripe**: Get keys from [dashboard.stripe.com](https://dashboard.stripe.com)

### Notifications (Optional)
- **Slack**: Create webhook at [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)
- **Discord**: Create webhook in Discord server settings

## 🗄️ Database Schema

The application uses Supabase (PostgreSQL) with the following main tables:

- `profiles` - User profiles extending Supabase auth
- `prompt_packs` - Main prompt storage
- `evaluations` - Prompt evaluation results
- `prompt_stars` - User favorites
- `test_cases` - Test cases for prompts
- `analytics_events` - Usage analytics

## 🔧 Configuration

### Supabase Setup

1. **Create Tables**: Run `backend/db/schema.sql` in Supabase SQL editor
2. **Enable RLS**: Row Level Security is enabled by default
3. **Auth Providers**: Configure GitHub OAuth in Supabase dashboard
4. **API Keys**: Copy your project URL and anon key to `.env`

### LLM Configuration

The system supports multiple LLM providers:

```python
# backend/llms/config.py
models = {
    "claude": "claude-3-sonnet-20240229",
    "gpt-4": "gpt-4",
    "mistral": "mistral-large-latest"  # When available
}
```

### Stripe Integration

For PromptPack marketplace:

1. Create Stripe account
2. Set up products and prices
3. Configure webhooks for payment processing
4. Add Stripe keys to `.env`

## 📦 CLI Commands

The PBT CLI supports these commands:

```bash
# Initialize project
pbt init

# Generate prompts
pbt generate-prompt --goal "Summarize tweets" --model claude

# Test prompts
pbt test tweet_summarizer.prompt.yaml

# Compare models
pbt render --compare gpt-4 claude mistral

# Run evaluations
pbt eval --input test.json

# Optimize prompts
pbt optimize tweet_summarizer.prompt.yaml

# Deploy
pbt deploy --provider supabase
```

## 🎨 UI Components

React components are in `playground/ui/`:

- `PromptEditor` - Main editing interface
- `PromptGenerator` - AI-powered prompt generation
- `PromptGallery` - Browse and search prompts
- `PromptPackMarketplace` - Commercial prompt store
- `EvalChart` - Analytics and evaluation results

## 📊 Analytics & Monitoring

### Evaluation Metrics
- Score (1-10) using Claude as judge
- Pass/fail rate based on criteria
- Performance trends over time
- Model comparison results

### Usage Analytics
- Prompt downloads and usage
- User engagement metrics
- Popular prompt categories
- Revenue tracking (if using Stripe)

## 🔐 Security

### Authentication
- Supabase Auth with GitHub OAuth
- JWT tokens for API access
- Row Level Security (RLS) for data protection

### API Security
- Rate limiting (recommended: nginx/cloudflare)
- Input validation and sanitization
- SQL injection protection via Supabase
- Environment variable protection

## 📧 Notifications

### Webhook Integration
Configure webhooks for:
- New prompt pack published
- Evaluation complete
- Weekly digest reports
- Payment notifications

### Email Digest
Weekly summary emails include:
- New prompts created
- Evaluation statistics
- Top performing prompts
- User activity metrics

## 🚀 Deployment

### Development
```bash
uvicorn backend.main:app --reload --port 8000
```

### Production
```bash
# Using Docker
docker build -t pbt-api .
docker run -p 8000:8000 pbt-api

# Using systemd service
sudo systemctl enable pbt-api
sudo systemctl start pbt-api
```

### Environment Variables
Ensure all required environment variables are set in production:
- Database credentials
- API keys for LLM providers
- Webhook URLs
- SMTP configuration for emails

## 🧪 Testing

Run the test suite:
```bash
pytest backend/tests/
```

Test coverage:
```bash
pytest --cov=backend backend/tests/
```

## 📚 API Documentation

Once running, visit:
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-org/pbt/issues)
- Community: [Discord](https://discord.gg/your-server)