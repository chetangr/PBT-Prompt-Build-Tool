# 🚀 Prompt Build Tool (PBT)

**Infrastructure-grade prompt engineering for AI teams working across LLMs, multimodal models, and agent workflows.**

PBT is an open-source prompt operating system designed for teams that need **dbt + Terraform** for LLM prompts. It works across Claude, GPT-4, Mistral, Azure, Ollama with a Visual Prompt IDE + CLI for authoring, diffing, testing, and deploying prompts.

---

## ✨ Key Features

🎯 **Core Infrastructure**
- ✅ Prompt Pack bundling & deployment
- ✅ Multi-agent orchestration support  
- ✅ Prompt-aware chunking + SEO optimization
- ✅ Claude + OpenAI prompt generation and eval
- ✅ Visual, audio, and image prompt preview
- ✅ Supabase, Firebase, HuggingFace deploy targets

🛠️ **Prompt Lifecycle Tooling**
- ✅ AI-powered prompt generation
- ✅ Cross-model testing & comparison
- ✅ Claude-based evaluation judge
- ✅ Visual diff viewer for prompt changes
- ✅ Batch test runners with pass/fail metrics
- ✅ SEO optimization for prompt discoverability

💼 **Enterprise Features**
- ✅ Supabase Auth + GitHub OAuth
- ✅ Role-based access control
- ✅ Stripe-powered PromptPack marketplace
- ✅ Export to Notion, CSV, Markdown
- ✅ Slack/Discord notification bots
- ✅ Weekly email reports + webhook triggers
- ✅ Usage analytics & performance tracking

🎨 **Developer Experience**
- ✅ React-based Visual Prompt IDE
- ✅ CLI for CI/CD integration
- ✅ Real-time prompt rendering & preview
- ✅ Multi-language support (i18n)
- ✅ Badge system for GDPR, safety compliance
- ✅ Version control integration

---

## 🏗️ Architecture

```
📁 PBT Infrastructure
├── 🖥️ Backend (FastAPI)
│   ├── /api/promptgen     → AI prompt generation
│   ├── /api/testgen       → Test case generation  
│   ├── /api/evals         → Claude evaluation judge
│   ├── /api/promptpacks   → Pack management
│   ├── /api/auth          → Supabase + GitHub OAuth
│   ├── /api/export        → Notion/CSV/Markdown export
│   └── /api/payment       → Stripe marketplace
├── 🎨 Frontend (React + Tailwind)
│   ├── PromptEditor       → Visual editing + diff
│   ├── PromptGenerator    → AI-powered creation
│   ├── PromptGallery      → Browse & search
│   ├── EvalChart          → Analytics dashboard
│   └── Marketplace       → Commercial prompt store
├── 🗄️ Database (Supabase)
│   ├── prompt_packs       → Versioned prompt storage
│   ├── evaluations        → Test results & scores
│   ├── analytics_events   → Usage tracking
│   └── auth integration   → User management
└── 🔧 CLI (Python)
    └── pbt command        → CI/CD integration
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/prompt-build-tool.git
cd prompt-build-tool

# Install globally (no virtual environment needed)
./install_system.sh
```

### 2. Get API Keys (Required)

```bash
# Minimum setup - just get this one key:
# ANTHROPIC_API_KEY from https://console.anthropic.com

# Optional for full features:
# OPENAI_API_KEY from https://platform.openai.com/api-keys
# SUPABASE_URL + SUPABASE_KEY from https://supabase.com

# See API_KEYS.md for detailed setup instructions
```

### 3. Create Your First Project

```bash
# Create and initialize project
mkdir my-prompts && cd my-prompts
pbt init --name "My Prompts"

# Add your API key
cp .env.example .env
nano .env  # Add ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Generate Your First Prompt

```bash
# Generate a prompt using AI
pbt generate --goal "Summarize customer feedback into actionable insights"

# Test the generated prompt
pbt test customer_feedback_summarizer.yaml

# Compare across models (requires OPENAI_API_KEY)
pbt compare --prompt "Hello world" --models claude gpt-4
```

### 5. Optional: Start Web Server

```bash
# Start the full web interface (requires SUPABASE keys)
pbt serve --port 8000

# Visit http://localhost:8000 for web UI
```

---

## 🔧 CLI Commands

```bash
# Project Management
pbt init --name my-prompts
pbt deploy --provider supabase

# Prompt Generation  
pbt generate-prompt --goal "Generate product descriptions" --model claude
pbt optimize my_prompt.yaml

# Testing & Evaluation
pbt test my_prompt.yaml --num-tests 10
pbt eval --input test_cases.json --model claude
pbt render --compare gpt-4 claude mistral --prompt "Hello world"

