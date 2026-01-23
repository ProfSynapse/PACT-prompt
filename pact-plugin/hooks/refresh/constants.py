"""
Location: pact-plugin/hooks/refresh/constants.py
Summary: Configuration constants for the workflow refresh system.
Used by: All refresh modules for consistent threshold and limit values.

This module centralizes configuration constants that may need tuning,
keeping regex patterns and workflow definitions in patterns.py while
extracting tunable numeric values here for maintainability.
"""

# === CONFIDENCE THRESHOLDS (Item 3) ===

# Minimum confidence score for checkpoint to be considered valid
CONFIDENCE_THRESHOLD = 0.3

# Confidence labels for human-readable output
CONFIDENCE_LABEL_HIGH = 0.8
CONFIDENCE_LABEL_MEDIUM = 0.5

# === LENGTH LIMITS ===

# Maximum length for extracted text to prevent excessive data
PENDING_ACTION_INSTRUCTION_MAX_LENGTH = 200
REVIEW_PROMPT_INSTRUCTION_MAX_LENGTH = 150
TASK_SUMMARY_MAX_LENGTH = 200

# === PROCESSING LIMITS ===

# Termination detection window: number of turns after trigger to check
TERMINATION_WINDOW_TURNS = 10

# Size threshold for switching to efficient tail-reading (10 MB)
LARGE_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024

# Maximum transcript lines to read for workflow detection
MAX_TRANSCRIPT_LINES = 500

# === CHECKPOINT CONFIGURATION ===

# Current checkpoint schema version
CHECKPOINT_VERSION = "1.0"

# Checkpoint file expiration in days (Item 11)
CHECKPOINT_MAX_AGE_DAYS = 7

# === STEP DESCRIPTIONS ===
# Human-readable descriptions for workflow steps, used in refresh messages
# to help the AI understand what each state means when resuming after compaction

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

# === PROSE CONTEXT TEMPLATES ===
# Templates for generating prose context lines that combine step action with context values
# Keys are step names; values are callables that take context dict and return prose string

def _prose_invoke_reviewers(ctx: dict) -> str:
    """Generate prose for invoke-reviewers step."""
    reviewers = ctx.get("reviewers", "")
    blocking = ctx.get("blocking", "0")
    # Parse reviewers like "2/3" to extract completed and total
    if "/" in str(reviewers):
        completed, total = str(reviewers).split("/")
        return f"Launched {total} reviewer agents; {completed} had completed with {blocking} blocking issues."
    elif reviewers:
        return f"Launched reviewer agents; {reviewers} had completed with {blocking} blocking issues."
    else:
        return "Was launching reviewer agents."


def _prose_synthesize(ctx: dict) -> str:
    """Generate prose for synthesize step."""
    blocking = ctx.get("blocking", ctx.get("has_blocking", "0"))
    minor = ctx.get("minor_count", "0")
    future = ctx.get("future_count", "0")
    if blocking in (False, "False", "0", 0):
        return f"Completed synthesis with no blocking issues; {minor} minor, {future} future recommendations."
    return f"Completed synthesis with {blocking} blocking issues."


def _prose_recommendations(ctx: dict) -> str:
    """Generate prose for recommendations step."""
    blocking = ctx.get("has_blocking", ctx.get("blocking", False))
    minor = ctx.get("minor_count", 0)
    future = ctx.get("future_count", 0)
    if blocking in (False, "False", "0", 0):
        return f"Processing recommendations; no blocking issues, {minor} minor, {future} future."
    return f"Processing recommendations with blocking issues to address."


def _prose_merge_ready(ctx: dict) -> str:
    """Generate prose for merge-ready step."""
    blocking = ctx.get("blocking", ctx.get("has_blocking", 0))
    if blocking in (False, "False", "0", 0):
        return "Completed review with no blocking issues; PR ready for merge."
    return "Review complete; awaiting resolution of blocking issues."


