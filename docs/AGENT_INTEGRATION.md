# 🤖 Agent Integration Guide

## Using PBT with Existing Agent Workflows

### Quick Integration Steps

1. **Convert Agent Prompts to PBT Format**
```bash
# Initialize PBT in your agent project
cd your-agent-project
pbt init --name "Agent Prompts"

# Convert existing prompts to YAML
pbt generate --goal "Your agent's purpose" --save agent_prompt.yaml
```

2. **Establish Testing Pipeline**
```bash
# Create test cases for your agent prompts
pbt test agent_prompt.yaml --generate-tests 10
pbt eval --model claude --input test_cases.json
```

3. **Version Control Integration**
```bash
# Add to your existing Git workflow
git add agent_prompts/
git commit -m "feat: migrate agent prompts to PBT format"
```

### Common Agent Integration Patterns

#### **Pattern 1: Single Agent with Multiple Prompts**
```yaml
# agent_prompts/data_extractor.yaml
name: "Data Extraction Agent"
prompts:
  - name: "parse_email"
    template: |
      Extract structured data from: {{ email }}
      Format as JSON with fields: sender, subject, intent
  
  - name: "validate_extraction"
    template: |
      Validate this extraction: {{ extracted_data }}
      Return validation_score (0-1) and corrections
```

#### **Pattern 2: Multi-Agent Orchestration**
```yaml
# agent_prompts/workflow.yaml
name: "Customer Support Workflow"
agents:
  - name: "classifier"
    model: "claude"
    prompt: "Classify customer inquiry: {{ message }}"
  
  - name: "responder"
    model: "gpt-4"
    prompt: "Generate response for {{ intent }}: {{ original_message }}"
  
  - name: "reviewer"
    model: "claude"
    prompt: "Review response quality: {{ response }}"
```

#### **Pattern 3: Prompt Chain Testing**
```bash
# Test entire agent workflow
pbt test-chain workflow.yaml \
  --input "Customer complaint about billing" \
  --trace-execution \
  --models claude,gpt-4
```

### Code Integration Examples

#### **Python Agent Integration**
```python
# your_agent.py
import pbt
from pbt.core import PromptPack

class MyAgent:
    def __init__(self):
        # Load prompts from PBT
        self.prompts = PromptPack.load("agent_prompts/")
    
    def process_email(self, email_content):
        # Use PBT-managed prompt
        result = self.prompts.run("parse_email", 
                                  email=email_content,
                                  model="claude")
        return result
    
    def validate_extraction(self, data):
        return self.prompts.run("validate_extraction",
                                extracted_data=data,
                                model="gpt-4")
```

#### **JavaScript/Node.js Integration**
```javascript
// agent.js
const pbt = require('pbt-js');

class EmailAgent {
    constructor() {
        this.prompts = pbt.loadPack('./agent_prompts/');
    }
    
    async classifyEmail(email) {
        return await this.prompts.run('email_classifier', {
            email_content: email,
            model: 'claude'
        });
    }
}
```

### CI/CD Integration

#### **GitHub Actions Example**
```yaml
# .github/workflows/agent-prompts.yml
name: Test Agent Prompts
on: [push, pull_request]

jobs:
  test-prompts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install PBT
        run: pip install prompt-build-tool
      
      - name: Test Agent Prompts
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          pbt test agent_prompts/ --format junit
          pbt compare --models claude,gpt-4 --save-report
```

### Advanced Agent Patterns

#### **A/B Testing Agent Prompts**
```bash
# Compare prompt versions in production
pbt compare \
  --prompt-a agent_prompts/v1/classifier.yaml \
  --prompt-b agent_prompts/v2/classifier.yaml \
  --test-data customer_emails.json \
  --metrics accuracy,latency,cost
```

#### **Prompt Performance Monitoring**
```python
# monitoring.py
import pbt

# Track agent prompt performance
pbt.monitor("email_classifier", 
           input_data=email,
           output=result,
           model="claude",
           metrics=["accuracy", "latency"])
```

#### **Prompt Marketplace Integration**
```bash
# Share successful agent prompts
pbt publish email_agent \
  --marketplace \
  --price 5.00 \
  --description "Production-tested email classification"

# Install community agent prompts
pbt install customer_support_pack --from-marketplace
```

### Migration Checklist

- [ ] Convert existing prompts to PBT YAML format
- [ ] Set up test cases for each agent prompt
- [ ] Integrate PBT testing into CI/CD pipeline
- [ ] Update agent code to use PBT prompt loading
- [ ] Establish prompt versioning strategy
- [ ] Configure monitoring for prompt performance
- [ ] Document prompt dependencies and requirements

### Best Practices

1. **Modular Prompts**: Break complex agent logic into testable prompt components
2. **Version Everything**: Track prompt changes with semantic versioning
3. **Test Continuously**: Run prompt tests on every code change
4. **Monitor Performance**: Track accuracy, latency, and cost metrics
5. **Share Knowledge**: Use marketplace for proven agent patterns