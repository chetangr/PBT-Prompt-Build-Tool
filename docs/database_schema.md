# 🗄️ Database Schema Documentation

## Overview

PBT uses a flexible database architecture supporting multiple backends. This document details the schema design for relational databases (PostgreSQL/MySQL), document stores (MongoDB/Firestore), and vector databases (Pinecone/Weaviate).

## Relational Database Schema (PostgreSQL)

### Core Tables

#### prompts
```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    template TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    
    INDEX idx_prompts_name (name),
    INDEX idx_prompts_tags USING GIN (tags),
    INDEX idx_prompts_created_at (created_at DESC),
    INDEX idx_prompts_deleted_at (deleted_at)
);

-- Version tracking
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    version VARCHAR(20) NOT NULL,
    template TEXT NOT NULL,
    changes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(prompt_id, version),
    INDEX idx_prompt_versions_prompt_id (prompt_id)
);
```

#### variables
```sql
CREATE TABLE variables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    validation_rules JSONB DEFAULT '{}',
    
    UNIQUE(prompt_id, name),
    INDEX idx_variables_prompt_id (prompt_id)
);
```

#### executions
```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    prompt_version VARCHAR(20) NOT NULL,
    user_id UUID REFERENCES users(id),
    input_variables JSONB NOT NULL,
    output TEXT NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    tokens_prompt INTEGER NOT NULL,
    tokens_completion INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    cost DECIMAL(10,6),
    latency_ms INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'completed',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_executions_prompt_id (prompt_id),
    INDEX idx_executions_user_id (user_id),
    INDEX idx_executions_created_at (created_at DESC),
    INDEX idx_executions_status (status)
);

-- Execution metrics for analytics
CREATE TABLE execution_metrics (
    execution_id UUID PRIMARY KEY REFERENCES executions(id),
    quality_score DECIMAL(3,1),
    feedback_score INTEGER CHECK (feedback_score BETWEEN 1 AND 5),
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    
    INDEX idx_execution_metrics_quality (quality_score)
);
```

#### tests
```sql
CREATE TABLE test_suites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    description TEXT,
    type VARCHAR(50) NOT NULL DEFAULT 'basic',
    configuration JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_test_suites_prompt_id (prompt_id)
);

CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    inputs JSONB NOT NULL,
    expected_output TEXT,
    expected_pattern TEXT,
    assertions JSONB DEFAULT '[]',
    
    INDEX idx_test_cases_suite_id (suite_id)
);

CREATE TABLE test_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suite_id UUID NOT NULL REFERENCES test_suites(id),
    prompt_version VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    total_tests INTEGER NOT NULL,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    average_score DECIMAL(3,1),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    run_by UUID REFERENCES users(id),
    
    INDEX idx_test_runs_suite_id (suite_id),
    INDEX idx_test_runs_status (status),
    INDEX idx_test_runs_started_at (started_at DESC)
);

CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES test_cases(id),
    status VARCHAR(50) NOT NULL,
    actual_output TEXT,
    score DECIMAL(3,1),
    execution_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_test_results_run_id (run_id),
    INDEX idx_test_results_status (status)
);
```

#### chains
```sql
CREATE TABLE chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_chains_name (name)
);

CREATE TABLE chain_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chain_id UUID NOT NULL REFERENCES chains(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    position INTEGER NOT NULL,
    configuration JSONB DEFAULT '{}',
    
    UNIQUE(chain_id, name),
    UNIQUE(chain_id, position),
    INDEX idx_chain_agents_chain_id (chain_id)
);

CREATE TABLE chain_flows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chain_id UUID NOT NULL REFERENCES chains(id) ON DELETE CASCADE,
    from_agent_id UUID NOT NULL REFERENCES chain_agents(id),
    to_agent_id UUID NOT NULL REFERENCES chain_agents(id),
    condition TEXT,
    mapping JSONB DEFAULT '{}',
    
    INDEX idx_chain_flows_chain_id (chain_id)
);

CREATE TABLE chain_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chain_id UUID NOT NULL REFERENCES chains(id),
    initial_inputs JSONB NOT NULL,
    final_output JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10,6) DEFAULT 0,
    total_latency_ms INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    executed_by UUID REFERENCES users(id),
    
    INDEX idx_chain_executions_chain_id (chain_id),
    INDEX idx_chain_executions_status (status)
);
```