def _prose_awaiting_user_decision(ctx: dict) -> str:
    """Generate prose for awaiting_user_decision step."""
    return "Was waiting for user decision."


def _prose_commit(ctx: dict) -> str:
    """Generate prose for commit step."""
    return "Was committing changes to git."


def _prose_create_pr(ctx: dict) -> str:
    """Generate prose for create-pr step."""
    pr_number = ctx.get("pr_number", "")
    if pr_number:
        return f"Was creating PR #{pr_number}."
    return "Was creating pull request."


def _prose_variety_assess(ctx: dict) -> str:
    """Generate prose for variety-assess step."""
    return "Was assessing task complexity."


def _prose_prepare(ctx: dict) -> str:
    """Generate prose for prepare step."""
    feature = ctx.get("feature", "")
    if feature:
        return f"Was running PREPARE phase for: {feature}."
    return "Was running PREPARE phase."


def _prose_architect(ctx: dict) -> str:
    """Generate prose for architect step."""
    return "Was running ARCHITECT phase."


def _prose_code(ctx: dict) -> str:
    """Generate prose for code step."""
    phase = ctx.get("phase", "")
    if phase:
        return f"Was running CODE phase ({phase})."
    return "Was running CODE phase."


def _prose_test(ctx: dict) -> str:
    """Generate prose for test step."""
    return "Was running TEST phase."


def _prose_analyze(ctx: dict) -> str:
    """Generate prose for analyze step."""
    return "Was analyzing scope and selecting specialists."


def _prose_consult(ctx: dict) -> str:
    """Generate prose for consult step."""
    return "Was consulting specialists for planning perspectives."


def _prose_present(ctx: dict) -> str:
    """Generate prose for present step."""
    plan_file = ctx.get("plan_file", "")
    if plan_file:
        return f"Was presenting plan ({plan_file}) for approval."
    return "Was presenting plan for user approval."


def _prose_invoking_specialist(ctx: dict) -> str:
    """Generate prose for invoking-specialist step."""
    return "Was delegating to specialist agent."


def _prose_specialist_completed(ctx: dict) -> str:
    """Generate prose for specialist-completed step."""
    return "Specialist work had completed."


def _prose_nested_prepare(ctx: dict) -> str:
    """Generate prose for nested-prepare step."""
    return "Was running nested PREPARE phase."


def _prose_nested_architect(ctx: dict) -> str:
    """Generate prose for nested-architect step."""
    return "Was running nested ARCHITECT phase."


def _prose_nested_code(ctx: dict) -> str:
    """Generate prose for nested-code step."""
    return "Was running nested CODE phase."


def _prose_nested_test(ctx: dict) -> str:
    """Generate prose for nested-test step."""
    return "Was running nested TEST phase."


PROSE_CONTEXT_TEMPLATES = {
    # peer-review steps
    "commit": _prose_commit,
    "create-pr": _prose_create_pr,
    "invoke-reviewers": _prose_invoke_reviewers,
    "synthesize": _prose_synthesize,
    "recommendations": _prose_recommendations,
    "merge-ready": _prose_merge_ready,
    "awaiting-merge": _prose_awaiting_user_decision,
    "awaiting_user_decision": _prose_awaiting_user_decision,
    # orchestrate steps
    "variety-assess": _prose_variety_assess,
    "prepare": _prose_prepare,
    "architect": _prose_architect,
    "code": _prose_code,
    "test": _prose_test,
    # plan-mode steps
    "analyze": _prose_analyze,
    "consult": _prose_consult,
    "present": _prose_present,
    # comPACT steps
    "invoking-specialist": _prose_invoking_specialist,
    "specialist-completed": _prose_specialist_completed,
    # rePACT (nested) steps
    "nested-prepare": _prose_nested_prepare,
    "nested-architect": _prose_nested_architect,
    "nested-code": _prose_nested_code,
    "nested-test": _prose_nested_test,
}
