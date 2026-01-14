# n8n Workflow JSON Validation Guide

Complete guide for validating n8n workflow JSON files before import.

---

## Pre-Import Checklist

Before importing a workflow JSON file into n8n, verify:

### 1. JSON Syntax
- [ ] Valid JSON (no trailing commas, proper quotes)
- [ ] All brackets and braces balanced
- [ ] String values properly escaped

### 2. Required Fields
- [ ] Workflow has `name` field
- [ ] Workflow has `nodes` array
- [ ] Workflow has `connections` object
- [ ] Each node has: `id`, `name`, `type`, `typeVersion`, `position`, `parameters`

### 3. Node Configuration
- [ ] Node types use full prefix (`n8n-nodes-base.*`)
- [ ] Each node has unique `id`
- [ ] Node names are unique within workflow
- [ ] `typeVersion` is specified for each node

### 4. Connections
- [ ] All source nodes exist
- [ ] All target nodes exist
- [ ] Connection arrays are properly nested `[[{...}]]`
- [ ] AI connections use correct types (`ai_languageModel`, etc.)

### 5. Expressions
- [ ] Expression format: `={{...}}` (not `{{...}}`)
- [ ] Webhook data accessed via `$json.body.*`
- [ ] Node references use correct names

---

## Common Validation Errors

### Error 1: Invalid JSON Syntax

**Symptoms**: Import fails immediately

**Common Causes**:
```json
// WRONG - Trailing comma
{
  "name": "Test",
  "nodes": [],  // ← trailing comma before closing brace
}

// CORRECT
{
  "name": "Test",
  "nodes": []
}
```

**Fix**: Use a JSON validator or IDE with JSON support.

---

### Error 2: Missing Node Fields

**Symptoms**: Node appears but doesn't work

```json
// WRONG - Missing typeVersion
{
  "id": "node-1",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "position": [250, 300],
  "parameters": {}
}

// CORRECT
{
  "id": "node-1",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "position": [250, 300],
  "parameters": {}
}
```

**Required Node Fields**:
- `id` - Unique identifier
- `name` - Display name
- `type` - Full node type
- `typeVersion` - Node version
- `position` - [x, y] coordinates
- `parameters` - Configuration object

---

### Error 3: Wrong Node Type Format

**Symptoms**: "Node type not found" error

```json
// WRONG - Short prefix
"type": "nodes-base.webhook"

// WRONG - No prefix
"type": "webhook"

// CORRECT - Full prefix
"type": "n8n-nodes-base.webhook"
```

**Node Type Formats**:
- Core nodes: `n8n-nodes-base.*`
- AI/Langchain nodes: `@n8n/n8n-nodes-langchain.*`

---

### Error 4: Invalid Connection Structure

**Symptoms**: Nodes not connected despite configuration

```json
// WRONG - Missing nested arrays
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

**Connection Structure**:
```
connections → SourceNodeName → outputType → [outputIndex][connectionIndex] → {target}
```

---

### Error 5: Expression Syntax

**Symptoms**: Expressions shown as literal text

```json
// WRONG - Missing equals sign
"text": "{{$json.message}}"

// WRONG - Single braces
"text": "{$json.message}"

// CORRECT
"text": "={{$json.message}}"
```

**Expression Format**: Always `={{expression}}`

---

### Error 6: Webhook Data Access

**Symptoms**: Data is undefined or empty

```json
// WRONG - Direct access
"email": "={{$json.email}}"

// CORRECT - Access via body
"email": "={{$json.body.email}}"
```

**Webhook Data Structure**:
```javascript
$json = {
  body: { /* POST body data */ },
  headers: { /* Request headers */ },
  params: { /* URL parameters */ },
  query: { /* Query string */ }
}
```

---

### Error 7: Duplicate Node IDs

**Symptoms**: Unpredictable behavior, wrong connections

```json
// WRONG - Same ID
{ "id": "node-1", "name": "Webhook", ... },
{ "id": "node-1", "name": "Slack", ... }

// CORRECT - Unique IDs
{ "id": "webhook-uuid-1", "name": "Webhook", ... },
{ "id": "slack-uuid-2", "name": "Slack", ... }
```

**Best Practice**: Use UUID format for IDs.

---

### Error 8: Broken Connection References

**Symptoms**: Connections don't appear in UI

```json
// WRONG - Target node doesn't exist
"connections": {
  "Webhook": {
    "main": [[{ "node": "Nonexistent Node", "type": "main", "index": 0 }]]
  }
}
```

**Fix**: Ensure all target node names match exactly.

---

### Error 9: AI Connection Type Mismatch

**Symptoms**: AI nodes not receiving inputs

```json
// WRONG - Using "main" for AI connection
"connections": {
  "OpenAI Chat Model": {
    "main": [[{ "node": "AI Agent", "type": "main", "index": 0 }]]
  }
}

