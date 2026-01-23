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
    from refresh.constants import CONFIDENCE_AUTO_PROCEED_THRESHOLD
except ImportError:
    # Fallback threshold if constants not available
    CONFIDENCE_AUTO_PROCEED_THRESHOLD = 0.8

# Try to import shared constants, fall back to local definitions only if unavailable
try:
    from refresh.shared_constants import STEP_DESCRIPTIONS, PROSE_CONTEXT_TEMPLATES
    _USE_SHARED_CONSTANTS = True
except ImportError:
    _USE_SHARED_CONSTANTS = False

    # Fallback: Step descriptions for refresh messages
    # Only used if shared_constants import fails
    STEP_DESCRIPTIONS = {
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

    # Fallback: Prose context generators
    def _prose_invoke_reviewers_fb(ctx: dict) -> str:
        """Generate prose for invoke-reviewers step."""
        reviewers = ctx.get("reviewers", "")
        blocking = ctx.get("blocking", "0")
        if "/" in str(reviewers):
            completed, total = str(reviewers).split("/")
            return f"Launched {total} reviewer agents; {completed} had completed with {blocking} blocking issues."
        elif reviewers:
            return f"Launched reviewer agents; {reviewers} had completed with {blocking} blocking issues."
        return "Was launching reviewer agents."

    def _prose_synthesize_fb(ctx: dict) -> str:
        """Generate prose for synthesize step."""
        blocking = ctx.get("blocking", ctx.get("has_blocking", "0"))
        minor = ctx.get("minor_count", "0")
        future = ctx.get("future_count", "0")
        if blocking in (False, "False", "0", 0):
            return f"Completed synthesis with no blocking issues; {minor} minor, {future} future recommendations."
        return f"Completed synthesis with {blocking} blocking issues."

    def _prose_recommendations_fb(ctx: dict) -> str:
        """Generate prose for recommendations step."""
        blocking = ctx.get("has_blocking", ctx.get("blocking", False))
        minor = ctx.get("minor_count", 0)
        future = ctx.get("future_count", 0)
        if blocking in (False, "False", "0", 0):
            return f"Processing recommendations; no blocking issues, {minor} minor, {future} future."
        return "Processing recommendations with blocking issues to address."

    def _prose_merge_ready_fb(ctx: dict) -> str:
        """Generate prose for merge-ready step."""
        blocking = ctx.get("blocking", ctx.get("has_blocking", 0))
        if blocking in (False, "False", "0", 0):
            return "Completed review with no blocking issues; PR ready for merge."
        return "Review complete; awaiting resolution of blocking issues."

    PROSE_CONTEXT_TEMPLATES = {
        "commit": lambda ctx: "Was committing changes to git.",
        "create-pr": lambda ctx: f"Was creating PR #{ctx.get('pr_number', '')}." if ctx.get("pr_number") else "Was creating pull request.",
        "invoke-reviewers": _prose_invoke_reviewers_fb,
        "synthesize": _prose_synthesize_fb,
        "recommendations": _prose_recommendations_fb,
        "merge-ready": _prose_merge_ready_fb,
        "awaiting-merge": lambda ctx: "Was waiting for user decision.",
        "awaiting_user_decision": lambda ctx: "Was waiting for user decision.",
        "variety-assess": lambda ctx: "Was assessing task complexity.",
        "prepare": lambda ctx: f"Was running PREPARE phase for: {ctx.get('feature', '')}." if ctx.get("feature") else "Was running PREPARE phase.",
        "architect": lambda ctx: "Was running ARCHITECT phase.",
        "code": lambda ctx: f"Was running CODE phase ({ctx.get('phase', '')})." if ctx.get("phase") else "Was running CODE phase.",
        "test": lambda ctx: "Was running TEST phase.",
        "analyze": lambda ctx: "Was analyzing scope and selecting specialists.",
        "consult": lambda ctx: "Was consulting specialists for planning perspectives.",
        "present": lambda ctx: f"Was presenting plan ({ctx.get('plan_file', '')}) for approval." if ctx.get("plan_file") else "Was presenting plan for user approval.",
        "invoking-specialist": lambda ctx: "Was delegating to specialist agent.",
        "specialist-completed": lambda ctx: "Specialist work had completed.",
        "nested-prepare": lambda ctx: "Was running nested PREPARE phase.",
        "nested-architect": lambda ctx: "Was running nested ARCHITECT phase.",
        "nested-code": lambda ctx: "Was running nested CODE phase.",
        "nested-test": lambda ctx: "Was running nested TEST phase.",
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


def _build_prose_context_fallback(step_name: str, context: dict) -> str:
    """
    Build a prose context line combining step action with context values.

    Fallback implementation when refresh package is not available.

    Args:
        step_name: The workflow step name (e.g., "invoke-reviewers")
        context: Dict of context values

    Returns:
        Prose sentence describing action + progress
    """
    template_fn = PROSE_CONTEXT_TEMPLATES.get(step_name)
    if template_fn:
        try:
            return template_fn(context)
        except Exception:
            pass  # Fall through to generic

    # Generic fallback
    step_desc = STEP_DESCRIPTIONS.get(step_name, step_name)
    if context:
        context_parts = [f"{k}={v}" for k, v in context.items()]
        return f"Was in {step_name} step ({', '.join(context_parts)})."
    return f"Was in {step_name} step."


def _build_refresh_message_fallback(checkpoint: dict) -> str:
    """
    Fallback: Build the directive prompt refresh message for the orchestrator (~50-60 tokens).

    Used when refresh package is not available.

    Format:
        [POST-COMPACTION CHECKPOINT]
        Prior conversation auto-compacted. Resume unfinished PACT workflow below:
        Workflow: {workflow_name} ({workflow_id})
        Context: {prose description of action + progress}
        Next Step: {pending_action.instruction} [. **Get user approval before acting.**]

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

    lines = ["[POST-COMPACTION CHECKPOINT]"]

    # Line 2: Shorter explanatory line
    lines.append("Prior conversation auto-compacted. Resume unfinished PACT workflow below:")

    # Line 3: Workflow: workflow (id)
    if workflow_id:
        lines.append(f"Workflow: {workflow_name} ({workflow_id})")
    else:
        lines.append(f"Workflow: {workflow_name}")

    # Line 4: Prose Context - combines action and progress in natural language
    prose_context = _build_prose_context_fallback(step_name, context)
    lines.append(f"Context: {prose_context}")

    # Line 5: Next step
    if pending_action:
        instruction = pending_action.get("instruction", "")
        if instruction:
            if confidence < CONFIDENCE_AUTO_PROCEED_THRESHOLD:
                lines.append(f"Next Step: {instruction}. **Get user approval before acting.**")
            else:
                lines.append(f"Next Step: {instruction}")
        else:
            # Has pending_action but no instruction
            lines.append("Next Step: **Ask user how to proceed.**")
    else:
        # No pending_action at all
        lines.append("Next Step: **Ask user how to proceed.**")

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
