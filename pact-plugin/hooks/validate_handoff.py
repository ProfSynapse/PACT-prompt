#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/validate_handoff.py
Summary: SubagentStop hook that validates PACT agent handoff format and Task protocol.
Used by: Claude Code settings.json SubagentStop hook

Validates that PACT agents:
1. Complete with proper handoff information (produced, decisions, next steps)
2. Reported completion via structured HANDOFF text (orchestrator handles TaskUpdate)

Input: JSON from stdin with `transcript`, `agent_id`, and optionally `task_id`
Output: JSON with `systemMessage` if handoff format is incomplete or Task protocol violated
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Any


# Required handoff elements with their patterns and descriptions
HANDOFF_ELEMENTS = {
    "what_produced": {
        "patterns": [
            r"(?:produced|created|generated|output|implemented|wrote|built|delivered)",
            r"(?:file|document|component|module|function|class|api|endpoint|schema)",
            r"(?:completed|finished|done with)",
        ],
        "description": "what was produced",
    },
    "key_decisions": {
        "patterns": [
            r"(?:decision|chose|selected|opted|rationale|reason|because)",
            r"(?:trade-?off|alternative|approach|strategy|pattern)",
            r"(?:decided to|went with|picked)",
        ],
        "description": "key decisions",
    },
    "next_steps": {
        "patterns": [
            r"(?:next|needs|requires|depends|should|must|recommend)",
            r"(?:follow-?up|remaining|todo|to-?do|action item)",
            r"(?:test engineer|tester|reviewer|next agent|next phase)",
        ],
        "description": "next steps/needs",
    },
}

# Required metadata fields for Task completion
REQUIRED_TASK_METADATA = ["produced", "decisions"]


def validate_handoff(transcript: str) -> tuple:
    """
    Check if transcript contains proper handoff elements.

    Args:
        transcript: The agent's complete output/transcript

    Returns:
        Tuple of (is_valid, missing_elements)
    """
    missing = []

    # First, check for explicit handoff section (indicates structured handoff)
    has_handoff_section = bool(re.search(
        r"(?:##?\s*)?(?:handoff|hand-off|hand off|summary|output|deliverables)[\s:]*\n",
        transcript,
        re.IGNORECASE
    ))

    # If there's an explicit handoff section, be more lenient
    if has_handoff_section:
        return True, []

    # Otherwise, check for implicit handoff elements
    transcript_lower = transcript.lower()

    for element_key, element_info in HANDOFF_ELEMENTS.items():
        found = False
        for pattern in element_info["patterns"]:
            if re.search(pattern, transcript_lower):
                found = True
                break

        if not found:
            missing.append(element_info["description"])

    # Consider valid if at least 2 out of 3 elements are present
    # (some agents may not have explicit decisions if straightforward)
    is_valid = len(missing) <= 1

    return is_valid, missing


def is_pact_agent(agent_id: str) -> bool:
    """
    Check if the agent is a PACT framework agent.

    Args:
        agent_id: The identifier of the agent

    Returns:
        True if this is a PACT agent that should be validated
    """
    if not agent_id:
        return False

    pact_prefixes = ["pact-", "PACT-", "pact_", "PACT_"]
    return any(agent_id.startswith(prefix) for prefix in pact_prefixes)


# -----------------------------------------------------------------------------
# Task Protocol Validation (Task System Integration)
# -----------------------------------------------------------------------------

def get_task_by_id(task_id: str) -> dict[str, Any] | None:
    """
    Read a specific task from the Task system by ID.

    Tasks are stored at ~/.claude/tasks/{sessionId}/{taskId}.json.

    Args:
        task_id: The task ID to look up

    Returns:
        Task dict, or None if not found
    """
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    task_list_id = os.environ.get("CLAUDE_CODE_TASK_LIST_ID", session_id)

    if not task_list_id or not task_id:
        return None

    # Try to find the task file
    tasks_dir = Path.home() / ".claude" / "tasks" / task_list_id

    # Task files might be named by ID or contain the ID in metadata
    # Try direct lookup first
    task_file = tasks_dir / f"{task_id}.json"
    if task_file.exists():
        try:
            content = task_file.read_text(encoding='utf-8')
            return json.loads(content)
        except (IOError, json.JSONDecodeError):
            pass

    # Fall back to scanning all tasks
    if tasks_dir.exists():
        try:
            for f in tasks_dir.glob("*.json"):
                try:
                    content = f.read_text(encoding='utf-8')
                    task = json.loads(content)
                    if task.get("id") == task_id:
                        return task
                except (IOError, json.JSONDecodeError):
                    continue
        except Exception:
            pass

    return None


def validate_task_completion(agent_id: str, task_id: str) -> tuple[bool, list[str]]:
    """
    Validate that the agent properly completed its Task.

    Checks:
    1. Task status was updated to "completed"
    2. Task metadata contains required handoff fields (produced, decisions)

    Args:
        agent_id: The agent identifier
        task_id: The task ID assigned to the agent

    Returns:
        Tuple of (is_valid, list of warnings)
    """
    warnings = []

    task = get_task_by_id(task_id)
    if task is None:
        # Can't find task - might be Task system unavailable or ID invalid
        # Don't warn harshly, just note it
        return True, []  # Assume valid if we can't check

    # Check status was updated
    status = task.get("status", "")
    if status != "completed":
        warnings.append(
            f"Agent '{agent_id}' did not mark Task {task_id} as completed (status: {status})"
        )

    # Check metadata contains required handoff fields
    metadata = task.get("metadata") or {}
    missing_fields = [f for f in REQUIRED_TASK_METADATA if f not in metadata]

    if missing_fields:
        warnings.append(
            f"Agent '{agent_id}' Task metadata missing: {', '.join(missing_fields)}"
        )

    is_valid = len(warnings) == 0
    return is_valid, warnings


def main():
    """
    Main entry point for the SubagentStop hook.

    Reads agent transcript from stdin, validates both:
    1. Handoff format (prose) for PACT agents
    2. Task protocol compliance (if task_id provided)

    Outputs warning messages if validation fails.
    """
    try:
        # Read input from stdin
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            # No input or invalid JSON - can't validate
            sys.exit(0)

        transcript = input_data.get("transcript", "")
        agent_id = input_data.get("agent_id", "")
        task_id = input_data.get("task_id", "")

        # Only validate PACT agents
        if not is_pact_agent(agent_id):
            sys.exit(0)

        warnings = []

        # Skip transcript validation if very short (likely an error case)
        if len(transcript) >= 100:
            is_valid, missing = validate_handoff(transcript)

            if not is_valid and missing:
                warnings.append(
                    f"PACT Handoff Warning: Agent '{agent_id}' completed without "
                    f"proper handoff. Missing: {', '.join(missing)}. "
                    "Consider including: what was produced, key decisions, and next steps."
                )

        # Validate Task protocol if task_id was provided
        if task_id:
            task_valid, task_warnings = validate_task_completion(agent_id, task_id)
            warnings.extend(task_warnings)

        # Output warnings if any
        if warnings:
            output = {
                "systemMessage": " | ".join(warnings)
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Don't block on errors - just warn
        print(f"Hook warning (validate_handoff): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
