---
name: n8n-workflow-builder
description: Expert guide for building n8n workflow JSON files. Use when creating workflows, understanding node structure, configuring connections, or building any n8n automation. Provides workflow structure guidance, node configuration patterns, and best practices for JSON-based development.
---

# n8n Workflow Builder

Master guide for creating n8n workflow JSON files directly in your codebase.

---

## Workflow JSON Structure

Every n8n workflow follows this structure:

```json
{
  "name": "My Workflow",
  "nodes": [],
  "connections": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "pinData": {}
}
```

---

## Quick Reference

### Workflow File Template

```json
{
  "name": "Webhook to Slack",
  "nodes": [
    {
      "id": "webhook-1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "my-webhook",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "webhookId": "unique-webhook-id"
    },
    {
      "id": "slack-1",
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [450, 300],
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": { "mode": "name", "value": "#general" },
        "text": "={{$json.body.message}}"
      },
      "credentials": {
        "slackApi": { "id": "cred-id", "name": "Slack Account" }
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "Slack", "type": "main", "index": 0 }]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

---

## Node Structure

### Required Node Fields

```json
{
  "id": "unique-uuid-string",
  "name": "Display Name",
  "type": "n8n-nodes-base.nodeType",
  "typeVersion": 2,
  "position": [x, y],
  "parameters": {}
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (UUID format recommended) |
| `name` | Yes | Display name shown in n8n UI |
| `type` | Yes | Node type with full prefix |
| `typeVersion` | Yes | Version of the node to use |
| `position` | Yes | [x, y] coordinates in canvas |
| `parameters` | Yes | Node-specific configuration |

### Optional Node Fields

| Field | Description |
|-------|-------------|
| `credentials` | Reference to stored credentials |
| `webhookId` | UUID for webhook nodes |
| `disabled` | Set to true to disable node |
| `notesInFlow` | Notes displayed in workflow |
| `onError` | Error handling: "continueErrorOutput", "stopWorkflow" |

---

## Connection Structure

### Basic Connection

```json
{
  "connections": {
    "Source Node Name": {
      "main": [
        [{ "node": "Target Node Name", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

### Multi-Output Nodes (IF, Switch)

**IF Node** - Two outputs (true/false):
```json
{
  "connections": {
    "IF": {
      "main": [
        [{ "node": "True Handler", "type": "main", "index": 0 }],
        [{ "node": "False Handler", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

**Switch Node** - Multiple outputs:
```json
{
  "connections": {
    "Switch": {
      "main": [
        [{ "node": "Case 0 Handler", "type": "main", "index": 0 }],
        [{ "node": "Case 1 Handler", "type": "main", "index": 0 }],
        [{ "node": "Default Handler", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

### AI Node Connections

AI nodes use special connection types:

```json
{
  "connections": {
    "OpenAI Chat Model": {
      "ai_languageModel": [
        [{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]
      ]
    },
    "HTTP Request Tool": {
      "ai_tool": [
        [{ "node": "AI Agent", "type": "ai_tool", "index": 0 }]
      ]
    },
    "Window Buffer Memory": {
      "ai_memory": [
        [{ "node": "AI Agent", "type": "ai_memory", "index": 0 }]
      ]
    }
  }
}
```

**AI Connection Types**:
- `ai_languageModel` - LLM connections
- `ai_tool` - Tool connections
- `ai_memory` - Memory connections
- `ai_outputParser` - Output parser connections
- `ai_embedding` - Embedding connections
- `ai_vectorStore` - Vector store connections
- `ai_document` - Document connections
- `ai_textSplitter` - Text splitter connections

---

## Common Node Types

### Triggers

| Node Type | Use Case | typeVersion |
|-----------|----------|-------------|
| `n8n-nodes-base.webhook` | Receive HTTP requests | 2 |
| `n8n-nodes-base.scheduleTrigger` | Run on schedule (cron) | 1.2 |
| `n8n-nodes-base.manualTrigger` | Manual execution | 1 |
| `n8n-nodes-base.emailTrigger` | Trigger on email | 1 |

### Processing

| Node Type | Use Case | typeVersion |
|-----------|----------|-------------|
| `n8n-nodes-base.set` | Transform/map data | 3.4 |
| `n8n-nodes-base.code` | Custom JavaScript/Python | 2 |
| `n8n-nodes-base.if` | Conditional branching | 2.1 |
| `n8n-nodes-base.switch` | Multi-way branching | 3 |
| `n8n-nodes-base.merge` | Combine data streams | 3 |
| `n8n-nodes-base.splitInBatches` | Process in chunks | 3 |

### Actions

| Node Type | Use Case | typeVersion |
|-----------|----------|-------------|
| `n8n-nodes-base.httpRequest` | Call REST APIs | 4.2 |
| `n8n-nodes-base.slack` | Slack integration | 2.2 |
| `n8n-nodes-base.gmail` | Gmail integration | 2.1 |
| `n8n-nodes-base.postgres` | PostgreSQL database | 2.5 |
| `n8n-nodes-base.mysql` | MySQL database | 2.4 |

### AI Nodes

| Node Type | Use Case | typeVersion |
|-----------|----------|-------------|
| `@n8n/n8n-nodes-langchain.agent` | AI Agent | 1.6 |
| `@n8n/n8n-nodes-langchain.openAi` | OpenAI Chat Model | 1.2 |
| `@n8n/n8n-nodes-langchain.memoryBufferWindow` | Conversation memory | 1.2 |

---

## Detailed Guides

### Node Configuration
See [NODE_REFERENCE.md](NODE_REFERENCE.md) for:
- Common node configurations
- Required parameters per node
- Configuration examples

### Validation
See [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) for:
- JSON structure validation
- Common errors and fixes
- Pre-import checklist

### Complete Examples
See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for:
- Full workflow examples
- Pattern implementations
- Step-by-step tutorials

---

## Expression Syntax

Expressions in n8n use the `={{}}` format:

```json
{
  "parameters": {
    "text": "={{$json.body.message}}",
    "email": "={{$node['Webhook'].json.body.email}}",
    "index": "={{$itemIndex}}"
  }
}
```

**Common Expressions**:
- `={{$json.fieldName}}` - Current item field
- `={{$json.body.fieldName}}` - Webhook body data
- `={{$node["Node Name"].json.field}}` - Previous node data
- `={{$itemIndex}}` - Current item index
- `={{$now}}` - Current timestamp
- `={{$env.VARIABLE}}` - Environment variable

---

## Building Workflows

### Step-by-Step Process

1. **Choose Pattern**
   - Webhook processing
   - API integration
   - Database operations
   - AI agent
   - Scheduled task

2. **Define Nodes**
   - Start with trigger node
   - Add processing nodes
   - Add output/action nodes

3. **Configure Connections**
   - Connect nodes in sequence
   - Handle multi-output nodes (IF, Switch)
   - Add AI connections if needed

4. **Add Parameters**
   - Configure each node
   - Use expressions for dynamic data
   - Reference credentials (will be linked on import)

5. **Validate JSON**
   - Check syntax
   - Verify node IDs are unique
   - Confirm all connections are valid

6. **Save & Import**
   - Save to `workflows/` directory
   - Import in n8n UI
   - Configure credentials
   - Activate workflow

---

## Common Mistakes

### Mistake 1: Wrong Node Type Prefix

```json
// WRONG
"type": "webhook"
"type": "nodes-base.webhook"

// CORRECT
"type": "n8n-nodes-base.webhook"
```

### Mistake 2: Expression Syntax

```json
// WRONG - Missing equals sign
"text": "{{$json.message}}"

// CORRECT
"text": "={{$json.message}}"
```

### Mistake 3: Webhook Data Access

```json
// WRONG - Webhook data is nested
"email": "={{$json.email}}"

// CORRECT - Access body field
"email": "={{$json.body.email}}"
```

### Mistake 4: Missing Connection Array

```json
// WRONG
"connections": {
  "Webhook": {
    "main": { "node": "Slack", "type": "main", "index": 0 }
  }
}

// CORRECT - Nested arrays required
"connections": {
  "Webhook": {
    "main": [[{ "node": "Slack", "type": "main", "index": 0 }]]
  }
}
```

### Mistake 5: Duplicate Node IDs

Each node must have a unique `id` field. Use UUID format:
```json
"id": "550e8400-e29b-41d4-a716-446655440000"
```

### Mistake 6: Missing typeVersion

Always include `typeVersion` for each node:
```json
{
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2
}
```

---

## Importing Workflows

### Manual Import (n8n UI)

1. Open n8n
2. Go to Settings (gear icon)
3. Select "Import from File"
4. Choose your JSON file
5. Review imported workflow
6. Configure any required credentials
7. Activate when ready

### API Import (if available)

If you have n8n API access:

```bash
curl -X POST "https://your-n8n-instance/api/v1/workflows" \
  -H "X-N8N-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

---

## Best Practices

### Do
- Use descriptive node names
- Include comments in Code nodes
- Save workflows with meaningful filenames
- Use UUIDs for node IDs
- Validate JSON before importing
- Test workflows before activation
- Version control your workflow files
- Use expressions for dynamic data

### Don't
- Hardcode sensitive data in parameters
- Reuse node IDs across workflows
- Skip the trigger node
- Leave connections incomplete
- Ignore typeVersion field
- Mix node type formats

---

## File Organization

Recommended structure:
```
project/
├── workflows/
│   ├── webhook-to-slack.json
│   ├── daily-report.json
│   └── api-integration.json
├── docs/
│   └── workflow-documentation.md
└── .env  (never commit credentials!)
```

---

## MCP Integration (Optional)

If you have n8n-mcp MCP server configured, you gain additional capabilities:
- Deploy workflows directly to n8n instance
- Validate against live node definitions
- Search 2,700+ workflow templates
- Real-time node discovery

**Without MCP** (default mode):
- Create workflow JSON files
- Import manually via n8n UI
- Use documented node types and patterns

---

## Summary

**Key Points**:
1. Node type format: Always `n8n-nodes-base.*`
2. Expression format: Always `={{expression}}`
3. Connections: Nested array structure `[[{...}]]`
4. Webhook data: Access via `$json.body.*`
5. Node IDs: Must be unique per workflow
6. Import: Use n8n UI or API

**Related Skills**:
- n8n Expression Syntax - Write expressions correctly
- n8n Workflow Patterns - Architectural patterns
- n8n Validation Expert - Validate and fix errors
- n8n Node Configuration - Configure specific operations
- n8n Code JavaScript - Write JavaScript in Code nodes
- n8n Code Python - Write Python in Code nodes
