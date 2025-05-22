# 🧠 Mega Prompt: Build Prompt Build Tool (PBT)

You are Claude Code, an advanced agent tasked with building a complete open-source system called Prompt Build Tool (PBT). This is like dbt + Terraform + LangChain for prompt engineering.

---

## 🎯 Core Goal

Build an infrastructure framework for creating, testing, comparing, and deploying prompt templates (text, audio, visual) that work across LLMs and multimodal models. It must support:

- Prompt Packs (reusable prompt modules)
- Prompt lifecycle tooling (generate, test, diff, eval, deploy)
- Supabase Auth, GitHub OAuth
- Visual and CLI interfaces
- Claude + OpenAI + Mistral + Ollama runtime selectors
- Cross-model output comparison
- Prompt optimizer, badges, i18n
- Image + video + audio prompt support
- Claude-based eval judge
- Slack/Discord notification bots
- Export prompts to Notion, CSV, Markdown
- Stripe-powered PromptPack store
- Weekly email report + webhook triggers

---

## 📂 Directories

- `/backend/` – FastAPI with routes:
  - `promptgen.py`, `testgen.py`, `seo.py`, `claude_score.py`, `analytics.py`, `stripe.py`, `stars.py`, `export.py`
- `/backend/db/` – Supabase schema + auth + seed script
- `/backend/tasks/` – `weekly_digest.py`
- `/backend/bots/` – `webhook_notifier.py`
- `/playground/ui/` – React components:
  - `PromptEditor`, `PromptGenerator`, `PromptGallery`, `PromptPackExplorer`, `PromptPackPublisher`, `EvalChart`, `PromptPackMarketplace`
- `/public/` – `index.html` landing page

---

## 🔧 CLI Commands

```bash
pbt init
pbt generate-prompt --goal "Summarize sarcastic tweets"
pbt test tweet_summarizer.prompt.yaml
pbt render --compare gpt-4 claude mistral
pbt eval --input test.json
pbt optimize tweet_summarizer.prompt.yaml
pbt badge --add GDPR
pbt i18n --languages en,fr
pbt pack build
pbt deploy --provider supabase
pbt import --source notion
```

---

## 🧠 Instructions for Claude Code

- Use FastAPI for backend
- Use Supabase for auth + prompt table
- Use Tailwind + React for frontend
- Use `.prompt.yaml` structure to define prompt packs
- Use Chart.js for EvalChart
- Use Stripe API for checkout
- Use Discord/Slack webhooks
- Use `markdownify` for Markdown export
- Assume all API keys passed in `.env`
- Use Claude to judge prompt output via `/api/evals/judge`

---

## 📊 Output Checklist

- ✅ Seed data file (`seed_prompts.py`)
- ✅ Auth and token wiring
- ✅ Claude/OpenAI integration via config
- ✅ UI playground for editing + diff + preview
- ✅ PromptPack publishing, rating, buying
- ✅ Stripe payment checkout
- ✅ Weekly digest + webhook
- ✅ Export endpoints
- ✅ Landing page in `public/index.html`