# Data Management
pbt export --format csv --prompts tweet_summarizer,product_gen
pbt import --source notion --database-id abc123
```

---

## 📊 Supported Models

| Provider | Models | Status |
|----------|--------|--------|
| **Anthropic** | Claude 3 Sonnet/Haiku/Opus | ✅ Full Support |
| **OpenAI** | GPT-4, GPT-4 Turbo | ✅ Full Support |
| **Mistral** | Mistral Large/Medium | 🚧 Coming Soon |
| **Azure OpenAI** | GPT-4, GPT-3.5 | 🚧 Coming Soon |
| **Ollama** | Llama 2, Code Llama | 🚧 Coming Soon |
| **Multimodal** | Midjourney, Runway, Whisper | 🚧 Coming Soon |

---

## 🎯 Use Cases

### **Enterprise Prompt Management**
- Centralized prompt version control
- Team collaboration with review workflows  
- Compliance tracking (GDPR, safety badges)
- Usage analytics across teams

### **AI Product Development**
- Rapid prompt prototyping & iteration
- A/B testing across model providers
- Performance benchmarking & optimization
- Production deployment pipelines

### **Research & Education**
- Prompt engineering experimentation
- Model comparison studies
- Educational prompt libraries
- Academic collaboration tools

---

## 🏪 PromptPack Marketplace

**Discover, buy, and sell high-quality prompt templates**

- 🔍 **Browse by Category**: Content, Analysis, Creative, Technical
- ⭐ **Community Ratings**: Star system + detailed reviews  
- 💰 **Flexible Pricing**: Free, paid, and subscription models
- 📈 **Creator Analytics**: Revenue tracking + download metrics
- 🔒 **Quality Assurance**: Automated testing + human review

Popular PromptPacks:
- **Tweet Summarizer** - Decode sarcasm & extract meaning
- **Code Documentor** - Auto-generate function documentation  
- **Email Responder** - Professional email composition
- **Travel Caption Gen** - Instagram-ready travel posts

---

## 📈 Analytics & Monitoring

### **Evaluation Metrics**
- **Claude Judge Scoring**: 1-10 quality ratings with explanations
- **Pass/Fail Rates**: Based on custom criteria
- **Performance Trends**: Track improvement over time
- **Cross-Model Comparison**: See which models work best

### **Usage Analytics**  
- **Prompt Downloads**: Track popular templates
- **User Engagement**: Session duration, feature usage
- **Revenue Metrics**: Marketplace sales & subscriptions
- **Error Monitoring**: Failed evaluations & API issues

### **Reporting**
- **Weekly Digest**: Email summaries of activity
- **Custom Dashboards**: Filter by team, project, timeframe
- **Export Options**: CSV, JSON, direct to Notion
- **Webhook Integration**: Real-time notifications

---

## 🔐 Security & Compliance

### **Authentication**
- Supabase Auth with GitHub OAuth
- JWT token-based API access
- Row Level Security (RLS) policies
- Multi-tenant data isolation

### **Data Protection**
- SOC 2 compliant infrastructure (via Supabase)
- End-to-end encryption for sensitive prompts
- GDPR compliance tools & badges
- Audit logs for all operations

### **Access Control**
- Role-based permissions (viewer, editor, admin)
- Team-based prompt sharing
- Private/public prompt visibility
- API key management

---

## 🌍 Roadmap

### **Q1 2024**
- [ ] Ollama + local LLM support
- [ ] Advanced multimodal prompt support  
- [ ] Claude-native agent workflows
- [ ] Enhanced marketplace features

### **Q2 2024**
- [ ] Prompt changelog visualization
- [ ] Advanced A/B testing framework
- [ ] Enterprise SSO integration  
- [ ] Custom evaluation metrics

### **Q3 2024**
- [ ] Prompt security policy API
- [ ] Integration with popular IDEs
- [ ] Advanced analytics & ML insights
- [ ] White-label marketplace options

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
git clone https://github.com/your-org/prompt-build-tool.git
cd prompt-build-tool
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your development keys
python -m pytest  # Run tests
```

### **Areas We Need Help**
- 🧪 Test coverage expansion
- 🎨 UI/UX improvements  
- 📚 Documentation & tutorials
- 🔌 New LLM provider integrations
- 🌍 Internationalization (i18n)

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[CLI Reference](docs/CLI_REFERENCE.md)** - Complete command documentation  
- **[API Docs](http://localhost:8000/docs)** - Interactive API explorer
- **[Architecture Overview](docs/OVERVIEW.md)** - System design & concepts

---

## 📞 Support

- **📧 Email**: support@promptbuildtool.com
- **💬 Discord**: [Join our community](https://discord.gg/prompt-build-tool)
- **🐛 Issues**: [GitHub Issues](https://github.com/your-org/prompt-build-tool/issues)
- **📖 Docs**: [Documentation Site](https://docs.promptbuildtool.com)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for the AI community**

*Making prompt engineering as robust as traditional software development.*