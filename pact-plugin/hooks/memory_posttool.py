#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/memory_posttool.py
Summary: PostToolUse hook that reminds agent to consider saving memory after edits.
Used by: Claude Code settings.json PostToolUse hook (Edit, Write tools)

PHILOSOPHY: Bias toward saving memories. Since pact-memory-agent runs in
background, there's no workflow interruption cost. Better to save too much
than lose context.

Always fires after Edit/Write to provide contextual guidance. The agent
decides based on whether they've completed a unit of work or are mid-task.

Input: JSON from stdin with tool_name, tool_input, tool_output
Output: JSON with `hookSpecificOutput.additionalContext` on every edit
"""

import json
import sys

# Paths to truly exclude (only transient/generated files)
EXCLUDED_PATHS = [
    "__pycache__",
    "node_modules",
    ".git/",
    "*.log",
    "*.tmp",
    ".pyc",
    "dist/",
    "build/",
]


def is_excluded_path(file_path: str) -> bool:
    """Check if the file path should be excluded from memory prompts."""
    for pattern in EXCLUDED_PATHS:
        if pattern in file_path:
            return True
    return False


def format_prompt() -> str:
    """Format the memory prompt message with contextual guidance."""
    return (
        "📝 Memory check: If you just completed a unit of work (finished a task, "
        "made a decision, learned something, resolved a problem), save it now. "
        "If you're mid-task with more edits coming, continue working. "
        "Bias: when in doubt, save."
    )


def main():
    """Main entry point for the PostToolUse hook."""
    try:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Edit and Write tools
        if tool_name not in ("Edit", "Write"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Skip transient/generated files
        if is_excluded_path(file_path):
            sys.exit(0)

        # Always output the prompt with contextual guidance
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": format_prompt()
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Don't block on errors
        print(f"PACT Hook [WARNING] (memory_posttool): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
