# CLAUDE_VALIDATE.md – Prompt Build Tool (PBT) Feature Validation

This file helps Claude Code verify implementation status of key PBT features.

## ✅ Authentication & Access Control
- [x] Supabase user authentication (`db/auth.py`)
- [x] GitHub OAuth callback handler (`routes/github_oauth.py`)
- [x] Frontend AuthContext and Login form

## ✅ LLM Integration & Runtime
- [x] Supports OpenAI, Claude, Azure via `llms/config.py`
- [x] Selectable `LLM_PROVIDER` via `.env`

## ✅ Prompt Features
- [x] Prompt Packs (reusable prompt modules)
- [x] Multi-agent orchestration stub
- [x] Prompt-aware vector chunking & embedding optimization
- [x] Prompt diff viewer (`PromptDiffViewer.jsx`)
- [x] SEO + badge metadata in YAML schema

## ✅ Prompt UI/UX
- [x] Visual prompt editor (`PromptEditor.jsx`)
- [x] Prompt generator (`PromptGenerator.jsx`)
- [x] Input runner (`PromptRunner.jsx`)
- [x] Model output gallery (`PromptGallery.jsx`)
- [x] Dashboard view with user prompt list (`Dashboard.jsx`)

## ✅ CLI Commands (implemented or stubbed)
- ✅ `pbt init` - Initialize a new PBT project
- ✅ `pbt generate --goal "<goal>"` - Generate prompts using AI
- ✅ `pbt gentests <prompt_file>` - Generate test cases for prompts
- ✅ `pbt render <prompt> --compare "model1,model2"` - Render and compare outputs
- ✅ `pbt eval <prompt_folder>` - Evaluate prompt quality metrics
- ✅ `pbt badge --add GDPR-compliant` - Manage compliance badges
- ✅ `pbt i18n <prompt> --languages en,fr` - Internationalize prompts
- ✅ `pbt pack build` - Build prompt packs
- ✅ `pbt deploy --provider supabase` - Deploy to cloud providers
- ✅ `pbt import --source notion` - Import from external sources
- ✅ `pbt convert <file>` - Convert Python agents to YAML format

## ✅ Backend API Routes
- `/api/promptgen`
- `/api/testgen`
- `/api/seo`
- `/api/auth/login`
- `/api/auth/github/callback`

## 🧱 Requirements to Integrate
- `.env` must include OpenAI, Claude, Azure, Supabase, GitHub OAuth vars
- Frontend must set `Authorization` header from token
- Supabase tables must match schema in `db/supabase_schema.sql`

This spec helps Claude automatically evaluate whether all PBT features are implemented and how to expand them.