// CORRECT - Using ai_languageModel
"connections": {
  "OpenAI Chat Model": {
    "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]]
  }
}
```

**AI Connection Types**:
- `ai_languageModel` - LLM models
- `ai_tool` - Agent tools
- `ai_memory` - Memory nodes
- `ai_outputParser` - Output parsers
- `ai_embedding` - Embedding models
- `ai_vectorStore` - Vector stores
- `ai_document` - Document loaders
- `ai_textSplitter` - Text splitters

---

## Validation Tools

### JSON Validators

**Online**:
- [JSONLint](https://jsonlint.com/)
- [JSON Formatter](https://jsonformatter.curiousconcept.com/)

**VS Code Extensions**:
- Built-in JSON validation
- Prettier for formatting

### Command Line

```bash
# Check JSON syntax (macOS/Linux)
cat workflow.json | python -m json.tool > /dev/null && echo "Valid JSON"

# Pretty print
cat workflow.json | python -m json.tool
```

### n8n Import Test

1. Create a test n8n instance
2. Import workflow
3. Check for import errors
4. Test execution

---

## Validation Workflow

### Step 1: Validate JSON Syntax

```bash
# Using Python
python -c "import json; json.load(open('workflow.json'))"

# Using Node.js
node -e "require('./workflow.json')"
```

### Step 2: Check Required Fields

Manually or programmatically verify:
- Workflow has name, nodes, connections
- Each node has all required fields
- Node types use correct prefix

### Step 3: Verify Connections

- All source nodes exist in nodes array
- All target nodes exist in nodes array
- Connection types match node types (main vs ai_*)

### Step 4: Test Import

- Import into n8n
- Check for warnings/errors
- Verify node connections in UI

### Step 5: Test Execution

- Run workflow with test data
- Verify data flows correctly
- Check expression evaluation

---

## Best Practices

### Do
- Use a JSON-aware editor (VS Code, etc.)
- Validate JSON before importing
- Use UUIDs for node IDs
- Test with sample data before deployment
- Keep backups of working workflows
- Use meaningful node names

### Don't
- Manually edit without validation
- Reuse node IDs across workflows
- Skip testing after changes
- Ignore import warnings
- Hardcode sensitive data

---

## MCP Integration (Optional)

If you have n8n-mcp configured, you can use:

```javascript
// Validate node configuration
validate_node({
  nodeType: "nodes-base.slack",
  config: { resource: "message", operation: "post" },
  profile: "runtime"
})

// Validate complete workflow
validate_workflow({
  workflow: { nodes: [...], connections: {...} },
  options: { validateNodes: true, validateConnections: true }
})
```

Without MCP, use the manual validation steps above.

---

## Quick Validation Script

```javascript
// validate-workflow.js
const fs = require('fs');

function validateWorkflow(filepath) {
  const errors = [];

  // Load JSON
  let workflow;
  try {
    workflow = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  } catch (e) {
    return [`Invalid JSON: ${e.message}`];
  }

  // Check required fields
  if (!workflow.name) errors.push('Missing workflow name');
  if (!Array.isArray(workflow.nodes)) errors.push('Missing nodes array');
  if (!workflow.connections) errors.push('Missing connections object');

  // Check nodes
  const nodeNames = new Set();
  const nodeIds = new Set();

  workflow.nodes?.forEach((node, i) => {
    if (!node.id) errors.push(`Node ${i}: Missing id`);
    if (!node.name) errors.push(`Node ${i}: Missing name`);
    if (!node.type) errors.push(`Node ${i}: Missing type`);
    if (!node.typeVersion) errors.push(`Node ${i}: Missing typeVersion`);
    if (!node.position) errors.push(`Node ${i}: Missing position`);

    if (node.id && nodeIds.has(node.id)) {
      errors.push(`Duplicate node id: ${node.id}`);
    }
    nodeIds.add(node.id);

    if (node.name) nodeNames.add(node.name);

    // Check node type format
    if (node.type && !node.type.includes('-nodes-')) {
      errors.push(`Node ${node.name}: Invalid type format (use n8n-nodes-base.*)`);
    }
  });

  // Check connections
  Object.entries(workflow.connections || {}).forEach(([source, outputs]) => {
    if (!nodeNames.has(source)) {
      errors.push(`Connection source not found: ${source}`);
    }

    Object.values(outputs).forEach(outputArray => {
      outputArray?.flat()?.forEach(conn => {
        if (conn.node && !nodeNames.has(conn.node)) {
          errors.push(`Connection target not found: ${conn.node}`);
        }
      });
    });
  });

  return errors;
}

// Usage
const errors = validateWorkflow(process.argv[2] || 'workflow.json');
if (errors.length === 0) {
  console.log('Workflow validation passed!');
} else {
  console.log('Validation errors:');
  errors.forEach(e => console.log(`  - ${e}`));
  process.exit(1);
}
```

---

## Related

- [SKILL.md](SKILL.md) - Workflow structure overview
- [NODE_REFERENCE.md](NODE_REFERENCE.md) - Node configurations
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete examples
