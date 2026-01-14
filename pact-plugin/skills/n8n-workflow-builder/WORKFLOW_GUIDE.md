# n8n Complete Workflow Examples

Complete workflow JSON examples for common use cases.

---

## Example 1: Webhook to Slack

Receive webhook and post to Slack channel.

```json
{
  "name": "Webhook to Slack Notification",
  "nodes": [
    {
      "id": "9c3f1a2b-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "slack-notify",
        "httpMethod": "POST",
        "responseMode": "onReceived",
        "responseData": "firstEntryJson"
      },
      "webhookId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    {
      "id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
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
              "id": "assign-1",
              "name": "message",
              "value": "={{$json.body.message}}",
              "type": "string"
            },
            {
              "id": "assign-2",
              "name": "channel",
              "value": "={{$json.body.channel || '#general'}}",
              "type": "string"
            }
          ]
        },
        "options": {}
      }
    },
    {
      "id": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
      "name": "Send to Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [650, 300],
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": {
          "mode": "name",
          "value": "={{$json.channel}}"
        },
        "text": "={{$json.message}}",
        "otherOptions": {}
      },
      "credentials": {
        "slackApi": {
          "id": "slack-cred-id",
          "name": "Slack Account"
        }
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "Transform Data", "type": "main", "index": 0 }]]
    },
    "Transform Data": {
      "main": [[{ "node": "Send to Slack", "type": "main", "index": 0 }]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

**Usage**: POST to `/webhook/slack-notify` with `{"message": "Hello!", "channel": "#alerts"}`

---

## Example 2: Scheduled API Fetch

Fetch data from API on schedule and store results.

```json
{
  "name": "Daily Weather Report",
  "nodes": [
    {
      "id": "schedule-node-1",
      "name": "Daily Schedule",
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
    },
    {
      "id": "http-node-1",
      "name": "Fetch Weather",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [450, 300],
      "parameters": {
        "method": "GET",
        "url": "https://api.openweathermap.org/data/2.5/weather",
        "authentication": "none",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            { "name": "q", "value": "New York" },
            { "name": "appid", "value": "={{$env.WEATHER_API_KEY}}" },
            { "name": "units", "value": "metric" }
          ]
        },
        "options": {}
      }
    },
    {
      "id": "code-node-1",
      "name": "Format Report",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300],
      "parameters": {
        "mode": "runOnceForAllItems",
        "language": "javaScript",
        "jsCode": "const weather = $input.first().json;\n\nconst report = {\n  city: weather.name,\n  temp: Math.round(weather.main.temp),\n  description: weather.weather[0].description,\n  humidity: weather.main.humidity,\n  timestamp: new Date().toISOString()\n};\n\nreturn [{ json: report }];"
      }
    },
    {
      "id": "slack-node-1",
      "name": "Send Report",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [850, 300],
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": { "mode": "name", "value": "#weather" },
        "text": "Weather in ={{$json.city}}: ={{$json.temp}}C, ={{$json.description}}. Humidity: ={{$json.humidity}}%",
        "otherOptions": {}
      },
      "credentials": {
        "slackApi": { "id": "slack-cred", "name": "Slack" }
      }
    }
  ],
  "connections": {
    "Daily Schedule": {
      "main": [[{ "node": "Fetch Weather", "type": "main", "index": 0 }]]
    },
    "Fetch Weather": {
      "main": [[{ "node": "Format Report", "type": "main", "index": 0 }]]
    },
    "Format Report": {
      "main": [[{ "node": "Send Report", "type": "main", "index": 0 }]]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```

---

## Example 3: Conditional Processing with IF

Route data based on conditions.

```json
{
  "name": "Order Processing with Routing",
  "nodes": [
    {
      "id": "webhook-1",
      "name": "Order Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "orders",
        "httpMethod": "POST",
        "responseMode": "lastNode"
      },
      "webhookId": "order-webhook-uuid"
    },
    {
      "id": "if-1",
      "name": "Check Order Value",
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
              "id": "condition-1",
              "leftValue": "={{$json.body.total}}",
              "rightValue": 100,
              "operator": {
                "type": "number",
                "operation": "gte"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      }
    },
    {
      "id": "high-value-1",
      "name": "High Value Order",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [650, 200],
      "parameters": {
        "mode": "manual",
        "assignments": {
          "assignments": [
            {
              "id": "a1",
              "name": "priority",
              "value": "high",
              "type": "string"
            },
            {
              "id": "a2",
              "name": "orderId",
              "value": "={{$json.body.orderId}}",
              "type": "string"
            }
          ]
        }
      }
    },
    {
      "id": "standard-1",
      "name": "Standard Order",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [650, 400],
      "parameters": {
        "mode": "manual",
        "assignments": {
          "assignments": [
            {
              "id": "a1",
              "name": "priority",
              "value": "standard",
              "type": "string"
            },
            {
              "id": "a2",
              "name": "orderId",
              "value": "={{$json.body.orderId}}",
              "type": "string"
            }
          ]
        }
      }
    },
    {
      "id": "respond-1",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [850, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"status\": \"received\", \"priority\": $json.priority, \"orderId\": $json.orderId } }}"
      }
    }
  ],
  "connections": {
    "Order Webhook": {
      "main": [[{ "node": "Check Order Value", "type": "main", "index": 0 }]]
    },
    "Check Order Value": {
      "main": [
        [{ "node": "High Value Order", "type": "main", "index": 0 }],
        [{ "node": "Standard Order", "type": "main", "index": 0 }]
      ]
    },
    "High Value Order": {
      "main": [[{ "node": "Respond", "type": "main", "index": 0 }]]
    },
    "Standard Order": {
      "main": [[{ "node": "Respond", "type": "main", "index": 0 }]]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```

**IF Connection Note**: First array is true branch, second is false branch.

---

## Example 4: AI Agent Workflow

AI assistant with tools and memory.

```json
{
  "name": "AI Assistant",
  "nodes": [
    {
      "id": "webhook-ai-1",
      "name": "Chat Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "chat",
        "httpMethod": "POST",
        "responseMode": "lastNode"
      },
      "webhookId": "chat-webhook-uuid"
    },
    {
      "id": "openai-1",
      "name": "OpenAI Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1.2,
      "position": [250, 500],
      "parameters": {
        "model": "gpt-4",
        "options": {
          "temperature": 0.7
        }
      },
      "credentials": {
        "openAiApi": { "id": "openai-cred", "name": "OpenAI" }
      }
    },
    {
      "id": "memory-1",
      "name": "Chat Memory",
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "typeVersion": 1.2,
      "position": [250, 650],
      "parameters": {
        "sessionIdType": "customKey",
        "sessionKey": "={{$json.body.sessionId}}",
        "contextWindowLength": 10
      }
    },
    {
      "id": "agent-1",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.6,
      "position": [450, 300],
      "parameters": {
        "options": {
          "systemMessage": "You are a helpful assistant. Be concise and friendly."
        }
      }
    },
    {
      "id": "respond-ai-1",
      "name": "Send Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [650, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"response\": $json.output, \"sessionId\": $json.body?.sessionId } }}"
      }
    }
  ],
  "connections": {
    "Chat Webhook": {
      "main": [[{ "node": "AI Agent", "type": "main", "index": 0 }]]
    },
    "OpenAI Chat Model": {
      "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]]
    },
    "Chat Memory": {
      "ai_memory": [[{ "node": "AI Agent", "type": "ai_memory", "index": 0 }]]
    },
    "AI Agent": {
      "main": [[{ "node": "Send Response", "type": "main", "index": 0 }]]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```

**AI Connection Types**:
- `ai_languageModel` - From LLM to Agent
- `ai_memory` - From Memory to Agent
- `ai_tool` - From Tool nodes to Agent

---

## Example 5: Database Sync

Sync data between webhook and database.

```json
{
  "name": "User Sync to Database",
  "nodes": [
    {
      "id": "webhook-db-1",
      "name": "User Update Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "user-sync",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "webhookId": "user-sync-uuid"
    },
    {
      "id": "postgres-1",
      "name": "Upsert User",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [450, 300],
      "parameters": {
        "operation": "upsert",
        "schema": { "mode": "list", "value": "public" },
        "table": { "mode": "list", "value": "users" },
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "email": "={{$json.body.email}}",
            "name": "={{$json.body.name}}",
            "updated_at": "={{$now}}"
          }
        },
        "conflictColumns": ["email"],
        "options": {}
      },
      "credentials": {
        "postgres": { "id": "pg-cred", "name": "Postgres" }
      }
    }
  ],
  "connections": {
    "User Update Webhook": {
      "main": [[{ "node": "Upsert User", "type": "main", "index": 0 }]]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```

---

## Workflow File Organization

Recommended directory structure:

```
project/
├── workflows/
│   ├── production/
│   │   ├── webhook-to-slack.json
│   │   └── daily-report.json
│   ├── development/
│   │   └── test-workflow.json
│   └── templates/
│       ├── webhook-template.json
│       └── scheduled-template.json
├── docs/
│   └── workflow-docs.md
└── .env  (credentials - never commit!)
```

---

## Importing Workflows

### n8n UI Import

1. Open n8n instance
2. Click gear icon (Settings)
3. Select "Import from File"
4. Choose JSON file
5. Review imported workflow
6. Configure credentials (they're removed on export)
7. Activate workflow

### API Import

```bash
curl -X POST "https://your-n8n.com/api/v1/workflows" \
  -H "X-N8N-API-KEY: your-key" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

---

## Best Practices

### Naming Conventions
- Workflows: `descriptive-name.json` (kebab-case)
- Nodes: Clear, action-based names ("Fetch Users", "Send Email")

### Documentation
- Add notes to complex workflows
- Document required credentials
- Include test data examples

### Version Control
- Commit workflow JSON files
- Use meaningful commit messages
- Tag releases for production workflows

### Testing
- Test with sample data before deployment
- Verify all paths (IF true/false, Switch cases)
- Check error handling

---

## Related

- [SKILL.md](SKILL.md) - Workflow structure overview
- [NODE_REFERENCE.md](NODE_REFERENCE.md) - Node configurations
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Validation checklist
