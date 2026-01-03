#!/bin/bash
# Hook: SubagentStop
# Updates kanban state when a subagent completes

set -e

KANBAN_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/kanban"
STATE_FILE="$KANBAN_DIR/state.json"

# Read hook input from stdin (contains subagent result)
INPUT=$(cat)

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Extract result snippet (first 500 chars for storage)
RESULT_SNIPPET=$(echo "$INPUT" | head -c 500 | tr '\n' ' ' | sed 's/"/\\"/g')

# Ensure state file exists
if [ ! -f "$STATE_FILE" ]; then
  echo "Kanban: No state file found"
  exit 0
fi

# Update state file - mark most recent running task as done
TEMP_FILE=$(mktemp)

python3 << PYTHON
import json

try:
    with open("$STATE_FILE", "r") as f:
        state = json.load(f)
except:
    print("Kanban: Could not read state")
    exit(0)

# Find the most recent running task and mark it done
running_tasks = [t for t in state["tasks"] if t["status"] == "running"]
if running_tasks:
    # Mark the most recent one as done
    task = running_tasks[-1]
    task["status"] = "done"
    task["completed_at"] = "$TIMESTAMP"
    task["result"] = """$RESULT_SNIPPET"""[:500] if """$RESULT_SNIPPET""" else None

    # Update agent status to idle
    agent = task.get("agent", "unknown")
    if agent in state["agents"]:
        state["agents"][agent] = {"status": "idle", "current_task": None}

with open("$TEMP_FILE", "w") as f:
    json.dump(state, f, indent=2)

print(f"Kanban: Completed task {task['id']}")
PYTHON

mv "$TEMP_FILE" "$STATE_FILE"

exit 0
