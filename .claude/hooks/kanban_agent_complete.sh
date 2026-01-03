#!/bin/bash
# Hook: SubagentStop
# Updates kanban state when a subagent completes

KANBAN_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/kanban"
STATE_FILE="$KANBAN_DIR/state.json"

# Read hook input from stdin
INPUT=$(cat)

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Ensure state file exists
if [ ! -f "$STATE_FILE" ]; then
  echo "Kanban: No state file found"
  exit 0
fi

# Update state file
TEMP_FILE=$(mktemp)

STATE_FILE="$STATE_FILE" TEMP_FILE="$TEMP_FILE" TIMESTAMP="$TIMESTAMP" INPUT="$INPUT" python3 << 'PYTHON'
import json
import sys
import os

state_file = os.environ['STATE_FILE']
temp_file = os.environ['TEMP_FILE']
timestamp = os.environ['TIMESTAMP']
input_json = os.environ.get('INPUT', '{}')

try:
    with open(state_file, "r") as f:
        state = json.load(f)
except:
    print("Kanban: Could not read state")
    sys.exit(0)

# Parse the hook input to get agent info
try:
    hook_input = json.loads(input_json)
    agent_id = hook_input.get("agent_id", "")
    transcript_path = hook_input.get("agent_transcript_path", "")
except:
    agent_id = ""
    transcript_path = ""

# Find the most recent running task and mark it done
running_tasks = [t for t in state["tasks"] if t["status"] == "running"]
if running_tasks:
    task = running_tasks[-1]
    task["status"] = "done"
    task["completed_at"] = timestamp
    task["agent_id"] = agent_id
    task["transcript_path"] = transcript_path

    # Update agent status to idle
    agent = task.get("agent", "unknown")
    if agent in state["agents"]:
        state["agents"][agent] = {"status": "idle", "current_task": None}

    print(f"Kanban: Completed task {task['id']} (agent: {agent_id})")

with open(temp_file, "w") as f:
    json.dump(state, f, indent=2)
PYTHON

mv "$TEMP_FILE" "$STATE_FILE"
exit 0
