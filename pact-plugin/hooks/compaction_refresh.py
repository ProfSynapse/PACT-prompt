#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/compaction_refresh.py
Summary: SessionStart hook that detects post-compaction sessions and injects refresh instructions.
Used by: Claude Code hooks.json SessionStart hook (after session_init.py)

This hook fires on SessionStart. It checks if the session was triggered by compaction
(source="compact") and if so, reads the checkpoint file created by precompact_refresh.py.
If an active workflow was in progress, it injects refresh instructions into the session
context to help the orchestrator resume seamlessly.

Input: JSON from stdin with:
  - source: Session start source ("compact" for post-compaction, others for normal start)

Output: JSON with hookSpecificOutput.additionalContext (refresh instructions if applicable)

Checkpoint location: ~/.claude/pact-refresh/{encoded-path}.json
"""

import json
import os
import sys
from pathlib import Path


def get_encoded_project_path_from_env() -> str | None:
    """
    Derive the encoded project path from CLAUDE_PROJECT_DIR.

    Converts /Users/mj/Sites/collab/PACT-prompt to -Users-mj-Sites-collab-PACT-prompt

    Note: The leading dash is intentional - it matches how Claude Code encodes
    project paths in the ~/.claude/projects/ directory structure.

    Returns:
        The encoded project path, or None if CLAUDE_PROJECT_DIR not set
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return None

    # Convert path to encoded form: replace all / with -
    # This preserves the leading dash from "/Users/..." -> "-Users-..."
    encoded = project_dir.replace("/", "-")
    return encoded


def get_checkpoint_path(encoded_path: str) -> Path:
    """
    Get the full checkpoint file path for a project.

    Args:
        encoded_path: The encoded project path segment

    Returns:
        Path to the checkpoint file
    """
    return Path.home() / ".claude" / "pact-refresh" / f"{encoded_path}.json"


def read_checkpoint(checkpoint_path: Path) -> dict | None:
    """
    Read and parse the checkpoint file.

    Args:
        checkpoint_path: Path to the checkpoint file

    Returns:
        Parsed checkpoint data, or None if file doesn't exist or is invalid
    """
    try:
        if not checkpoint_path.exists():
            return None
        content = checkpoint_path.read_text(encoding='utf-8')
        return json.loads(content)
    except (IOError, json.JSONDecodeError):
        return None


def validate_checkpoint(checkpoint: dict, current_session_id: str) -> bool:
    """
    Validate that the checkpoint is applicable to the current session.

    Checks:
    - Session ID matches (compaction preserves session ID)
    - Checkpoint has required fields
    - Version is supported

    Args:
        checkpoint: The checkpoint data
        current_session_id: Current session ID from environment

    Returns:
        True if checkpoint is valid and applicable
    """
    if not checkpoint:
        return False

    # Check version
    version = checkpoint.get("version", "")
    if not version.startswith("1."):
        return False

    # Check session ID matches
    checkpoint_session = checkpoint.get("session_id", "")
    if checkpoint_session != current_session_id:
        return False

    # Check workflow field exists
    if "workflow" not in checkpoint:
        return False

    return True


def build_refresh_message(checkpoint: dict) -> str:
    """
    Build the refresh instruction message for the orchestrator.

    Args:
        checkpoint: The validated checkpoint data

    Returns:
        Formatted refresh message string
    """
    workflow = checkpoint.get("workflow", {})
    workflow_name = workflow.get("name", "unknown")
    workflow_id = workflow.get("id", "")

    step = checkpoint.get("step", {})
    step_name = step.get("name", "unknown")

    extraction = checkpoint.get("extraction", {})
    confidence = extraction.get("confidence", 0)
    confidence_label = "high" if confidence >= 0.7 else "medium" if confidence >= 0.4 else "low"

    # Build context summary
    context = checkpoint.get("context", {})
    context_lines = []
    for key, value in context.items():
        context_lines.append(f"- {key}: {value}")

    # Build pending action section
    pending_action = checkpoint.get("pending_action", {})
    action_section = ""
    if pending_action:
        action_type = pending_action.get("type", "")
        instruction = pending_action.get("instruction", "")
        if action_type and instruction:
            action_section = f"""
NEXT ACTION REQUIRED:
{action_type}: {instruction}
"""

    # Assemble the message
    workflow_display = workflow_name
    if workflow_id:
        workflow_display = f"{workflow_name} ({workflow_id})"

    message_parts = [
        "=== WORKFLOW REFRESH ===",
        "",
        "Session resumed after compaction.",
        f"Active workflow: {workflow_display}",
        f"Checkpoint: {step_name}",
        f"Confidence: {confidence:.1f} ({confidence_label})",
    ]

    if action_section:
        message_parts.append(action_section.strip())

    if context_lines:
        message_parts.append("")
        message_parts.append("Context:")
        message_parts.extend(context_lines)

    message_parts.append("")
    message_parts.append("Resume workflow from this checkpoint.")
    message_parts.append("===========================")

    return "\n".join(message_parts)


def main():
    """
    Main entry point for the SessionStart refresh hook.

    Checks if this is a post-compaction session and injects refresh instructions
    if an active workflow was in progress.
    """
    try:
        # Parse input
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            input_data = {}

        source = input_data.get("source", "")

        # Only act on post-compaction sessions
        if source != "compact":
            # Not a post-compaction session, no action needed
            sys.exit(0)

        # Get session ID and project path
        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
        encoded_path = get_encoded_project_path_from_env()

        if not encoded_path:
            # Cannot determine project, skip refresh
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "Refresh skipped: project path unavailable"
                }
            }))
            sys.exit(0)

        # Read checkpoint
        checkpoint_path = get_checkpoint_path(encoded_path)
        checkpoint = read_checkpoint(checkpoint_path)

        if not checkpoint:
            # No checkpoint file, nothing to recover
            sys.exit(0)

        # Validate checkpoint
        if not validate_checkpoint(checkpoint, session_id):
            # Checkpoint invalid or from different session
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "Refresh skipped: checkpoint validation failed"
                }
            }))
            sys.exit(0)

        # Check if there was an active workflow
        workflow_name = checkpoint.get("workflow", {}).get("name", "none")
        if workflow_name == "none":
            # No active workflow at compaction time
            sys.exit(0)

        # Build and inject refresh instructions
        refresh_message = build_refresh_message(checkpoint)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": refresh_message
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Never fail the hook - log and exit cleanly
        print(f"Compaction refresh hook warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
