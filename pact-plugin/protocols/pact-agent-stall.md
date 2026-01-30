## Agent Stall Detection

**Stalled indicators**:
- Background task running but no progress at monitoring checkpoints
- Task completed but no handoff received
- Process terminated without handoff or blocker report

Detection is event-driven: check at signal monitoring points (after dispatch, on completion, on stoppage). If a background task returned but produced no handoff or blocker, treat as stalled immediately.

### Recovery Protocol

1. Check the agent's output (from `run_in_background`) for partial work or error messages
2. Mark the stalled agent task as `completed` with `metadata={"stalled": true, "reason": "{what happened}"}`
3. Assess: Is the work partially done? Can it be continued from where it stopped?
4. Create a new agent task to retry or continue the work, passing any partial output as context
5. If stall persists after 1 retry, emit an **ALERT** algedonic signal (META-BLOCK category)

### Prevention

Include in agent prompts: "If you encounter an error that prevents completion, report a partial handoff with whatever work you completed rather than silently failing."

### Non-Happy-Path Task Termination

When an agent cannot complete normally (stall, failure, or unresolvable blocker), mark its task as `completed` with descriptive metadata:

Metadata: `{"stalled": true, "reason": "..."}` | `{"failed": true, "reason": "..."}` | `{"blocked": true, "blocker_task": "..."}`

**Convention**: All non-happy-path terminations use `completed` with metadata — no `failed` status exists. This preserves the `pending → in_progress → completed` lifecycle.

---
