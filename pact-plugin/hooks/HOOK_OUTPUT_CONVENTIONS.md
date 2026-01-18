# Hook Output Structure Conventions

This document defines the conventions for hook script output fields in the PACT framework.

## Output Field Types

Hooks can return JSON with two different output mechanisms:

### 1. `systemMessage` (Top-Level)

**Purpose**: Important messages that should be prominently displayed to the user/agent.

**Use when**:
- Reminding the agent to take action (memory saves, phase completion)
- Warning about issues that need attention
- Providing validation feedback (missing handoff elements)
- Reporting errors or failures

**Example**:
```json
{
  "systemMessage": "Decision logs should be created in docs/decision-logs/ before completing CODE phase."
}
```

**Used by**:
- `memory_prompt.py` - Prompts to save memory after significant work
- `phase_completion.py` - Reminders for decision logs and TEST phase
- `validate_handoff.py` - Warnings about missing handoff elements
- `session_init.py` - Error messages for failed installations

### 2. `hookSpecificOutput.additionalContext`

**Purpose**: Contextual information that supplements the agent's work without demanding immediate attention.

**Use when**:
- Providing background context (available plans, session state)
- Gentle reminders that fire frequently (post-edit memory checks)
- File size warnings that inform but don't block
- Operational status updates

**Example**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "File size: 650 lines. Consider extracting functions."
  }
}
```

**Used by**:
- `memory_posttool.py` - Memory check reminder after every edit
- `file_size_check.py` - File size guidance
- `memory_enforce.py` - Mandatory memory save instructions
- `session_init.py` - Session context (plans found, migration status)

## Decision Guide

| Scenario | Use | Rationale |
|----------|-----|-----------|
| Agent should take action NOW | `systemMessage` | Prominent visibility |
| Validation failed, needs fix | `systemMessage` | Actionable feedback |
| Error occurred | `systemMessage` | User needs to know |
| Reminder that fires frequently | `additionalContext` | Avoids noise |
| Background context | `additionalContext` | Supplementary info |
| Status update (success) | `additionalContext` | Informational only |

## Combining Both

Hooks can use both fields when appropriate:

```json
{
  "systemMessage": "Failed to install model2vec. Memory features may be limited.",
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Plans found: auth-feature-plan.md | Migrated 50/50 embeddings"
  }
}
```

Use this pattern when there's both:
- An issue requiring attention (`systemMessage`)
- Contextual status info (`additionalContext`)

## Required Fields for `hookSpecificOutput`

When using `hookSpecificOutput`, include:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",  // Match the hook event type
    "additionalContext": "Your message here"
  }
}
```

The `hookEventName` should match the hook event: `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStop`, `Stop`.

## Silent Operation

Hooks that find nothing actionable should exit with empty output:

```python
# Nothing to report
print("{}")
sys.exit(0)
```

Or simply exit without output:

```python
# No issues found
sys.exit(0)
```
