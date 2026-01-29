---
description: Perform end-of-session cleanup and documentation synchronization
---
# PACT Wrap-Up Protocol

You are now entering the **Wrap-Up Phase**. Your goal is to ensure the workspace is clean and documentation is synchronized before the session ends or code is committed.

## 1. Documentation Synchronization
- **Scan** the workspace for recent code changes.
- **Update** `docs/CHANGELOG.md` with a new entry for this session:
    - **Date/Time**: Current timestamp.
    - **Focus**: The main task or feature worked on.
    - **Changes**: List modified files and brief descriptions.
    - **Result**: The outcome (e.g., "Completed auth flow", "Fixed login bug").
- **Verify** that `CLAUDE.md` reflects the current system state (architecture, patterns, components).
- **Verify** that `docs/<feature>/preparation/` and `docs/<feature>/architecture/` are up-to-date with the implementation.
- **Update** any outdated documentation.
- **Archive** any obsolete documentation to `docs/archive/`.

## 2. Workspace Cleanup
- **Identify** any temporary files created during the session (e.g., `temp_test.py`, `debug.log`, `foo.txt`, `test_output.json`).
- **Delete** these files to leave the workspace clean.

## 3. Task Audit

Use Task tools to review and clean up session Tasks:

```
1. TaskList: Review all session tasks
2. For abandoned in_progress tasks:
   - Determine why they were abandoned
   - TaskUpdate: Mark completed with description noting reason
     OR document why they remain in_progress
3. Verify Feature task reflects final state:
   - All child phases completed or documented
   - Metadata reflects actual work done
4. Report task summary:
   "Session has N tasks (X completed, Y pending, Z abandoned)"
```

### Multi-Session Cleanup

If `CLAUDE_CODE_TASK_LIST_ID` is set (multi-session mode):
- Offer: "Clean up completed workflows? (Context already archived to memory)"
- If user confirms: Delete completed feature hierarchies to keep Task list manageable
- If user declines: Leave as-is

**Task list size guidance**:
| Task Count | Action |
|------------|--------|
| < 20 | Normal operation |
| 20-50 | Suggest cleanup |
| > 50 | Warn about performance, strongly suggest cleanup |

**Graceful degradation**: If TaskList fails, skip Task audit and proceed with other wrap-up activities.

---

## 4. Final Status Report
- **Report** a summary of actions taken:
    - Docs updated: [List files]
    - Files archived: [List files]
    - Temp files deleted: [List files]
    - Status: READY FOR COMMIT / REVIEW

If no actions were needed, state "Workspace is clean and docs are in sync."
