#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/memory_posttool.py
Summary: PostToolUse hook that prompts agent to save memory after edits.
Used by: Claude Code settings.json PostToolUse hook (Edit, Write tools)

PHILOSOPHY: Bias toward saving memories. Since pact-memory-agent runs in
background, there's no workflow interruption cost. Better to save too much
than lose context.

Tracks file edits and prompts for memory save after significant work.
The agent decides what's worth preserving - our job is just to remind.

Input: JSON from stdin with tool_name, tool_input, tool_output
Output: JSON with `hookSpecificOutput.additionalContext` when threshold met
"""

import json
import os
import sys
from pathlib import Path

# Track edits across hook invocations via temp file
EDIT_COUNTER_FILE = "/tmp/pact_edit_counter.txt"

# How many edits before prompting (low threshold - bias toward saving)
EDIT_THRESHOLD = 3

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


def get_edit_count() -> int:
    """Get current edit count from temp file."""
    try:
        if os.path.exists(EDIT_COUNTER_FILE):
            with open(EDIT_COUNTER_FILE, "r") as f:
                return int(f.read().strip())
    except (ValueError, IOError):
        pass
    return 0


def set_edit_count(count: int) -> None:
    """Set edit count in temp file."""
    try:
        with open(EDIT_COUNTER_FILE, "w") as f:
            f.write(str(count))
    except IOError:
        pass


def reset_edit_count() -> None:
    """Reset edit count after prompting."""
    set_edit_count(0)


def is_significant_edit(file_path: str) -> bool:
    """Determine if an edit should count toward the threshold."""
    # Only skip truly transient files
    return not is_excluded_path(file_path)


def format_prompt(edit_count: int) -> str:
    """Format the memory prompt message."""
    return (
        f"📝 Memory checkpoint: {edit_count}+ files edited. "
        f"Delegate to pact-memory-agent with run_in_background=true to save context. "
        f"Example: Task(subagent_type='pact-memory-agent', run_in_background=true, prompt='Save memory: ...')"
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

        # Count significant edits
        if is_significant_edit(file_path):
            current_count = get_edit_count() + 1
            set_edit_count(current_count)

            # Prompt when threshold reached
            if current_count >= EDIT_THRESHOLD:
                prompt = format_prompt(current_count)
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": prompt
                    }
                }
                print(json.dumps(output))
                # Reset counter after prompting
                reset_edit_count()

        sys.exit(0)

    except Exception as e:
        # Don't block on errors
        print(f"Hook warning (memory_posttool): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
