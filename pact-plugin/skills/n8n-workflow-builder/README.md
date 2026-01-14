# n8n Workflow Builder

Expert guide for building n8n workflow JSON files directly in Claude Code.

---

## Purpose

Build n8n workflow JSON files without requiring MCP server access. Create, configure, and validate workflow files that can be imported directly into n8n.

## Activates On

- n8n workflow
- create workflow
- build workflow
- workflow JSON
- n8n automation
- import workflow
- node configuration

## File Count

5 files, ~1,500 lines total

## Priority

**HIGH** - Essential for n8n workflow development without MCP

## Dependencies

**No MCP required!** Works entirely with JSON file creation.

**Optional MCP Integration**: If n8n-mcp is configured, additional features available:
- Direct deployment to n8n instance
- Real-time validation
- Template search and deployment

**Related skills**:
- n8n Expression Syntax (write expressions in fields)
- n8n Workflow Patterns (choose the right pattern)
- n8n Validation Expert (validate configurations)
- n8n Node Configuration (configure specific operations)
- n8n Code JavaScript (write JavaScript in Code nodes)
- n8n Code Python (write Python in Code nodes)

## Coverage

### Core Topics
- Workflow JSON structure (name, nodes, connections, settings)
- Node structure (id, name, type, typeVersion, position, parameters)
- Connection patterns (main, AI connections)
- Expression syntax (`={{...}}` format)
- Common node configurations

### Node Categories Covered
- **Triggers**: Webhook, Schedule, Manual
- **Processing**: Set, Code, IF, Switch, Merge
- **Actions**: HTTP Request, Slack, Postgres, MySQL, Email
- **AI**: Agent, OpenAI Chat Model, Memory, Tools

## Files

- **SKILL.md** (500 lines) - Core workflow building guide
- **NODE_REFERENCE.md** (500 lines) - Node configurations and examples
- **VALIDATION_GUIDE.md** (450 lines) - Validation checklist and errors
- **WORKFLOW_GUIDE.md** (560 lines) - Complete workflow examples
- **README.md** (this file) - Skill metadata

## What You'll Learn

- n8n workflow JSON structure
- Required node fields and formats
- Connection patterns (including AI connections)
- Expression syntax for dynamic data
- Validation before import
- Common mistakes and fixes
- Best practices for workflow files

## Key Features

- **No MCP Required**: Create workflows without external dependencies
- **Complete Examples**: Full workflow JSON for common patterns
- **Node Reference**: Configurations for popular nodes
- **Validation Guide**: Checklist for error-free imports
- **AI Support**: AI Agent, LLM, Memory connection patterns

## Last Updated

2026-01-14

---

**Part of**: PACT Framework n8n Skills
