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
- `pbt init`
- `pbt generate-prompt --goal "<goal>"`
- `pbt testgen <prompt_file>`
- `pbt render <prompt> --compare <model1> <model2>`
- `pbt eval <prompt_folder>`
- `pbt badge --add GDPR-compliant`
- `pbt i18n <prompt> --languages en,fr`
- `pbt pack build`
- `pbt deploy --provider supabase`
- `pbt import --source notion`

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
