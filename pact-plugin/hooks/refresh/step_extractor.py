"""
Location: pact-plugin/hooks/refresh/step_extractor.py
Summary: Extract current step and pending action from workflow state.
Used by: refresh/__init__.py for building refresh checkpoints.

Analyzes transcript turns after a workflow trigger to determine
the current step/phase and any pending user action.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .transcript_parser import Turn
from .workflow_detector import WorkflowInfo
from .patterns import (
    WORKFLOW_PATTERNS,
    PENDING_ACTION_PATTERNS,
    extract_context_value,
)


@dataclass
class PendingAction:
    """
    Represents an action awaiting user input.

    Attributes:
        action_type: Type of pending action (e.g., "AskUserQuestion")
        instruction: The instruction or question for the user
        data: Additional action-specific data
    """

    action_type: str
    instruction: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class StepInfo:
    """
    Information about the current workflow step.

    Attributes:
        name: Step name (e.g., "code", "invoke-reviewers")
        sequence: Step sequence number (1-based, if determinable)
        started_at: Timestamp when step started
        pending_action: Any action awaiting user input
        context: Extracted context values for checkpoint
    """

    name: str
    sequence: int = 0
    started_at: str = ""
    pending_action: Optional[PendingAction] = None
    context: dict[str, Any] = field(default_factory=dict)


def find_step_markers_in_turn(turn: Turn, workflow_name: str) -> list[str]:
    """
    Find step markers present in a turn's content.

    Args:
        turn: Turn to analyze
        workflow_name: Workflow to check markers for

    Returns:
        List of matched step markers
    """
    pattern = WORKFLOW_PATTERNS.get(workflow_name)
    if not pattern:
        return []

    matched = []
    content_lower = turn.content.lower()

    for marker in pattern.step_markers:
        # Check for marker as word boundary (avoid partial matches)
        marker_pattern = rf"\b{re.escape(marker.lower())}\b"
        if re.search(marker_pattern, content_lower):
            matched.append(marker)

    return matched


def determine_current_step(
    turns: list[Turn],
    workflow_info: WorkflowInfo,
) -> tuple[str, int, str]:
    """
    Determine the current step in the workflow.

    Scans turns after the workflow trigger to find the most recent
    step marker.

    Args:
        turns: List of turns
        workflow_info: Detected workflow information

    Returns:
        Tuple of (step_name, sequence_number, started_timestamp)
    """
    if not workflow_info.trigger_turn:
        return "unknown", 0, ""

    # Find trigger index
    trigger_index = 0
    for i, turn in enumerate(turns):
        if turn.line_number == workflow_info.trigger_turn.line_number:
            trigger_index = i
            break

    pattern = WORKFLOW_PATTERNS.get(workflow_info.name)
    if not pattern:
        return "unknown", 0, ""

    step_markers = pattern.step_markers
    current_step = ""
    step_sequence = 0
    step_timestamp = ""

    # Scan forward from trigger to find most recent step
    for turn in turns[trigger_index:]:
        if not turn.is_assistant:
            continue

        markers = find_step_markers_in_turn(turn, workflow_info.name)
        if markers:
            # Use the last marker found (most recent step mention)
            current_step = markers[-1]
            step_timestamp = turn.timestamp

            # Determine sequence from marker position in step_markers list
            try:
                step_sequence = step_markers.index(current_step) + 1
            except ValueError:
                step_sequence = 0

    # If no step found, use first step as default
    if not current_step and step_markers:
        current_step = step_markers[0]
        step_sequence = 1
        step_timestamp = workflow_info.started_at

    return current_step, step_sequence, step_timestamp


def detect_pending_action(turns: list[Turn], trigger_index: int) -> PendingAction | None:
    """
    Detect any pending action requiring user input.

    Analyzes the most recent assistant turns for action indicators.

    Args:
        turns: List of turns
        trigger_index: Index of workflow trigger

    Returns:
        PendingAction if found, None otherwise
    """
    # Check last few assistant turns for pending action indicators
    assistant_turns = [t for t in turns[trigger_index:] if t.is_assistant]

    if not assistant_turns:
        return None

    # Check the last 2 assistant turns (action might not be in very last)
    for turn in reversed(assistant_turns[-2:]):
        content = turn.content

        # Check for AskUserQuestion pattern
        match = PENDING_ACTION_PATTERNS["AskUserQuestion"].search(content)
        if match:
            return PendingAction(
                action_type="AskUserQuestion",
                instruction=match.group(1).strip()[:200],  # Cap length
            )

        # Check for review prompt pattern
        match = PENDING_ACTION_PATTERNS["review_prompt"].search(content)
        if match:
            return PendingAction(
                action_type="UserDecision",
                instruction=f"Would you like to {match.group(1).strip()[:150]}",
            )

        # Check for general awaiting input
        if PENDING_ACTION_PATTERNS["awaiting_input"].search(content):
            return PendingAction(
                action_type="AwaitingInput",
                instruction="Waiting for user response",
            )

    return None


def extract_workflow_context(
    turns: list[Turn],
    workflow_info: WorkflowInfo,
) -> dict[str, Any]:
    """
    Extract context values relevant to the workflow.

    Scans turns for PR numbers, task summaries, and other context
    that would help resume the workflow.

    Args:
        turns: List of turns
        workflow_info: Detected workflow information

    Returns:
        Dict of context key-value pairs
    """
    context: dict[str, Any] = {}

    # Find trigger index
    trigger_index = 0
    if workflow_info.trigger_turn:
        for i, turn in enumerate(turns):
            if turn.line_number == workflow_info.trigger_turn.line_number:
                trigger_index = i
                break

    # Extract context from all turns after trigger
    for turn in turns[trigger_index:]:
        content = turn.content

        # PR number
        if "pr_number" not in context:
            pr_num = extract_context_value(content, "pr_number")
            if pr_num:
                context["pr_number"] = int(pr_num)

        # Task summary
        if "task_summary" not in context:
            summary = extract_context_value(content, "task_summary")
            if summary:
                context["task_summary"] = summary[:200]  # Cap length

        # Branch name
        if "branch_name" not in context:
            branch = extract_context_value(content, "branch_name")
            if branch:
                context["branch_name"] = branch

    # Workflow-specific context extraction
    if workflow_info.name == "peer-review":
        context = _extract_peer_review_context(turns, trigger_index, context)
    elif workflow_info.name == "orchestrate":
        context = _extract_orchestrate_context(turns, trigger_index, context)

    return context


def _extract_peer_review_context(
    turns: list[Turn],
    trigger_index: int,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract peer-review specific context.

    Args:
        turns: List of turns
        trigger_index: Index of workflow trigger
        context: Existing context dict to extend

    Returns:
        Extended context dict
    """
    # Look for review findings summary
    for turn in reversed(turns[trigger_index:]):
        if not turn.is_assistant:
            continue

        content = turn.content.lower()

        # Check for blocking issues
        if "has_blocking" not in context:
            if "blocking" in content:
                if "no blocking" in content or "0 blocking" in content:
                    context["has_blocking"] = False
                else:
                    context["has_blocking"] = True

        # Count patterns
        minor_match = re.search(r"(\d+)\s*minor", content)
        if minor_match and "minor_count" not in context:
            context["minor_count"] = int(minor_match.group(1))

        future_match = re.search(r"(\d+)\s*future", content)
        if future_match and "future_count" not in context:
            context["future_count"] = int(future_match.group(1))

    return context