#### users and permissions
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    api_key VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_users_email (email),
    INDEX idx_users_api_key (api_key)
);

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_teams_name (name)
);

CREATE TABLE team_members (
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (team_id, user_id)
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    team_id UUID REFERENCES teams(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    action VARCHAR(50) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID REFERENCES users(id),
    
    CHECK ((user_id IS NOT NULL) OR (team_id IS NOT NULL)),
    INDEX idx_permissions_user_id (user_id),
    INDEX idx_permissions_team_id (team_id),
    INDEX idx_permissions_resource (resource_type, resource_id)
);
```

#### deployments
```sql
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    version VARCHAR(20) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    endpoint_url TEXT,
    configuration JSONB DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'deploying',
    deployed_by UUID REFERENCES users(id),
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_deployments_prompt_id (prompt_id),
    INDEX idx_deployments_environment (environment),
    INDEX idx_deployments_status (status)
);

CREATE TABLE deployment_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_deployment_logs_deployment_id (deployment_id),
    INDEX idx_deployment_logs_created_at (created_at DESC)
);
```

### Views and Materialized Views

```sql
-- Prompt usage statistics
CREATE MATERIALIZED VIEW prompt_usage_stats AS
SELECT 
    p.id,
    p.name,
    p.version,
    COUNT(DISTINCT e.id) as total_executions,
    COUNT(DISTINCT e.user_id) as unique_users,
    AVG(e.tokens_total) as avg_tokens,
    AVG(e.cost) as avg_cost,
    AVG(e.latency_ms) as avg_latency_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.latency_ms) as p50_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY e.latency_ms) as p95_latency,
    SUM(e.cost) as total_cost,
    MAX(e.created_at) as last_used_at
FROM prompts p
LEFT JOIN executions e ON p.id = e.prompt_id
GROUP BY p.id, p.name, p.version;

CREATE INDEX idx_prompt_usage_stats_name ON prompt_usage_stats(name);

-- Test performance view
CREATE VIEW test_performance AS
SELECT 
    ts.prompt_id,
    ts.name as suite_name,
    COUNT(DISTINCT tr.id) as total_runs,
    AVG(tr.average_score) as avg_score,
    AVG(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) as pass_rate,
    AVG(tr.completed_at - tr.started_at) as avg_duration
FROM test_suites ts
JOIN test_runs tr ON ts.id = tr.suite_id
WHERE tr.status IN ('passed', 'failed')
GROUP BY ts.prompt_id, ts.name;
```

## Document Database Schema (MongoDB)

### Collections

#### prompts
```javascript
{
  "_id": ObjectId(),
  "name": "customer-classifier",
  "version": "1.2.0",
  "description": "Classify customer intents",
  "template": "Classify the following message...",
  "variables": [
    {
      "name": "message",
      "type": "string",
      "required": true,
      "description": "Customer message",
      "validation": {
        "maxLength": 1000
      }
    }
  ],
  "model": "gpt-4",
  "temperature": 0.3,
  "maxTokens": 1000,
  "examples": [
    {
      "input": {"message": "I need help"},
      "output": "support_request"
    }
  ],
  "metadata": {
    "author": "user@example.com",
    "tags": ["classification", "customer-service"],
    "category": "nlp"
  },
  "createdAt": ISODate("2024-01-15T10:00:00Z"),
  "updatedAt": ISODate("2024-01-20T15:30:00Z"),
  "versions": [
    {
      "version": "1.0.0",
      "template": "Previous template...",
      "createdAt": ISODate("2024-01-15T10:00:00Z")
    }
  ]
}

