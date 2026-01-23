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
