#!/bin/bash
# Test hook - logs to file when triggered
# Receives JSON on stdin with hook context

LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/hook_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Read stdin (hook context JSON)
INPUT=$(cat)

# Extract hook info
TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name":"[^"]*"' | cut -d'"' -f4)
HOOK_TYPE="${CLAUDE_HOOK_TYPE:-unknown}"

# Log it
echo "[$TIMESTAMP] Hook: $HOOK_TYPE | Tool: $TOOL_NAME" >> "$LOG_FILE"

# Also output to stdout so it shows in Claude's context
echo "Hook fired: $HOOK_TYPE for $TOOL_NAME"

exit 0
