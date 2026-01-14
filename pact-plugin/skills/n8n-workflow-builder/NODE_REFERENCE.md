# n8n Node Reference Guide

Complete reference for common n8n nodes and their configurations.

---

## Node Type Format

**Always use the full prefix** in workflow JSON:
```json
"type": "n8n-nodes-base.webhook"
"type": "n8n-nodes-base.httpRequest"
"type": "@n8n/n8n-nodes-langchain.agent"
```

---

## Trigger Nodes

### Webhook

**Type**: `n8n-nodes-base.webhook`
**Version**: 2

```json
{
  "id": "webhook-uuid",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "position": [250, 300],
  "parameters": {
    "path": "my-endpoint",
    "httpMethod": "POST",
    "responseMode": "onReceived",
    "responseData": "firstEntryJson"
  },
  "webhookId": "unique-webhook-uuid"
}
```

**Key Parameters**:
- `path`: URL endpoint path
- `httpMethod`: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- `responseMode`: "onReceived" (immediate) or "lastNode" (after processing)
- `responseData`: What to return - "firstEntryJson", "allEntries", "noData"

**Data Access**: Webhook data is in `$json.body.*`
```
={{$json.body.email}}
={{$json.body.name}}
```

---

### Schedule Trigger

**Type**: `n8n-nodes-base.scheduleTrigger`
**Version**: 1.2

```json
{
  "id": "schedule-uuid",
  "name": "Schedule",
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "position": [250, 300],
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * *"
        }
      ]
    }
  }
}
```

**Key Parameters**:
- `rule.interval`: Array of schedule rules
- `field`: "cronExpression", "hours", "minutes", "seconds"
- `expression`: Cron expression (e.g., "0 9 * * *" = daily at 9 AM)

---

### Manual Trigger

**Type**: `n8n-nodes-base.manualTrigger`
**Version**: 1

```json
{
  "id": "manual-uuid",
  "name": "Manual Trigger",
  "type": "n8n-nodes-base.manualTrigger",
  "typeVersion": 1,
  "position": [250, 300],
  "parameters": {}
}
```

Use for testing or manually-triggered workflows.

---

## Data Processing Nodes

### Set (Data Transformation)

**Type**: `n8n-nodes-base.set`
**Version**: 3.4

```json
{
  "id": "set-uuid",
  "name": "Transform Data",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "position": [450, 300],
  "parameters": {
    "mode": "manual",
    "duplicateItem": false,
    "assignments": {
      "assignments": [
        {
          "id": "assignment-uuid",
          "name": "email",
          "value": "={{$json.body.email}}",
          "type": "string"
        },
        {
          "id": "assignment-uuid-2",
          "name": "processed",
          "value": true,
          "type": "boolean"
        }
      ]
    },
    "options": {}
  }
}
```

**Key Parameters**:
- `mode`: "manual" (define fields) or "raw" (JSON)
- `assignments.assignments`: Array of field mappings
- Each assignment: `id`, `name`, `value`, `type`

---

### Code (JavaScript/Python)

**Type**: `n8n-nodes-base.code`
**Version**: 2

```json
{
  "id": "code-uuid",
  "name": "Process Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const items = $input.all();\nreturn items.map(item => ({\n  json: {\n    processed: true,\n    data: item.json\n  }\n}));"
  }
}
```

**Key Parameters**:
- `mode`: "runOnceForAllItems" or "runOnceForEachItem"
- `language`: "javaScript" or "python"
- `jsCode` / `pythonCode`: The code to execute

**JavaScript Data Access**:
- `$input.all()` - All items
- `$input.first()` - First item
- `$input.item` - Current item (in runOnceForEachItem mode)

---

### IF (Conditional)

**Type**: `n8n-nodes-base.if`
**Version**: 2.1

