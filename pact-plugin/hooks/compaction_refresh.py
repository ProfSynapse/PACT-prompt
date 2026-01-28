#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/compaction_refresh.py
Summary: SessionStart hook that detects post-compaction sessions and injects refresh instructions.
Used by: Claude Code hooks.json SessionStart hook (after session_init.py)

This hook fires on SessionStart. It checks if the session was triggered by compaction
(source="compact") and if so, reads workflow state from TaskList (which survives compaction)
to build refresh context. If no TaskList is available, falls back to checkpoint file.

The Task system (TaskCreate, TaskUpdate, TaskGet, TaskList) is PACT's single source of truth
for workflow state. Tasks persist across compaction at ~/.claude/tasks/{sessionId}/*.json.

Input: JSON from stdin with:
  - source: Session start source ("compact" for post-compaction, others for normal start)

Output: JSON with hookSpecificOutput.additionalContext (refresh instructions if applicable)

Fallback checkpoint location: ~/.claude/pact-refresh/{encoded-path}.json
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Add hooks directory to path for refresh package imports
_hooks_dir = Path(__file__).parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

# Import checkpoint utilities from refresh package (always available - same directory)
# These are used as fallback when TaskList is unavailable
from refresh.checkpoint_builder import (
    get_checkpoint_path,
    get_encoded_project_path,
    checkpoint_to_refresh_message,
)


# -----------------------------------------------------------------------------
# Task System Integration (Primary State Source)
# -----------------------------------------------------------------------------

def get_task_list() -> list[dict[str, Any]] | None:
    """
    Read TaskList from the Claude Task system.

    Tasks are stored at ~/.claude/tasks/{sessionId}/*.json and survive compaction.
    This function reads directly from the filesystem since hooks cannot call Task tools.

    Returns:
        List of task dicts, or None if tasks unavailable
    """
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    # Also check for multi-session task list ID
    task_list_id = os.environ.get("CLAUDE_CODE_TASK_LIST_ID", session_id)

    if not task_list_id:
        return None

    tasks_dir = Path.home() / ".claude" / "tasks" / task_list_id
    if not tasks_dir.exists():
        return None

    tasks = []
    try:
        for task_file in tasks_dir.glob("*.json"):
            try:
                content = task_file.read_text(encoding='utf-8')
                task = json.loads(content)
                tasks.append(task)
            except (IOError, json.JSONDecodeError):
                continue
    except Exception:
        return None

    return tasks if tasks else None


def find_feature_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Find the main Feature task from the task list.

    Feature tasks are top-level tasks that represent the overall work item.
    They can be identified by:
    - Having no blockedBy (top-level)
    - Subject starting with a verb (e.g., "Implement user auth")
    - OR having phase tasks as children

    Args:
        tasks: List of all tasks

    Returns:
        Feature task dict, or None if not found
    """
    # Look for tasks with no blockedBy that have children
    task_ids = {t.get("id") for t in tasks if t.get("id")}
    blocked_by_ids = set()
    for task in tasks:
        blocked_by = task.get("blockedBy", [])
        if blocked_by:
            blocked_by_ids.update(blocked_by)

    # Feature task is one that blocks others but isn't blocked itself
    # (or has status in_progress at top level)
    for task in tasks:
        task_id = task.get("id")
        if not task_id:
            continue

        # Skip if this task is blocked by something
        if task.get("blockedBy"):
            continue

        # Check if it's a feature-like task (not a phase task)
        subject = task.get("subject", "")
        # Phase tasks start with phase names
        phase_prefixes = ("PREPARE:", "ARCHITECT:", "CODE:", "TEST:", "Review:")
        if any(subject.startswith(p) for p in phase_prefixes):
            continue

        # This looks like a feature task
        if task.get("status") in ("in_progress", "pending"):
            return task

    return None


def find_current_phase(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Find the currently active phase task.

    Phase tasks follow the pattern: "{PHASE}: {feature-slug}"
    The current phase is the one with status "in_progress".

    Args:
        tasks: List of all tasks

    Returns:
        Phase task dict, or None if not found
    """
    phase_prefixes = ("PREPARE:", "ARCHITECT:", "CODE:", "TEST:")

    for task in tasks:
        subject = task.get("subject", "")
        if any(subject.startswith(p) for p in phase_prefixes):
            if task.get("status") == "in_progress":
                return task

    return None


def find_active_agents(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Find all currently active agent tasks.

    Agent tasks follow the pattern: "{agent-type}: {work-description}"
    and have status "in_progress".

    Args:
        tasks: List of all tasks

    Returns:
        List of agent task dicts
    """
    agent_prefixes = (
        "pact-preparer:",
        "pact-architect:",
        "pact-backend-coder:",
        "pact-frontend-coder:",
        "pact-database-engineer:",
        "pact-test-engineer:",
        "pact-memory-agent:",
        "pact-n8n:",
    )

    active = []
    for task in tasks:
        subject = task.get("subject", "").lower()
        if any(subject.startswith(p) for p in agent_prefixes):
            if task.get("status") == "in_progress":
                active.append(task)

    return active


def find_blockers(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Find any blocker or algedonic tasks.

    These are signal tasks created by agents when they hit blockers
    or detect viability threats.

    Args:
        tasks: List of all tasks

    Returns:
        List of blocker/algedonic task dicts
    """
    blockers = []
    for task in tasks:
        metadata = task.get("metadata", {})
        task_type = metadata.get("type", "")
        if task_type in ("blocker", "algedonic"):
            if task.get("status") != "completed":
                blockers.append(task)

    return blockers


def build_refresh_from_tasks(
    feature: dict[str, Any] | None,
    phase: dict[str, Any] | None,
    agents: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> str:
    """
    Build refresh context message from Task state.

    Generates a concise message describing the workflow state for
    the orchestrator to resume from.

    Args:
        feature: Feature task dict or None
        phase: Current phase task dict or None
        agents: List of active agent tasks
        blockers: List of active blocker tasks

    Returns:
        Formatted refresh message string
    """
    lines = ["[POST-COMPACTION CHECKPOINT]"]
    lines.append("Prior conversation auto-compacted. Resume from Task state below:")

    # Feature context
    if feature:
        feature_subject = feature.get("subject", "unknown feature")
        feature_id = feature.get("id", "")
        if feature_id:
            lines.append(f"Feature: {feature_subject} (id: {feature_id})")
        else:
            lines.append(f"Feature: {feature_subject}")
    else:
        lines.append("Feature: Unable to identify feature task")

    # Phase context
    if phase:
        phase_subject = phase.get("subject", "unknown phase")
        lines.append(f"Current Phase: {phase_subject}")
    else:
        lines.append("Current Phase: None detected")

    # Active agents
    if agents:
        agent_names = [a.get("subject", "unknown") for a in agents]
        lines.append(f"Active Agents ({len(agents)}): {', '.join(agent_names)}")
    else:
        lines.append("Active Agents: None")

    # Blockers (critical info)
    if blockers:
        lines.append("")
        lines.append("**BLOCKERS DETECTED:**")
        for blocker in blockers:
            subj = blocker.get("subject", "unknown blocker")
            meta = blocker.get("metadata", {})
            level = meta.get("level", "")
            if level:
                lines.append(f"  - {level}: {subj}")
            else:
                lines.append(f"  - {subj}")

    # Next step guidance
    lines.append("")
    if blockers:
        lines.append("Next Step: **Address blockers before proceeding.**")
    elif agents:
        lines.append("Next Step: Monitor active agents via TaskList, then proceed.")
    elif phase:
        lines.append("Next Step: Continue current phase or check agent completion.")
    else:
        lines.append("Next Step: **Check TaskList and ask user how to proceed.**")

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Checkpoint Fallback (Legacy State Source)
# -----------------------------------------------------------------------------

def read_checkpoint(checkpoint_path: Path) -> dict | None:
    """
    Read and parse the checkpoint file (fallback when Tasks unavailable).

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

    # Check version (handle None values)
    version = checkpoint.get("version", "")
    if not version or not version.startswith("1."):
        return False

    # Check session ID matches
    checkpoint_session = checkpoint.get("session_id", "")
    if checkpoint_session != current_session_id:
        return False

    # Check workflow field exists
    if "workflow" not in checkpoint:
        return False

    return True


def build_refresh_message_from_checkpoint(checkpoint: dict) -> str:
    """
    Build the refresh instruction message from checkpoint (fallback).

    Delegates to checkpoint_to_refresh_message from the refresh package.

    Args:
        checkpoint: The validated checkpoint data

    Returns:
        Formatted refresh message string
    """
    return checkpoint_to_refresh_message(checkpoint)


# Alias for backward compatibility with tests
build_refresh_message = build_refresh_message_from_checkpoint


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

def main():
    """
    Main entry point for the SessionStart refresh hook.

    Strategy:
    1. Primary: Read TaskList directly (Tasks survive compaction)
    2. Fallback: Read checkpoint file if TaskList unavailable

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

        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")

        # ---------------------------------------------------------------------
        # Primary: Try TaskList first (Tasks survive compaction)
        # ---------------------------------------------------------------------
        tasks = get_task_list()

        if tasks:
            # Find workflow state from Tasks
            in_progress = [t for t in tasks if t.get("status") == "in_progress"]

            if in_progress:
                feature_task = find_feature_task(tasks)
                current_phase = find_current_phase(tasks)
                active_agents = find_active_agents(tasks)
                blockers = find_blockers(tasks)

                refresh_message = build_refresh_from_tasks(
                    feature=feature_task,
                    phase=current_phase,
                    agents=active_agents,
                    blockers=blockers,
                )

                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": refresh_message
                    }
                }
                print(json.dumps(output))
                sys.exit(0)

            # Tasks exist but nothing in_progress - no active workflow
            sys.exit(0)

        # ---------------------------------------------------------------------
        # Fallback: Read checkpoint file (legacy approach)
        # ---------------------------------------------------------------------
        encoded_path = get_encoded_project_path("")

        if encoded_path == "unknown-project":
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

        # Build and inject refresh instructions from checkpoint
        refresh_message = build_refresh_message_from_checkpoint(checkpoint)

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
