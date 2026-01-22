"""
Location: pact-plugin/hooks/refresh/checkpoint_builder.py
Summary: Build checkpoint JSON from extracted workflow state.
Used by: refresh/__init__.py and PreCompact hook.

Assembles a checkpoint dict following the schema defined in the
refresh plan, suitable for writing to disk and later refresh.
"""

import os
from datetime import datetime, timezone
from typing import Any

from .workflow_detector import WorkflowInfo
from .step_extractor import StepInfo


def get_session_id() -> str:
    """
    Get the current Claude session ID from environment.

    Returns:
        Session ID string or "unknown" if not available
    """
    return os.environ.get("CLAUDE_SESSION_ID", "unknown")


def get_encoded_project_path(transcript_path: str) -> str:
    """
    Extract the encoded project path from transcript path.

    The transcript path format is:
    ~/.claude/projects/{encoded-path}/{session-uuid}/session.jsonl

    Args:
        transcript_path: Full path to the transcript file

    Returns:
        Encoded project path segment (e.g., "-Users-mj-Sites-project")
    """
    parts = transcript_path.split("/")
    try:
        projects_idx = parts.index("projects")
        return parts[projects_idx + 1]
    except (ValueError, IndexError):
        # Fall back to deriving from project dir
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if project_dir:
            # Convert /Users/mj/Sites/project to -Users-mj-Sites-project
            return project_dir.replace("/", "-").lstrip("-")
        return "unknown-project"


def get_current_timestamp() -> str:
    """
    Get current UTC timestamp in ISO format.

    Returns:
        ISO 8601 formatted timestamp string
    """
    return datetime.now(timezone.utc).isoformat()


def build_checkpoint(
    transcript_path: str,
    workflow_info: WorkflowInfo,
    step_info: StepInfo,
    lines_scanned: int,
) -> dict[str, Any]:
    """
    Build a checkpoint dict from extracted workflow state.

    Assembles all extracted information into the checkpoint schema
    defined in the refresh plan.

    Args:
        transcript_path: Path to the source transcript
        workflow_info: Detected workflow information
        step_info: Extracted step information
        lines_scanned: Number of transcript lines analyzed

    Returns:
        Checkpoint dict ready for JSON serialization
    """
    # Build pending_action section
    pending_action_data: dict[str, Any] | None = None
    if step_info.pending_action:
        pending_action_data = {
            "type": step_info.pending_action.action_type,
            "instruction": step_info.pending_action.instruction,
            "data": step_info.pending_action.data,
        }

    # Calculate extraction notes
    extraction_notes = workflow_info.notes
    if workflow_info.is_terminated:
        extraction_notes = "Workflow terminated"

    checkpoint = {
        "version": "1.0",
        "session_id": get_session_id(),
        "workflow": {
            "name": workflow_info.name if not workflow_info.is_terminated else "none",
            "id": workflow_info.workflow_id,
            "started_at": workflow_info.started_at,
        },
        "step": {
            "name": step_info.name,
            "sequence": step_info.sequence,
            "started_at": step_info.started_at,
        },
        "pending_action": pending_action_data,
        "context": step_info.context,
        "extraction": {
            "confidence": workflow_info.confidence,
            "notes": extraction_notes,
            "transcript_lines_scanned": lines_scanned,
        },
        "created_at": get_current_timestamp(),
    }

    return checkpoint


def build_no_workflow_checkpoint(
    transcript_path: str,
    lines_scanned: int,
    reason: str = "No active workflow detected",
) -> dict[str, Any]:
    """
    Build a checkpoint indicating no active workflow.

    Used when transcript parsing finds no active workflow, or when
    a workflow has terminated.

    Args:
        transcript_path: Path to the source transcript
        lines_scanned: Number of transcript lines analyzed
        reason: Explanation for why no workflow was found

    Returns:
        Checkpoint dict with workflow.name = "none"
    """
    return {
        "version": "1.0",
        "session_id": get_session_id(),
        "workflow": {
            "name": "none",
            "id": "",
            "started_at": "",
        },
        "step": {
            "name": "",
            "sequence": 0,
            "started_at": "",
        },
        "pending_action": None,
        "context": {},
        "extraction": {
            "confidence": 1.0,  # High confidence that there's no workflow
            "notes": reason,
            "transcript_lines_scanned": lines_scanned,
        },
        "created_at": get_current_timestamp(),
    }


def validate_checkpoint(checkpoint: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a checkpoint dict has required fields.

    Args:
        checkpoint: Checkpoint dict to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ["version", "session_id", "workflow", "extraction", "created_at"]

    for key in required_keys:
        if key not in checkpoint:
            return False, f"Missing required key: {key}"

    workflow = checkpoint.get("workflow", {})
    if "name" not in workflow:
        return False, "Missing workflow.name"

    extraction = checkpoint.get("extraction", {})
    if "confidence" not in extraction:
        return False, "Missing extraction.confidence"

    return True, ""


def checkpoint_to_refresh_message(checkpoint: dict[str, Any]) -> str:
    """
    Convert a checkpoint to a human-readable refresh message.

    Used by the SessionStart hook to generate the refresh
    instructions injected after compaction.

    Args:
        checkpoint: Valid checkpoint dict

    Returns:
        Formatted refresh message string
    """
    workflow = checkpoint.get("workflow", {})
    workflow_name = workflow.get("name", "unknown")

    if workflow_name == "none":
        return ""

    workflow_id = workflow.get("id", "")
    step = checkpoint.get("step", {})
    step_name = step.get("name", "unknown")
    extraction = checkpoint.get("extraction", {})
    confidence = extraction.get("confidence", 0)
    context = checkpoint.get("context", {})
    pending_action = checkpoint.get("pending_action")

    # Format confidence level
    if confidence >= 0.8:
        confidence_label = "high"
    elif confidence >= 0.5:
        confidence_label = "medium"
    else:
        confidence_label = "low"

    lines = [
        "=== WORKFLOW REFRESH ===",
        "",
        "Session resumed after compaction.",
        f"Active workflow: {workflow_name}" + (f" ({workflow_id})" if workflow_id else ""),
        f"Checkpoint: {step_name}",
        f"Confidence: {confidence:.1f} ({confidence_label})",
    ]

    # Add pending action if present
    if pending_action:
        action_type = pending_action.get("type", "Unknown")
        instruction = pending_action.get("instruction", "")
        lines.extend([
            "",
            "NEXT ACTION REQUIRED:",
            f"{action_type}: {instruction}",
        ])

    # Add context if present
    if context:
        lines.extend(["", "Context:"])
        for key, value in context.items():
            lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Resume workflow from this checkpoint.",
        "===========================",
    ])

    return "\n".join(lines)