```json
{
  "id": "if-uuid",
  "name": "IF",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2.1,
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "id": "condition-uuid",
          "leftValue": "={{$json.status}}",
          "rightValue": "active",
          "operator": {
            "type": "string",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

**Connection Structure** (two outputs):
```json
{
  "IF": {
    "main": [
      [{ "node": "True Handler", "type": "main", "index": 0 }],
      [{ "node": "False Handler", "type": "main", "index": 0 }]
    ]
  }
}
```

---

### Switch (Multi-way Branching)

**Type**: `n8n-nodes-base.switch`
**Version**: 3

```json
{
  "id": "switch-uuid",
  "name": "Switch",
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "rules": {
      "rules": [
        {
          "outputKey": "Case 1",
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{$json.type}}",
                "rightValue": "order",
                "operator": { "type": "string", "operation": "equals" }
              }
            ]
          }
        },
        {
          "outputKey": "Case 2",
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{$json.type}}",
                "rightValue": "refund",
                "operator": { "type": "string", "operation": "equals" }
              }
            ]
          }
        }
      ]
    },
    "options": {
      "fallbackOutput": "extra"
    }
  }
}
```

---

## Action Nodes

### HTTP Request

**Type**: `n8n-nodes-base.httpRequest`
**Version**: 4.2

```json
{
  "id": "http-uuid",
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "authentication": "none",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "email",
          "value": "={{$json.body.email}}"
        }
      ]
    },
    "options": {}
  }
}
```

**Key Parameters**:
- `method`: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- `url`: Target URL (can use expressions)
- `authentication`: "none", "genericCredentialType", "predefinedCredentialType"
- `sendBody`: Whether to send request body
- `bodyParameters`: Body fields for form/JSON

**For JSON Body**:
```json
{
  "contentType": "json",
  "body": "={{JSON.stringify({ email: $json.body.email })}}"
}
```

---

### Slack

**Type**: `n8n-nodes-base.slack`
**Version**: 2.2

```json
{
  "id": "slack-uuid",
  "name": "Slack",
  "type": "n8n-nodes-base.slack",
  "typeVersion": 2.2,
  "position": [450, 300],
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": {
      "mode": "name",
      "value": "#general"
    },
    "text": "={{$json.body.message}}",
    "otherOptions": {}
  },
  "credentials": {
    "slackApi": {
      "id": "credential-id",
      "name": "Slack Account"
    }
  }
}
```

**Resources & Operations**:
- `message`: post, update, delete, getPermalink
- `channel`: archive, close, create, get, getAll, history, invite, join, kick, leave, member, open, rename, setDescription, setPurpose, setTopic, unarchive
- `file`: getAll, upload
- `reaction`: add, get, remove
- `star`: add, delete, getAll
- `user`: get, getAll, getStatus, updateProfile

---

### Postgres

**Type**: `n8n-nodes-base.postgres`
**Version**: 2.5

```json
{
  "id": "postgres-uuid",
  "name": "Postgres",
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.5,
  "position": [450, 300],
  "parameters": {
    "operation": "select",
    "schema": {
      "mode": "list",
      "value": "public"
    },
    "table": {
      "mode": "list",
      "value": "users"
    },
    "limit": 50,
    "options": {}
  },
  "credentials": {
    "postgres": {
      "id": "credential-id",
      "name": "Postgres Account"
    }
  }
}
```

**Operations**:
- `select`: Query data
- `insert`: Insert rows
- `update`: Update rows
- `upsert`: Insert or update
- `delete`: Delete rows
- `executeQuery`: Run raw SQL

---

## AI Nodes

### AI Agent

**Type**: `@n8n/n8n-nodes-langchain.agent`
**Version**: 1.6

```json
{
  "id": "agent-uuid",
  "name": "AI Agent",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "typeVersion": 1.6,
  "position": [450, 300],
  "parameters": {
    "options": {
      "systemMessage": "You are a helpful assistant."
    }
  }
}
```

**AI Connections** (from other nodes to AI Agent):
```json
{
  "OpenAI Chat Model": {
    "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]]
  },
  "HTTP Request Tool": {
    "ai_tool": [[{ "node": "AI Agent", "type": "ai_tool", "index": 0 }]]
  },
  "Window Buffer Memory": {
    "ai_memory": [[{ "node": "AI Agent", "type": "ai_memory", "index": 0 }]]
  }
}
```

---

### OpenAI Chat Model

**Type**: `@n8n/n8n-nodes-langchain.lmChatOpenAi`
**Version**: 1.2

```json
{
  "id": "openai-uuid",
  "name": "OpenAI Chat Model",
  "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
  "typeVersion": 1.2,
  "position": [250, 300],
  "parameters": {
    "model": "gpt-4",
    "options": {
      "temperature": 0.7
    }
  },
  "credentials": {
    "openAiApi": {
      "id": "credential-id",
      "name": "OpenAI Account"
    }
  }
}
```

---

## Common Patterns

### Webhook to Processing to Output

```
Webhook → Set (transform) → HTTP Request (API call)
```

### Conditional Processing

```
Webhook → IF → True: Slack notify
              → False: Log only
```

### Scheduled Report

```
Schedule → HTTP Request (fetch) → Code (process) → Email
```

### AI Assistant

```
Webhook → AI Agent ← OpenAI Chat Model
                   ← HTTP Tool
                   ← Memory
```

---

## MCP Integration (Optional)

If you have n8n-mcp configured, you can use these tools for node discovery:
- `search_nodes({query: "slack"})` - Find nodes
- `get_node({nodeType: "nodes-base.slack"})` - Get details
- `validate_node({nodeType, config})` - Validate configuration

Without MCP, use this reference guide for node configurations.

---

## Related

- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Validate configurations
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow examples
