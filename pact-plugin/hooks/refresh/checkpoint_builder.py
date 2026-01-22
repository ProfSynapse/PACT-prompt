"""
Location: pact-plugin/hooks/refresh/checkpoint_builder.py
Summary: Build checkpoint JSON from extracted workflow state.
Used by: refresh/__init__.py and PreCompact hook.

Assembles a checkpoint dict following the schema defined in the
refresh plan, suitable for writing to disk and later refresh.
Also provides shared utilities for checkpoint path resolution.

Item 13 Note: This module uses Pydantic BaseModel when available for
validation, with dataclass fallback. To enable Pydantic features,
install pydantic: pip install pydantic
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .workflow_detector import WorkflowInfo
from .step_extractor import StepInfo
from .constants import (
    CHECKPOINT_VERSION,
    CONFIDENCE_LABEL_HIGH,
    CONFIDENCE_LABEL_MEDIUM,
)

# Item 13: Try to use Pydantic, fall back to dataclass
try:
    from pydantic import BaseModel, Field

    class CheckpointSchema(BaseModel):
        """
        Item 13: Pydantic model for checkpoint data structure.

        Provides automatic validation, serialization, and type checking.
        Uses model_dump() and model_validate() for dict conversion.
        """
        version: str = CHECKPOINT_VERSION
        session_id: str
        workflow_name: str
        workflow_id: str = ""
        workflow_started_at: str = ""
        step_name: str = ""
        step_sequence: int = 0
        step_started_at: str = ""
        pending_action_type: str | None = None
        pending_action_instruction: str | None = None
        pending_action_data: dict[str, Any] = Field(default_factory=dict)
        context: dict[str, Any] = Field(default_factory=dict)
        confidence: float = 0.0
        extraction_notes: str = ""
        transcript_lines_scanned: int = 0
        created_at: str = ""

        def to_dict(self) -> dict[str, Any]:
            """Convert to checkpoint dict format (compatibility method)."""
            pending_action = None
            if self.pending_action_type:
                pending_action = {
                    "type": self.pending_action_type,
                    "instruction": self.pending_action_instruction or "",
                    "data": self.pending_action_data,
                }

            return {
                "version": self.version,
                "session_id": self.session_id,
                "workflow": {
                    "name": self.workflow_name,
                    "id": self.workflow_id,
                    "started_at": self.workflow_started_at,
                },
                "step": {
                    "name": self.step_name,
                    "sequence": self.step_sequence,
                    "started_at": self.step_started_at,
                },
                "pending_action": pending_action,
                "context": self.context,
                "extraction": {
                    "confidence": self.confidence,
                    "notes": self.extraction_notes,
                    "transcript_lines_scanned": self.transcript_lines_scanned,
                },
                "created_at": self.created_at,
            }

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "CheckpointSchema":
            """Create from checkpoint dict format (compatibility method)."""
            # Item 10: Version compatibility check
            version = data.get("version", CHECKPOINT_VERSION)
            if version != CHECKPOINT_VERSION:
                print(
                    f"Warning: Checkpoint version {version} differs from current {CHECKPOINT_VERSION}. "
                    "Attempting to use anyway. Migration may be needed for future versions.",
                    file=sys.stderr,
                )

            workflow = data.get("workflow", {})
            step = data.get("step", {})
            extraction = data.get("extraction", {})
            pending = data.get("pending_action") or {}

            return cls(
                version=version,
                session_id=data.get("session_id", ""),
                workflow_name=workflow.get("name", "none"),
                workflow_id=workflow.get("id", ""),
                workflow_started_at=workflow.get("started_at", ""),
                step_name=step.get("name", ""),
                step_sequence=step.get("sequence", 0),
                step_started_at=step.get("started_at", ""),
                pending_action_type=pending.get("type") if pending else None,
                pending_action_instruction=pending.get("instruction") if pending else None,
                pending_action_data=pending.get("data", {}) if pending else {},
                context=data.get("context", {}),
                confidence=extraction.get("confidence", 0.0),
                extraction_notes=extraction.get("notes", ""),
                transcript_lines_scanned=extraction.get("transcript_lines_scanned", 0),
                created_at=data.get("created_at", ""),
            )

    _USING_PYDANTIC = True

except ImportError:
    # Fall back to dataclass when Pydantic not available
    from dataclasses import dataclass, field

    @dataclass
    class CheckpointSchema:
        """
        Dataclass fallback for checkpoint data structure.

        Provides type-safe access to checkpoint fields and serves as
        documentation for the checkpoint format. Install pydantic for
        automatic validation features.
        """
        version: str = CHECKPOINT_VERSION
        session_id: str = ""
        workflow_name: str = ""
        workflow_id: str = ""
        workflow_started_at: str = ""
        step_name: str = ""
        step_sequence: int = 0
        step_started_at: str = ""
        pending_action_type: str | None = None
        pending_action_instruction: str | None = None
        pending_action_data: dict[str, Any] = field(default_factory=dict)
        context: dict[str, Any] = field(default_factory=dict)
        confidence: float = 0.0
        extraction_notes: str = ""
        transcript_lines_scanned: int = 0
        created_at: str = ""

        def to_dict(self) -> dict[str, Any]:
            """Convert to checkpoint dict format."""
            pending_action = None
            if self.pending_action_type:
                pending_action = {
                    "type": self.pending_action_type,
                    "instruction": self.pending_action_instruction or "",
                    "data": self.pending_action_data,
                }

            return {
                "version": self.version,
                "session_id": self.session_id,
                "workflow": {
                    "name": self.workflow_name,
                    "id": self.workflow_id,
                    "started_at": self.workflow_started_at,
                },
                "step": {
                    "name": self.step_name,
                    "sequence": self.step_sequence,
                    "started_at": self.step_started_at,
                },
                "pending_action": pending_action,
                "context": self.context,
                "extraction": {
                    "confidence": self.confidence,
                    "notes": self.extraction_notes,
                    "transcript_lines_scanned": self.transcript_lines_scanned,
                },
                "created_at": self.created_at,
            }

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "CheckpointSchema":
            """Create from checkpoint dict format."""
            # Item 10: Version compatibility check
            version = data.get("version", CHECKPOINT_VERSION)
            if version != CHECKPOINT_VERSION:
                print(
                    f"Warning: Checkpoint version {version} differs from current {CHECKPOINT_VERSION}. "
                    "Attempting to use anyway. Migration may be needed for future versions.",
                    file=sys.stderr,
                )

            workflow = data.get("workflow", {})
            step = data.get("step", {})
            extraction = data.get("extraction", {})
            pending = data.get("pending_action") or {}

            return cls(
                version=version,
                session_id=data.get("session_id", ""),
                workflow_name=workflow.get("name", "none"),
                workflow_id=workflow.get("id", ""),
                workflow_started_at=workflow.get("started_at", ""),
                step_name=step.get("name", ""),
                step_sequence=step.get("sequence", 0),
                step_started_at=step.get("started_at", ""),
                pending_action_type=pending.get("type") if pending else None,
                pending_action_instruction=pending.get("instruction") if pending else None,
                pending_action_data=pending.get("data", {}) if pending else {},
                context=data.get("context", {}),
                confidence=extraction.get("confidence", 0.0),
                extraction_notes=extraction.get("notes", ""),
                transcript_lines_scanned=extraction.get("transcript_lines_scanned", 0),
                created_at=data.get("created_at", ""),
            )

    _USING_PYDANTIC = False


def get_checkpoint_path(encoded_path: str) -> Path:
    """
    Get the full checkpoint file path for a project.

    Shared utility used by both precompact_refresh.py and compaction_refresh.py
    to ensure consistent checkpoint file location.

    Args:
        encoded_path: The encoded project path segment

    Returns:
        Path to the checkpoint file
    """
    return Path.home() / ".claude" / "pact-refresh" / f"{encoded_path}.json"


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
        "version": CHECKPOINT_VERSION,
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
        "version": CHECKPOINT_VERSION,
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
    Convert a checkpoint to a directive prompt refresh message (~50-60 tokens).

    Used by the SessionStart hook to generate the refresh
    instructions injected after compaction.

    Format:
        [WORKFLOW REFRESH]
        Context auto-compaction occurred. This information helps you resume the PACT workflow in progress.
        You are resuming: {workflow_name} ({workflow_id})
        State: {step_name}
        Context: key=value, ... (only if context exists)
        Action: {pending_action.instruction} (only if pending action exists)
        Confidence: X.X. Verify with user if context seems outdated.

    Args:
        checkpoint: Valid checkpoint dict

    Returns:
        Directive prompt formatted refresh message string, or empty string if no workflow
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

    lines = ["[WORKFLOW REFRESH]"]

    # Line 2: Explanatory line
    lines.append("Context auto-compaction occurred. This information helps you resume the PACT workflow in progress.")

    # Line 3: You are resuming: workflow (id)
    if workflow_id:
        lines.append(f"You are resuming: {workflow_name} ({workflow_id})")
    else:
        lines.append(f"You are resuming: {workflow_name}")

    # Line 4: State
    lines.append(f"State: {step_name}")

    # Line 5: Context (only if present)
    if context:
        context_parts = [f"{k}={v}" for k, v in context.items()]
        lines.append(f"Context: {', '.join(context_parts)}")

    # Line 6: Action (only if pending action exists)
    if pending_action:
        instruction = pending_action.get("instruction", "")
        if instruction:
            lines.append(f"Action: {instruction}")

    # Line 7: Confidence guidance
    lines.append(f"Confidence: {confidence:.1f}. Verify with user if context seems outdated.")

    return "\n".join(lines)
