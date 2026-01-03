#!/bin/bash
# Hook: PreToolUse (matcher: Task)
# Updates kanban state when a subagent is spawned

set -e

KANBAN_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/kanban"
STATE_FILE="$KANBAN_DIR/state.json"

# Read hook input from stdin
INPUT=$(cat)

# Extract task info from JSON input
# tool_input contains: description, prompt, subagent_type
DESCRIPTION=$(echo "$INPUT" | grep -o '"description":"[^"]*"' | head -1 | cut -d'"' -f4)
AGENT_TYPE=$(echo "$INPUT" | grep -o '"subagent_type":"[^"]*"' | head -1 | cut -d'"' -f4)
PROMPT=$(echo "$INPUT" | grep -o '"prompt":"[^"]*"' | head -1 | cut -d'"' -f4 | head -c 500)

# Generate task ID
TASK_ID="task-$(date +%s)-$$"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Ensure state file exists
if [ ! -f "$STATE_FILE" ]; then
  echo '{"session":{"id":null,"started_at":null},"agents":{},"tasks":[]}' > "$STATE_FILE"
fi

# Create new task entry
NEW_TASK=$(cat <<EOF
{
  "id": "$TASK_ID",
  "description": "$DESCRIPTION",
  "agent": "$AGENT_TYPE",
  "prompt": "$PROMPT",
  "status": "running",
  "started_at": "$TIMESTAMP",
  "completed_at": null,
  "result": null
}
EOF
)

# Update state file using a temp file for atomicity
TEMP_FILE=$(mktemp)

# Use Python for reliable JSON manipulation (jq may not be available)
python3 << PYTHON
import json
import sys

try:
    with open("$STATE_FILE", "r") as f:
        state = json.load(f)
except:
    state = {"session": {"id": None, "started_at": None}, "agents": {}, "tasks": []}

# Add new task
new_task = {
    "id": "$TASK_ID",
    "description": "$DESCRIPTION",
    "agent": "$AGENT_TYPE",
    "prompt": """$PROMPT""",
    "status": "running",
    "started_at": "$TIMESTAMP",
    "completed_at": None,
    "result": None
}
state["tasks"].append(new_task)

# Update agent status
agent = "$AGENT_TYPE" or "unknown"
state["agents"][agent] = {"status": "busy", "current_task": "$TASK_ID"}

with open("$TEMP_FILE", "w") as f:
    json.dump(state, f, indent=2)
PYTHON

mv "$TEMP_FILE" "$STATE_FILE"

# Output for Claude's context
echo "Kanban: Started task $TASK_ID ($AGENT_TYPE)"

exit 0
