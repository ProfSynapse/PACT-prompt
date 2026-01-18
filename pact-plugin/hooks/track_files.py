#!/usr/bin/env python3
"""
Location: .claude/hooks/track_files.py
Summary: PostToolUse hook that tracks files modified during the session.
Used by: Claude Code settings.json PostToolUse hook (Edit, Write tools)

Extracts file paths from Edit/Write tool usage and records them
for the memory system's graph network.

Input: JSON from stdin with tool_name, tool_input, tool_output
Output: None (writes to tracking file for later memory association)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# Directory for tracking data
TRACKING_DIR = Path.home() / ".claude" / "pact-memory" / "session-tracking"


def ensure_tracking_dir():
    """Ensure the tracking directory exists."""
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)


def get_session_tracking_file() -> Path:
    """Get the tracking file for the current session."""
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    return TRACKING_DIR / f"{session_id}.json"


def load_tracked_files() -> dict:
    """Load existing tracked files for this session."""
    tracking_file = get_session_tracking_file()
    if tracking_file.exists():
        try:
            with open(tracking_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"files": [], "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")}


def save_tracked_files(data: dict):
    """Save tracked files for this session."""
    ensure_tracking_dir()
    tracking_file = get_session_tracking_file()
    try:
        with open(tracking_file, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save tracking data: {e}", file=sys.stderr)


def extract_file_path(tool_input: dict) -> str:
    """Extract file path from tool input."""
    # Both Edit and Write use file_path parameter
    return tool_input.get("file_path", "")


def track_file(file_path: str, tool_name: str):
    """Add a file to the tracking list."""
    if not file_path:
        return

    data = load_tracked_files()

    # Check if already tracked
    existing_paths = [f["path"] for f in data["files"]]
    if file_path in existing_paths:
        # Update timestamp
        for f in data["files"]:
            if f["path"] == file_path:
                f["last_modified"] = datetime.now(timezone.utc).isoformat()
                f["tool"] = tool_name
                break
    else:
        # Add new entry
        data["files"].append({
            "path": file_path,
            "tool": tool_name,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "last_modified": datetime.now(timezone.utc).isoformat(),
        })

    save_tracked_files(data)


def main():
    """Main entry point for the PostToolUse hook."""
    try:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only track Edit and Write tools
        if tool_name not in ("Edit", "Write"):
            sys.exit(0)

        # Extract and track the file path
        file_path = extract_file_path(tool_input)
        if file_path:
            track_file(file_path, tool_name)

        sys.exit(0)

    except Exception as e:
        # Don't block on errors
        print(f"PACT Hook [WARNING] (track_files): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
