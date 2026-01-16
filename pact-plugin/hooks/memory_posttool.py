#!/usr/bin/env python3
"""
Location: .claude/hooks/memory_posttool.py
Summary: PostToolUse hook that prompts agent to save memory after significant edits.
Used by: Claude Code settings.json PostToolUse hook (Edit, Write tools)

Analyzes file edits and prompts the agent to consider saving to pact-memory
when significant application code changes are detected.

Input: JSON from stdin with tool_name, tool_input, tool_output
Output: JSON with `hookSpecificOutput.additionalContext` if edit is significant
"""

import json
import os
import sys
from pathlib import Path


# File extensions considered "application code" (worth remembering)
SIGNIFICANT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".rs", ".rb", ".java", ".kt",
    ".c", ".cpp", ".h", ".hpp",
    ".sh", ".bash",
    ".sql",
    ".tf", ".yaml", ".yml",  # Infrastructure
}

# Paths to exclude (not worth prompting for)
EXCLUDED_PATHS = [
    "CLAUDE.md",
    "/docs/",
    "/.claude/",
    "__pycache__",
    "node_modules",
    ".git/",
    "*.log",
    "*.tmp",
]

# Minimum lines changed to be considered "substantial"
MIN_LINES_THRESHOLD = 5


def is_excluded_path(file_path: str) -> bool:
    """Check if the file path should be excluded from memory prompts."""
    for pattern in EXCLUDED_PATHS:
        if pattern in file_path:
            return True
    return False


def is_significant_extension(file_path: str) -> bool:
    """Check if the file has a significant extension."""
    ext = Path(file_path).suffix.lower()
    return ext in SIGNIFICANT_EXTENSIONS


def estimate_change_size(tool_input: dict, tool_name: str) -> int:
    """Estimate the size of the change in lines."""
    if tool_name == "Write":
        content = tool_input.get("content", "")
        return content.count("\n") + 1
    elif tool_name == "Edit":
        new_string = tool_input.get("new_string", "")
        old_string = tool_input.get("old_string", "")
        # Estimate change as the difference in lines
        new_lines = new_string.count("\n") + 1
        old_lines = old_string.count("\n") + 1
        return abs(new_lines - old_lines) + min(new_lines, old_lines)
    return 0


def is_significant_edit(file_path: str, tool_input: dict, tool_name: str) -> bool:
    """Determine if an edit is significant enough to prompt for memory."""
    # Skip excluded paths
    if is_excluded_path(file_path):
        return False

    # Check for significant file type
    if not is_significant_extension(file_path):
        return False

    # Check change size
    change_size = estimate_change_size(tool_input, tool_name)
    if change_size < MIN_LINES_THRESHOLD:
        return False

    return True


def format_prompt(file_path: str, tool_name: str) -> str:
    """Format the memory prompt message."""
    filename = Path(file_path).name
    action = "created" if tool_name == "Write" else "modified"
    return (
        f"MANDATORY: Significant file {action}: {filename}. "
        f"You MUST delegate to pact-memory-agent after completing this task to save "
        f"context, lessons learned, and decisions. This is NOT optional."
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

        # Check if this edit is significant
        if is_significant_edit(file_path, tool_input, tool_name):
            prompt = format_prompt(file_path, tool_name)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": prompt
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Don't block on errors
        print(f"Hook warning (memory_posttool): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
