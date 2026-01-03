#!/bin/bash
# Test SubagentStop hook - logs when any subagent completes

LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/hook_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Read stdin (contains subagent result info)
INPUT=$(cat)

# Log it
echo "[$TIMESTAMP] SubagentStop fired" >> "$LOG_FILE"
echo "  Context: $INPUT" >> "$LOG_FILE"

# Output to stdout
echo "SubagentStop hook fired - subagent completed"

exit 0