// Indexes
db.prompts.createIndex({ "name": 1 }, { unique: true })
db.prompts.createIndex({ "metadata.tags": 1 })
db.prompts.createIndex({ "createdAt": -1 })
db.prompts.createIndex({ "$**": "text" }) // Full-text search
```

#### executions
```javascript
{
  "_id": ObjectId(),
  "promptId": ObjectId("..."),
  "promptVersion": "1.2.0",
  "userId": ObjectId("..."),
  "input": {
    "message": "Where is my order?"
  },
  "output": "order_inquiry",
  "model": "gpt-4",
  "usage": {
    "promptTokens": 45,
    "completionTokens": 12,
    "totalTokens": 57
  },
  "cost": 0.00171,
  "latencyMs": 1234,
  "status": "completed",
  "metadata": {
    "requestId": "req_abc123",
    "clientIp": "192.168.1.1",
    "userAgent": "PBT-SDK/1.0"
  },
  "createdAt": ISODate("2024-01-25T14:30:00Z")
}

// Indexes
db.executions.createIndex({ "promptId": 1, "createdAt": -1 })
db.executions.createIndex({ "userId": 1, "createdAt": -1 })
db.executions.createIndex({ "status": 1 })
db.executions.createIndex({ "createdAt": -1 }, { expireAfterSeconds: 2592000 }) // 30-day TTL
```

#### test_results
```javascript
{
  "_id": ObjectId(),
  "suiteId": ObjectId("..."),
  "promptId": ObjectId("..."),
  "promptVersion": "1.2.0",
  "runId": "run_12345",
  "status": "completed",
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0
  },
  "scores": {
    "accuracy": 9.6,
    "consistency": 9.2,
    "performance": 8.8
  },
  "testCases": [
    {
      "name": "positive_sentiment",
      "input": {"text": "Great product!"},
      "expected": "positive",
      "actual": "positive",
      "passed": true,
      "score": 10.0,
      "latencyMs": 523
    }
  ],
  "metadata": {
    "environment": "production",
    "runBy": "ci-pipeline"
  },
  "startedAt": ISODate("2024-01-25T10:00:00Z"),
  "completedAt": ISODate("2024-01-25T10:05:00Z")
}
```

#### chains
```javascript
{
  "_id": ObjectId(),
  "name": "customer-support-flow",
  "version": "2.0.0",
  "description": "Automated customer support workflow",
  "agents": [
    {
      "id": "classifier",
      "promptId": ObjectId("..."),
      "inputs": ["message"],
      "outputs": ["intent", "confidence"]
    },
    {
      "id": "router",
      "promptId": ObjectId("..."),
      "inputs": ["intent", "confidence"],
      "outputs": ["action"]
    }
  ],
  "flows": [
    {
      "from": "classifier",
      "to": "router",
      "condition": "confidence > 0.8"
    }
  ],
  "metadata": {
    "author": "team@example.com",
    "tags": ["workflow", "customer-service"]
  }
}
```

## Vector Database Schema (Pinecone)

### Indexes

#### prompt-embeddings
```python
# Index configuration
index_config = {
    "name": "prompt-embeddings",
    "dimension": 1536,  # OpenAI embedding dimension
    "metric": "cosine",
    "pods": 1,
    "replicas": 1,
    "pod_type": "p1.x1"
}

# Vector schema
vector_schema = {
    "id": "prompt_123_v1.2.0",
    "values": [0.1, 0.2, ...],  # 1536-dimensional embedding
    "metadata": {
        "prompt_id": "prompt_123",
        "version": "1.2.0",
        "name": "customer-classifier",
        "type": "classification",
        "tags": ["customer-service", "nlp"],
        "model": "gpt-4",
        "created_at": "2024-01-15T10:00:00Z"
    }
}

# Query example
query_results = index.query(
    vector=query_embedding,
    top_k=10,
    include_metadata=True,
    filter={
        "tags": {"$in": ["customer-service"]},
        "model": {"$eq": "gpt-4"}
    }
)
```

#### execution-embeddings
```python
# For semantic search of past executions
execution_vector = {
    "id": "exec_456",
    "values": [0.3, 0.4, ...],  # Input/output embedding
    "metadata": {
        "execution_id": "exec_456",
        "prompt_id": "prompt_123",
        "input_summary": "order inquiry",
        "output_summary": "tracking provided",
        "quality_score": 9.5,
        "user_id": "user_789",
        "timestamp": "2024-01-25T14:30:00Z"
    }
}
```

## Key-Value Store Schema (Redis)

### Cache Structure

```redis
# Prompt cache
prompt:prompt_123 -> JSON {
    "name": "customer-classifier",
    "version": "1.2.0",
    "template": "...",
    "ttl": 3600
}

