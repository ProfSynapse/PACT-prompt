#!/bin/bash
# Hook: PreToolUse (matcher: Task)
# Updates kanban state when a subagent is spawned

KANBAN_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/kanban"
STATE_FILE="$KANBAN_DIR/state.json"

# Read hook input from stdin
INPUT=$(cat)

TASK_ID="task-$(date +%s)-$$"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Ensure kanban directory and state file exist
mkdir -p "$KANBAN_DIR"
if [ ! -f "$STATE_FILE" ]; then
  echo '{"session":{"id":null,"started_at":null},"agents":{},"tasks":[]}' > "$STATE_FILE"
fi

# Update state file
TEMP_FILE=$(mktemp)

STATE_FILE="$STATE_FILE" TEMP_FILE="$TEMP_FILE" TASK_ID="$TASK_ID" TIMESTAMP="$TIMESTAMP" INPUT="$INPUT" python3 << 'PYTHON'
import json
import sys
import os

state_file = os.environ['STATE_FILE']
temp_file = os.environ['TEMP_FILE']
task_id = os.environ['TASK_ID']
timestamp = os.environ['TIMESTAMP']
input_json = os.environ.get('INPUT', '{}')

try:
    with open(state_file, "r") as f:
        state = json.load(f)
except:
    state = {"session": {"id": None, "started_at": None}, "agents": {}, "tasks": []}

# Parse the hook input
try:
    hook_input = json.loads(input_json)
    tool_input = hook_input.get("tool_input", {})
    description = tool_input.get("description", "")
    prompt = tool_input.get("prompt", "")
    agent_type = tool_input.get("subagent_type", "unknown")
except Exception as e:
    description = ""
    prompt = ""
    agent_type = "unknown"

# Add new task
new_task = {
    "id": task_id,
    "description": description,
    "agent": agent_type,
    "prompt": prompt,
    "status": "running",
    "started_at": timestamp,
    "completed_at": None,
    "agent_id": None,
    "transcript_path": None
}
state["tasks"].append(new_task)

# Update agent status
state["agents"][agent_type] = {"status": "busy", "current_task": task_id}

with open(temp_file, "w") as f:
    json.dump(state, f, indent=2)

print(f"Kanban: Started task {task_id} ({agent_type})")
PYTHON

mv "$TEMP_FILE" "$STATE_FILE"
exit 0
