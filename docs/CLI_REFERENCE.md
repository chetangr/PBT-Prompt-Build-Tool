# 📘 PBT CLI Reference Guide

This is the complete command-line reference for Prompt Build Tool (PBT).

---

## 🛠️ Core Commands

### `pbt init`
Initialize a new prompt project folder.

### `pbt generate-prompt --goal "<goal>"`
Generate a prompt YAML structure using an LLM.

### `pbt test <prompt_file>`
Run test cases defined in the prompt YAML.

### `pbt test --batch <file.jsonl>`
Run batch tests on inputs from a JSONL file.

### `pbt render <prompt> --compare <model1> <model2>`
Compare output across multiple models.

### `pbt eval <prompt_folder>`
Run evaluations on prompt results using similarity or pass/fail metrics.

---

## 🧠 Prompt Optimization & Analysis

### `pbt optimize <prompt_file>`
Suggest shorter or more efficient prompt alternatives.

### `pbt badge <prompt_file> --add <badge>`
Apply metadata badges like `secure`, `GDPR-compliant`, or `reviewed`.

### `pbt i18n <prompt_file> --languages en,fr,hi`
Translate and validate prompt in multiple languages.

---

## 🧳 Prompt Packs & Deployment

### `pbt pack build <folder>`
Create a deployable Prompt Pack from prompt folder.

### `pbt deploy <prompt> --provider <target>`
Deploy the prompt module to a cloud platform:
- `supabase`
- `firebase`
- `huggingface`
- `replicate`

---

## 🌍 Imports & Extensions

### `pbt import --source <tool> --page "<name>"`
Import prompts from:
- Notion
- Slack
- Airtable

---

## 💡 Examples

```bash
pbt generate-prompt --goal "Summarize sarcastic tweets"
pbt render tweet_summarizer --compare openai/gpt-4 claude-3
pbt deploy tweet_summarizer --provider supabase
```