# Execution cache
exec:cache:hash(prompt_id+inputs) -> JSON {
    "output": "result",
    "model": "gpt-4",
    "tokens": 57,
    "timestamp": "2024-01-25T14:30:00Z"
}
SET exec:cache:abc123 "..." EX 3600

# Rate limiting
rate:user:user_123:minute -> 45
INCR rate:user:user_123:minute
EXPIRE rate:user:user_123:minute 60

# Session data
session:session_abc -> JSON {
    "user_id": "user_123",
    "active_prompts": ["prompt_123", "prompt_456"],
    "last_activity": "2024-01-25T14:30:00Z"
}

# Queue for async processing
LPUSH queue:executions "{\"prompt_id\": \"prompt_123\", ...}"
BRPOP queue:executions 0

# Real-time metrics
HINCRBY metrics:daily:2024-01-25 executions 1
HINCRBY metrics:daily:2024-01-25 tokens 57
HINCRBYFLOAT metrics:daily:2024-01-25 cost 0.00171
```

## Migration Scripts

### Initial Setup
```sql
-- Create database
CREATE DATABASE pbt_production;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Run migrations
\i 001_create_users.sql
\i 002_create_prompts.sql
\i 003_create_executions.sql
\i 004_create_tests.sql
\i 005_create_chains.sql
\i 006_create_indexes.sql
\i 007_create_views.sql
```

### Version Migrations
```sql
-- Example: Add new field
ALTER TABLE prompts 
ADD COLUMN IF NOT EXISTS optimization_hints JSONB DEFAULT '{}';

-- Update existing records
UPDATE prompts 
SET optimization_hints = '{"reduce_tokens": true}'
WHERE char_length(template) > 1000;
```

## Backup and Recovery

### Backup Strategy
```yaml
backup_policy:
  relational_db:
    frequency: daily
    retention: 30_days
    type: full_backup
    location: s3://backups/pbt/postgres/
    
  document_db:
    frequency: hourly
    retention: 7_days
    type: incremental
    location: s3://backups/pbt/mongodb/
    
  vector_db:
    frequency: weekly
    retention: 90_days
    type: snapshot
    
  redis:
    frequency: every_6_hours
    retention: 3_days
    type: rdb_snapshot
```

## Performance Optimization

### Indexes Strategy
```sql
-- Composite indexes for common queries
CREATE INDEX idx_executions_user_prompt_date 
ON executions(user_id, prompt_id, created_at DESC);

-- Partial indexes for filtered queries
CREATE INDEX idx_active_prompts 
ON prompts(name, version) 
WHERE deleted_at IS NULL;

-- Expression indexes
CREATE INDEX idx_prompts_lower_name 
ON prompts(LOWER(name));
```

### Query Optimization
```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT p.name, COUNT(e.id) as exec_count
FROM prompts p
JOIN executions e ON p.id = e.prompt_id
WHERE e.created_at > NOW() - INTERVAL '7 days'
GROUP BY p.name
ORDER BY exec_count DESC
LIMIT 10;
```

## Security Considerations

### Data Encryption
```sql
-- Encrypt sensitive data
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(10) NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_api_keys_hash (key_hash)
);

-- Row-level security
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY prompts_access_policy ON prompts
    FOR ALL
    USING (
        created_by = current_user_id() OR
        EXISTS (
            SELECT 1 FROM permissions
            WHERE user_id = current_user_id()
            AND resource_type = 'prompt'
            AND resource_id = prompts.id
        )
    );
```

## Monitoring Queries

### Health Checks
```sql
-- Database health
SELECT 
    'connections' as metric,
    count(*) as value
FROM pg_stat_activity
WHERE state = 'active'

UNION ALL

SELECT 
    'cache_hit_ratio',
    ROUND(sum(blks_hit)::numeric / sum(blks_hit + blks_read), 4)
FROM pg_stat_database
WHERE datname = current_database();

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

This schema provides a robust foundation for PBT's data storage needs, supporting high performance, scalability, and flexibility across different database technologies.