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
from typing import Callable

# Import shared utilities from refresh package
_hooks_dir = Path(__file__).parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

# Import constants for consistent thresholds (Item 3)
try:
    from refresh.constants import CONFIDENCE_LABEL_HIGH, CONFIDENCE_LABEL_MEDIUM
except ImportError:
    # Fallback thresholds if constants not available
    CONFIDENCE_LABEL_HIGH = 0.8
    CONFIDENCE_LABEL_MEDIUM = 0.5

# Mapping of terse context keys to verbose equivalents for refresh messages
# This helps AI understand what each key means when resuming after compaction
# Duplicated here for fallback when refresh package not available
CONTEXT_KEY_VERBOSE = {
    "reviewers": "reviewers_completed",
    "blocking": "blocking_issues",
    "round": "review_round",
    "pr_number": "pr_number",  # already clear
    "phase": "current_phase",
    "feature": "feature_name",
    "branch": "branch_name",
    "plan_file": "plan_file",  # already clear
    "has_blocking": "has_blocking_issues",
    "minor_count": "minor_issues_count",
    "future_count": "future_recommendations_count",
}

# Step descriptions for refresh messages (fallback when refresh package not available)
# Duplicated from refresh.constants for standalone use
STEP_DESCRIPTIONS_FALLBACK = {
    # peer-review steps
    "commit": "Committing changes to git",
    "create-pr": "Creating pull request",
    "invoke-reviewers": "Launching reviewer agents in parallel",
    "synthesize": "Synthesizing reviewer findings",
    "recommendations": "Processing review recommendations",
    "merge-ready": "All reviews complete, PR ready for merge authorization",
    "awaiting-merge": "Waiting for user to authorize merge",
    "awaiting_user_decision": "Waiting for user decision",
    # orchestrate steps
    "variety-assess": "Assessing task complexity and variety",
    "prepare": "Running PREPARE phase - research and requirements",
    "architect": "Running ARCHITECT phase - system design",
    "code": "Running CODE phase - implementation",
    "test": "Running TEST phase - testing and QA",
    # plan-mode steps
    "analyze": "Analyzing scope and selecting specialists",
    "consult": "Consulting specialists for planning perspectives",
    "present": "Presenting plan for user approval",
    # comPACT steps
    "invoking-specialist": "Delegating to specialist agent",
    "specialist-completed": "Specialist work completed",
    # rePACT (nested) steps
    "nested-prepare": "Running nested PREPARE phase",
    "nested-architect": "Running nested ARCHITECT phase",
    "nested-code": "Running nested CODE phase",
    "nested-test": "Running nested TEST phase",
}

# Item 4 & 9: Explicit type annotation for get_checkpoint_path
# Restructured to avoid defining unused fallback when shared utils are available
get_checkpoint_path: Callable[[str], Path]
checkpoint_to_refresh_message: Callable[[dict], str] | None = None

try:
    from refresh.checkpoint_builder import (
        get_checkpoint_path as _shared_get_checkpoint_path,
        checkpoint_to_refresh_message as _shared_checkpoint_to_refresh_message,
    )
    get_checkpoint_path = _shared_get_checkpoint_path
    checkpoint_to_refresh_message = _shared_checkpoint_to_refresh_message
    _USE_SHARED_UTILS = True
except ImportError:
    _USE_SHARED_UTILS = False
    # Only define fallback when shared utils are not available
    def _get_checkpoint_path_fallback(encoded_path: str) -> Path:
        """Fallback if refresh package not available."""
        return Path.home() / ".claude" / "pact-refresh" / f"{encoded_path}.json"

    get_checkpoint_path = _get_checkpoint_path_fallback


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


def _build_refresh_message_fallback(checkpoint: dict) -> str:
    """
    Fallback: Build the directive prompt refresh message for the orchestrator (~50-60 tokens).

    Used when refresh package is not available.

    Format:
        [WORKFLOW REFRESH]
        Context auto-compaction occurred. Resume the PACT workflow below, following framework protocols.
        You are resuming: {workflow_name} ({workflow_id})
        State: {step_name} — {step_description}
        Context: key=value, ... (only if context exists)
        Action: {pending_action.instruction} (only if pending action exists)
        Confidence: X.X. Verify with user if context seems outdated.

    Args:
        checkpoint: The validated checkpoint data

    Returns:
        Directive prompt formatted refresh message string
    """
    workflow = checkpoint.get("workflow", {})
    workflow_name = workflow.get("name", "unknown")
    workflow_id = workflow.get("id", "")

    step = checkpoint.get("step", {})
    step_name = step.get("name", "unknown")

    extraction = checkpoint.get("extraction", {})
    confidence = extraction.get("confidence", 0)

    context = checkpoint.get("context", {})
    pending_action = checkpoint.get("pending_action", {})

    lines = ["[WORKFLOW REFRESH]"]

    # Line 2: Explanatory line with framework emphasis
    lines.append("Context auto-compaction occurred. Resume the PACT workflow below, following framework protocols.")

    # Line 3: You are resuming: workflow (id)
    if workflow_id:
        lines.append(f"You are resuming: {workflow_name} ({workflow_id})")
    else:
        lines.append(f"You are resuming: {workflow_name}")

    # Line 4: State with description (if available)
    step_desc = STEP_DESCRIPTIONS_FALLBACK.get(step_name)
    if step_desc:
        lines.append(f"State: {step_name} — {step_desc}")
    else:
        lines.append(f"State: {step_name}")

    # Line 5: Context (only if present) - use verbose key names
    if context:
        context_parts = [
            f"{CONTEXT_KEY_VERBOSE.get(k, k)}={v}"
            for k, v in context.items()
        ]
        lines.append(f"Context: {', '.join(context_parts)}")

    # Line 6: Action (only if pending action exists)
    if pending_action:
        instruction = pending_action.get("instruction", "")
        if instruction:
            lines.append(f"Action: {instruction}")

    # Line 7: Confidence guidance
    lines.append(f"Confidence: {confidence:.1f}. Verify with user if context seems outdated.")

    return "\n".join(lines)


def build_refresh_message(checkpoint: dict) -> str:
    """
    Build the refresh instruction message for the orchestrator.

    Uses shared checkpoint_to_refresh_message if available (Fix 2),
    falls back to local implementation otherwise.

    Args:
        checkpoint: The validated checkpoint data

    Returns:
        Formatted refresh message string
    """
    if _USE_SHARED_UTILS:
        return checkpoint_to_refresh_message(checkpoint)
    return _build_refresh_message_fallback(checkpoint)


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
