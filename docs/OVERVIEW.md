# 📚 Prompt Build Tool (PBT) – Overview & Use Cases

## 🧭 Why It Was Built

Prompt engineering has become a critical discipline — but it's chaotic:
- Prompts are shared in Notion docs or chat messages
- There's no version control, diffing, or testing
- Teams can't reuse or deploy prompts like code

**PBT solves this** by treating prompts like infrastructure:
- Modular, testable, version-controlled
- Deployable like apps
- Visual and CLI-first for cross-functional teams

---

## 🧩 Use Cases

### 1. 🛠️ LLM Feature Prototyping
Use PBT to design, test, and compare prompts before shipping into an app.

Example:
```yaml
goal: "Summarize sarcastic tweets"
model: gpt-4
template: |
  Detect sarcasm in: "{{ tweet }}"
```

### 2. 🧪 Prompt Evaluation
Run prompts against real test data. Evaluate output correctness, tone, format.

### 3. 🧳 PromptPack Deployment
Package prompts into reusable `packs` for deployment across environments.

### 4. 🧠 Prompt Agents
Orchestrate multi-prompt workflows (e.g., summarizer → classifier → explainer).

### 5. 🖼️ Visual + Multimodal Prompt Testing
Compare outputs across Google Veo, Midjourney, Claude for the same input.

---

## 🆚 GitHub Models vs PBT

| Feature                        | GitHub Models          | Prompt Build Tool (PBT)     |
|-------------------------------|------------------------|-----------------------------|
| Prompt Versioning             | ✅ Git-integrated      | ✅ Git-compatible & YAML    |
| Prompt Testing                | ✅ In-repo evaluators  | ✅ CLI + UI test harness    |
| Model Comparison              | ✅ Visual Playground    | ✅ CLI + visual viewer      |
| Deployment                    | ❌ Manual via repo      | ✅ Deploy packs via CLI     |
| Prompt Packs                  | ❌ Not supported        | ✅ Modularized + testable   |
| Agent Support                 | ❌                     | ✅ Multi-agent workflows    |
| Multimodal Prompting          | ⚠️ LLMs only           | ✅ Visual / video supported |
| GitHub Lock-in                | ✅ Yes                 | ❌ Platform-agnostic        |
| Offline / Edge                | ❌ Cloud only          | ✅ Ollama, local run ready  |

---

## 💡 Target Audience

- AI engineers and PMs
- Designers crafting multimodal prompts
- Researchers comparing models
- Teams building AI-powered apps
- Enterprises needing compliant, testable prompt workflows
