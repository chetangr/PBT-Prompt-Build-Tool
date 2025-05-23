# 🔗 ref() Function Use Cases in PBT

The `ref()` function in PBT enables prompt dependencies, creating a directed acyclic graph (DAG) of prompt execution. This document outlines practical use cases and patterns.

## 📋 Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Common Use Cases](#common-use-cases)
3. [Real-World Examples](#real-world-examples)
4. [Best Practices](#best-practices)
5. [Anti-Patterns](#anti-patterns)

## 📝 Basic Syntax

```yaml
# prompts/my_prompt.yaml
name: my_prompt
depends_on:
  - ref('upstream_prompt_1')
  - ref('upstream_prompt_2')
```

## 🎯 Common Use Cases

### 1. Data Pipeline Pattern

**Use Case**: Sequential data processing where each step refines the previous output.

```yaml
# prompts/data_extractor.yaml
name: data_extractor
description: Extract structured data from raw text
variables:
  - raw_text
template: |
  Extract key information from: {{ raw_text }}
  Return as JSON with fields: name, date, amount

---
# prompts/data_validator.yaml
name: data_validator
depends_on:
  - ref('data_extractor')
variables:
  - extracted_data
template: |
  Validate the following data: {{ extracted_data }}
  Check for: missing fields, invalid formats, business rules

---
# prompts/data_enricher.yaml
name: data_enricher
depends_on:
  - ref('data_validator')
variables:
  - validated_data
template: |
  Enrich data with additional context: {{ validated_data }}
  Add: category classification, risk scores, metadata
```

### 2. Multi-Stage Analysis Pattern

**Use Case**: Complex analysis requiring multiple specialized prompts.

```yaml
# prompts/sentiment_analyzer.yaml
name: sentiment_analyzer
description: Basic sentiment analysis
variables:
  - text
template: |
  Analyze sentiment: {{ text }}
  Return: positive/negative/neutral with confidence

---
# prompts/emotion_detector.yaml
name: emotion_detector
depends_on:
  - ref('sentiment_analyzer')
variables:
  - text
  - sentiment_result
template: |
  Given sentiment {{ sentiment_result }}, detect emotions in: {{ text }}
  Identify: joy, anger, fear, surprise, sadness

---
# prompts/insight_generator.yaml
name: insight_generator
depends_on:
  - ref('sentiment_analyzer')
  - ref('emotion_detector')
variables:
  - sentiment_data
  - emotion_data
template: |
  Generate actionable insights from:
  Sentiment: {{ sentiment_data }}
  Emotions: {{ emotion_data }}
```

### 3. Content Generation Pipeline

**Use Case**: Multi-stage content creation with quality checks.

```yaml
# prompts/content_outliner.yaml
name: content_outliner
description: Create content outline
variables:
  - topic
  - audience
template: |
  Create outline for {{ topic }} targeting {{ audience }}

---
# prompts/content_writer.yaml
name: content_writer
depends_on:
  - ref('content_outliner')
variables:
  - outline
  - tone
template: |
  Write content based on outline: {{ outline }}
  Tone: {{ tone }}

---
# prompts/content_reviewer.yaml
name: content_reviewer
depends_on:
  - ref('content_writer')
variables:
  - content
  - guidelines
template: |
  Review content: {{ content }}
  Check against guidelines: {{ guidelines }}

---
# prompts/seo_optimizer.yaml
name: seo_optimizer
depends_on:
  - ref('content_reviewer')
variables:
  - reviewed_content
  - keywords
template: |
  Optimize for SEO: {{ reviewed_content }}
  Target keywords: {{ keywords }}
```

### 4. Decision Support System

**Use Case**: Multi-criteria decision making with various analysis stages.

```yaml
# prompts/risk_assessor.yaml
name: risk_assessor
variables:
  - proposal
template: |
  Assess risks in: {{ proposal }}
  Categorize by: financial, operational, reputational

---
# prompts/opportunity_analyzer.yaml
name: opportunity_analyzer
variables:
  - proposal
template: |
  Identify opportunities in: {{ proposal }}
  Consider: market potential, competitive advantage

---
# prompts/recommendation_engine.yaml
name: recommendation_engine
depends_on:
  - ref('risk_assessor')
  - ref('opportunity_analyzer')
variables:
  - risk_assessment
  - opportunity_analysis
template: |
  Generate recommendations based on:
  Risks: {{ risk_assessment }}
  Opportunities: {{ opportunity_analysis }}
```

## 🌟 Real-World Examples

### Example 1: Customer Support Automation

```yaml
# prompts/ticket_classifier.yaml
name: ticket_classifier
description: Classify support tickets
variables:
  - ticket_content
template: |
  Classify ticket: {{ ticket_content }}
  Categories: billing, technical, feature_request, complaint

---
# prompts/urgency_scorer.yaml
name: urgency_scorer
depends_on:
  - ref('ticket_classifier')
variables:
  - ticket_content
  - classification
template: |
  Score urgency (1-10) for {{ classification }} ticket:
  {{ ticket_content }}

---
# prompts/response_generator.yaml
name: response_generator
depends_on:
  - ref('ticket_classifier')
  - ref('urgency_scorer')
variables:
  - ticket_content
  - classification
  - urgency_score
template: |
  Generate response for {{ classification }} ticket (urgency: {{ urgency_score }}):
  {{ ticket_content }}

---
# prompts/escalation_checker.yaml
name: escalation_checker
depends_on:
  - ref('urgency_scorer')
  - ref('response_generator')
variables:
  - urgency_score
  - generated_response
  - classification
template: |
  Determine if escalation needed:
  Urgency: {{ urgency_score }}
  Classification: {{ classification }}
  Response: {{ generated_response }}
```

### Example 2: Financial Analysis Pipeline

```yaml
# prompts/transaction_parser.yaml
name: transaction_parser
description: Parse financial transactions
variables:
  - raw_transactions
template: |
  Parse transactions: {{ raw_transactions }}
  Extract: date, amount, merchant, category

---
# prompts/anomaly_detector.yaml
name: anomaly_detector
depends_on:
  - ref('transaction_parser')
variables:
  - parsed_transactions
  - user_profile
template: |
  Detect anomalies in: {{ parsed_transactions }}
  Based on profile: {{ user_profile }}

---
# prompts/spending_analyzer.yaml
name: spending_analyzer
depends_on:
  - ref('transaction_parser')
variables:
  - parsed_transactions
template: |
  Analyze spending patterns: {{ parsed_transactions }}
  Identify: categories, trends, recurring expenses

---
# prompts/financial_advisor.yaml
name: financial_advisor
depends_on:
  - ref('anomaly_detector')
  - ref('spending_analyzer')
variables:
  - anomalies
  - spending_analysis
  - financial_goals
template: |
  Provide financial advice based on:
  Anomalies: {{ anomalies }}
  Spending: {{ spending_analysis }}
  Goals: {{ financial_goals }}
```

### Example 3: Code Review System

```yaml
# prompts/code_style_checker.yaml
name: code_style_checker
variables:
  - code
  - language
template: |
  Check style for {{ language }} code:
  {{ code }}

---
# prompts/security_scanner.yaml
name: security_scanner
variables:
  - code
  - language
template: |
  Scan for security issues in {{ language }}:
  {{ code }}

---
# prompts/performance_analyzer.yaml
name: performance_analyzer
variables:
  - code
  - language
template: |
  Analyze performance of {{ language }} code:
  {{ code }}

---
# prompts/review_summarizer.yaml
name: review_summarizer
depends_on:
  - ref('code_style_checker')
  - ref('security_scanner')
  - ref('performance_analyzer')
variables:
  - style_issues
  - security_issues
  - performance_issues
template: |
  Summarize code review:
  Style: {{ style_issues }}
  Security: {{ security_issues }}
  Performance: {{ performance_issues }}
  
  Provide actionable recommendations.
```

## ✅ Best Practices

### 1. Keep Dependencies Meaningful

```yaml
# ✅ GOOD: Clear data flow
depends_on:
  - ref('data_cleaner')  # Provides clean data
  - ref('data_validator')  # Ensures data quality

# ❌ BAD: Arbitrary dependencies
depends_on:
  - ref('unrelated_prompt')  # No clear relationship
```

### 2. Avoid Deep Nesting

```yaml
# ✅ GOOD: Flat structure with parallel processing
# prompt_c depends on both a and b
depends_on:
  - ref('prompt_a')
  - ref('prompt_b')

# ❌ BAD: Too many levels
# a → b → c → d → e → f
```

### 3. Use Parallel Dependencies

```yaml
# ✅ GOOD: Parallel analysis
name: final_report
depends_on:
  - ref('financial_analysis')
  - ref('market_analysis')
  - ref('risk_analysis')
# All three can run in parallel
```

### 4. Document Dependency Reasons

```yaml
# ✅ GOOD: Clear documentation
name: report_generator
depends_on:
  - ref('data_processor')  # Provides cleaned dataset
  - ref('metric_calculator')  # Provides KPIs for report
description: Generates report using processed data and calculated metrics
```

### 5. Version Dependencies Carefully

```yaml
# Consider versioning for stable dependencies
depends_on:
  - ref('data_cleaner@v1.2.0')  # Pin to specific version
  - ref('analyzer')  # Use latest
```

## ❌ Anti-Patterns

### 1. Circular Dependencies

```yaml
# ❌ NEVER DO THIS
# prompt_a.yaml
depends_on:
  - ref('prompt_b')

# prompt_b.yaml
depends_on:
  - ref('prompt_a')
```

### 2. Unnecessary Dependencies

```yaml
# ❌ BAD: Adding dependencies "just in case"
depends_on:
  - ref('prompt_1')
  - ref('prompt_2')
  - ref('prompt_3')
# When only prompt_1's output is actually used
```

### 3. Hidden Dependencies

```yaml
# ❌ BAD: Template references data from another prompt without declaring dependency
template: |
  Analyze using the customer segments from the segmentation prompt
# Missing: depends_on: [ref('customer_segmentation')]
```

## 🔧 Advanced Patterns

### Dynamic Dependency Resolution

```python
# In custom code, dynamically determine dependencies
def get_dependencies(prompt_type):
    base_deps = ['ref("data_validator")']
    
    if prompt_type == "financial":
        base_deps.extend([
            'ref("currency_converter")',
            'ref("tax_calculator")'
        ])
    elif prompt_type == "marketing":
        base_deps.extend([
            'ref("audience_segmenter")',
            'ref("channel_optimizer")'
        ])
    
    return base_deps
```

### Conditional Dependencies

```yaml
# Future feature: Conditional dependencies
depends_on:
  - ref('base_analyzer')
  - when: "{{ env == 'production' }}"
    then: ref('production_validator')
  - when: "{{ include_ml == true }}"
    then: ref('ml_predictor')
```

### Dependency Groups

```yaml
# Future feature: Dependency groups
depends_on:
  required:
    - ref('data_source')
    - ref('config_loader')
  optional:
    - ref('cache_warmer')
    - ref('metric_collector')
```

## 🎯 Conclusion

The `ref()` function in PBT enables sophisticated prompt orchestration patterns that mirror real-world AI application needs. By thinking in terms of data flow and dependencies, teams can build maintainable, scalable prompt systems that are easy to understand, test, and deploy.