def _extract_orchestrate_context(
    turns: list[Turn],
    trigger_index: int,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract orchestrate workflow specific context.

    Args:
        turns: List of turns
        trigger_index: Index of workflow trigger
        context: Existing context dict to extend

    Returns:
        Extended context dict
    """
    # Look for current phase
    for turn in reversed(turns[trigger_index:]):
        if not turn.is_assistant:
            continue

        content = turn.content.lower()

        # Detect current phase
        if "current_phase" not in context:
            phases = ["prepare", "architect", "code", "test"]
            for phase in phases:
                if f"{phase} phase" in content or f"starting {phase}" in content:
                    context["current_phase"] = phase
                    break

    return context


def extract_current_step(
    turns: list[Turn],
    workflow_info: WorkflowInfo,
) -> StepInfo:
    """
    Extract complete step information from the workflow.

    Main entry point for step extraction. Determines current step,
    sequence, pending action, and context.

    Args:
        turns: List of turns
        workflow_info: Detected workflow information

    Returns:
        StepInfo with current step details
    """
    # Find trigger index
    trigger_index = 0
    if workflow_info.trigger_turn:
        for i, turn in enumerate(turns):
            if turn.line_number == workflow_info.trigger_turn.line_number:
                trigger_index = i
                break

    # Determine current step
    step_name, sequence, started_at = determine_current_step(turns, workflow_info)

    # Detect pending action
    pending_action = detect_pending_action(turns, trigger_index)

    # Extract context
    context = extract_workflow_context(turns, workflow_info)

    return StepInfo(
        name=step_name,
        sequence=sequence,
        started_at=started_at,
        pending_action=pending_action,
        context=context,
    )
