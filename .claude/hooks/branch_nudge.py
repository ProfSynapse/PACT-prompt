#!/usr/bin/env python3
"""
Location: .claude/hooks/branch_nudge.py
Summary: PostToolUse hook that reminds the AI to use feature branches and push changes.
Used by: Claude Code settings.json PostToolUse hook (Edit, Write tools)

Checks:
- If on main/master branch -> warn to create feature branch
- Tracks edit count and reminds to push periodically (threshold: 10 edits)

Input: JSON from stdin with tool_name, tool_input, tool_output
Output: JSON with systemMessage to stdout if nudge needed
"""

import json
import os
import subprocess
import sys
from pathlib import Path


# Hook version for tracking updates
HOOK_VERSION = "1.0.0"

# Number of edits before reminding to push
PUSH_REMINDER_THRESHOLD = 10

# Protected branches that should trigger a warning
PROTECTED_BRANCHES = {"main", "master"}

# Directory for tracking edit count
TRACKING_DIR = Path.home() / ".claude" / "pact-memory" / "session-tracking"


def get_current_branch() -> str:
    """
    Get the name of the current git branch.

    Returns:
        Branch name or empty string if not in a git repo
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def is_git_repo() -> bool:
    """Check if we're in a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def has_unpushed_commits() -> bool:
    """
    Check if there are commits that haven't been pushed to remote.

    Returns:
        True if there are unpushed commits, False otherwise
    """
    try:
        # Get current branch
        branch = get_current_branch()
        if not branch:
            return False

        # Check if remote tracking branch exists
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # No upstream branch, so any local commits are unpushed
            local_commits = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return local_commits.returncode == 0 and bool(local_commits.stdout.strip())

        # Check for commits ahead of upstream
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{branch}@{{upstream}}..HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return int(result.stdout.strip()) > 0

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError, ValueError):
        return False


def get_edit_count_file() -> Path:
    """Get the file path for tracking edit counts in this session."""
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    return TRACKING_DIR / f"{session_id}_edit_count.json"


def load_edit_count() -> dict:
    """Load the current edit count for this session."""
    edit_file = get_edit_count_file()
    if edit_file.exists():
        try:
            with open(edit_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "count": 0,
        "last_push_reminder_at": 0,
        "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown")
    }


def save_edit_count(data: dict):
    """Save the edit count for this session."""
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    edit_file = get_edit_count_file()
    try:
        with open(edit_file, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save edit count: {e}", file=sys.stderr)


def increment_edit_count() -> int:
    """
    Increment the edit count and return the new value.

    Returns:
        The new edit count after incrementing
    """
    data = load_edit_count()
    data["count"] += 1
    save_edit_count(data)
    return data["count"]


def should_remind_push(current_count: int) -> bool:
    """
    Determine if we should remind to push based on edit count.

    We remind after every PUSH_REMINDER_THRESHOLD edits since the last reminder.

    Args:
        current_count: The current edit count

    Returns:
        True if a push reminder should be shown
    """
    if current_count < PUSH_REMINDER_THRESHOLD:
        return False

    data = load_edit_count()
    last_reminder = data.get("last_push_reminder_at", 0)

    # Check if we've crossed a threshold since last reminder
    if current_count - last_reminder >= PUSH_REMINDER_THRESHOLD:
        # Update the last reminder count
        data["last_push_reminder_at"] = current_count
        save_edit_count(data)
        return True

    return False


def build_nudge_message() -> str:
    """
    Build the appropriate nudge message based on current git state.

    Returns:
        A message string to send to the AI, or empty string if no nudge needed
    """
    messages = []

    # Check if in git repo
    if not is_git_repo():
        return ""

    # Check if on protected branch
    branch = get_current_branch()
    if branch in PROTECTED_BRANCHES:
        messages.append(
            f"You are on the '{branch}' branch. Consider creating a feature branch "
            "with `git checkout -b <feature-name>` before making more changes."
        )

    # Track edits and check if push reminder is due
    edit_count = increment_edit_count()

    if should_remind_push(edit_count):
        if has_unpushed_commits():
            messages.append(
                f"You have made {edit_count} edits this session with unpushed commits. "
                "Consider pushing your changes to remote with `git push`."
            )

    if messages:
        return " | ".join(messages)

    return ""


def main():
    """Main entry point for the PostToolUse hook."""
    try:
        # Read input from stdin
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        tool_name = input_data.get("tool_name", "")

        # Only process Edit and Write tools
        if tool_name not in ("Edit", "Write"):
            sys.exit(0)

        # Build nudge message based on git state
        nudge_message = build_nudge_message()

        if nudge_message:
            # Output the system message for Claude Code
            print(json.dumps({"systemMessage": nudge_message}))

        sys.exit(0)

    except Exception as e:
        # Don't block on errors - just log and exit cleanly
        print(f"Hook warning (branch_nudge): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
