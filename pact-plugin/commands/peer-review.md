---
description: Peer review of current work (commit, create PR, multi-agent review)
argument-hint: [e.g., feature X implementation]
---
Review the current work: $ARGUMENTS

1. Commit any uncommitted work
2. Create a PR if one doesn't exist
3. Review the PR

**PR Review Workflow**

Pull request reviews should mirror real-world team practices where multiple reviewers sign off before merging. Invoke **at least 3 agents in parallel** to provide comprehensive review coverage:

Standard reviewer combination:
- **pact-architect**: Design coherence, architectural patterns, interface contracts, separation of concerns
- **pact-test-engineer**: Test coverage, testability, performance implications, edge cases
- **Domain specialist coder** (selected below): Implementation quality specific to the domain

Select the domain coder based on PR focus:
- Frontend changes → **pact-frontend-coder** (UI implementation quality, accessibility, state management)
- Backend changes → **pact-backend-coder** (Server-side implementation quality, API design, error handling)
- Database changes → **pact-database-engineer** (Query efficiency, schema design, data integrity)
- Multiple domains → Coder for domain with most significant changes, or all relevant domain coders if changes are equally significant

---

## Task Hierarchy

Create Task hierarchy for the review process:

```
1. TaskCreate: Review task — subject: "Review: {feature-slug}"
2. Analyze PR: Which reviewers needed?
3. TaskCreate: Reviewer agent tasks
   - subject: "{agent-type}: review {feature-slug}"
   - (architect, test-engineer, domain specialist(s))
4. TaskUpdate: Review task addBlockedBy = [reviewer IDs]
5. Dispatch reviewers in parallel (mark in_progress immediately after dispatch)
6. Monitor until reviewers complete (handoffs received)
7. TaskUpdate: Reviewer tasks completed (extract metadata from handoffs)
8. Synthesize findings
9. If major/blocking issues found:
   a. TaskCreate: Remediation agent tasks
   b. Dispatch, monitor until complete
   c. TaskUpdate: Remediation tasks completed
10. If minor/future items require fixes (user approved):
    a. TaskCreate: Fix agent tasks
    b. Dispatch, monitor until complete
    c. TaskUpdate: Fix tasks completed
11. TaskCreate: "Awaiting merge decision" — approval task
12. Present to user, await approval
13. On approval: TaskUpdate approval task completed
14. TaskUpdate: Review task completed, metadata.artifact = PR URL
```

**Merge authorization boundary**: The orchestrator NEVER merges. Present findings, state merge readiness, then stop and wait for explicit user authorization.

**Graceful degradation**: If any Task tool call fails, log a warning and continue. Task integration enhances PACT but should never block it.

---

## Output Conciseness

**Default: Concise output.** User sees synthesis, not each reviewer's full output restated.

| Internal (don't show) | External (show) |
|----------------------|-----------------|
| Each reviewer's raw output | Recommendations table + `See docs/review/` |
| Reviewer selection reasoning | `Invoking architect + test engineer + backend coder` |
| Agreement/conflict analysis details | `Ready to merge` or `Changes requested: [specifics]` |

**User can always ask** for full reviewer output (e.g., "What did the architect say?" or "Show me all findings").

| Verbose (avoid) | Concise (prefer) |
|-----------------|------------------|
| "The architect found X, the test engineer found Y..." | Consolidated summary in `docs/review/` |
| "Let me synthesize the findings from all reviewers..." | (just do it, show result) |

---

**After all reviews complete**:
1. Synthesize findings into a unified review summary with consolidated recommendations
2. Present **all** findings to user as a **markdown table** **before asking any questions** (blocking, minor, and future):

   | Recommendation | Severity | Reviewer |
   |----------------|----------|----------|
   | [the finding]  | Blocking / Minor / Future | architect / test / backend / etc. |

   - **Blocking**: Must fix before merge
   - **Minor**: Optional fix for this PR
   - **Future**: Out of scope; track as GitHub issue

3. Handle recommendations by severity:
   - **No recommendations**: If the table is empty (no blocking, minor, or future items), proceed directly to step 4.
   - **Blocking**: Automatically address all blocking items:
     - Batch fixes by selecting appropriate workflow(s) based on combined scope:
       - Single-domain items → `/PACT:comPACT` (invoke concurrently if independent)
       - Multi-domain items → `/PACT:orchestrate`
       - Mixed (both single and multi-domain) → Use `/PACT:comPACT` for the single-domain batch AND `/PACT:orchestrate` for the multi-domain batch (can run in parallel if independent)
     - After all fixes complete, re-run review to verify fixes only (not a full PR re-review)
     - **Termination**: If blocking items persist after 2 fix-verify cycles → escalate via `/PACT:imPACT`
   - **Minor + Future**:

     **Step A — Initial Gate Question** (Yes/No only):
     - Use `AskUserQuestion` tool: "Would you like to review the minor and future recommendations?"
       - Options: **Yes** (review each item) / **No** (skip to merge readiness)
     - If **No**: Skip to step 4 directly
     - If **Yes**: Continue to Step B

     **Step B — Preemptive Context Gathering**:
     - Before asking per-recommendation questions, gather and present context for ALL minor and future recommendations
     - For each recommendation, provide:
       - Why it matters (impact on code quality, maintainability, security, performance)
       - What the change would involve (scope, affected areas)
       - Trade-offs of addressing vs. not addressing
     - Keep each entry concise (2-3 sentences per bullet).
     - Present as a formatted list (one entry per recommendation) so user can review all context at once.
     - After presenting all context, proceed to Step C.

     **Step C — Per-Recommendation Questions** (after context presented):
     - Use `AskUserQuestion` tool with one question per recommendation
     - For each **minor** recommendation, ask "Address [recommendation] now?" with options:
       - **Yes** — Fix it in this PR
       - **No** — Skip for now
       - **More context** — Get additional details (if more detail is needed)
     - For each **future** recommendation, ask "What would you like to do with [recommendation]?" with options:
       - **Create GitHub issue** — Track for future work
       - **Skip** — Don't track or address
       - **Address now** — Fix it in this PR
       - **More context** — Get additional details (if more detail is needed)
     - Note: Tool supports 2-4 options per question and 1-4 questions per call. If >4 recommendations exist, make multiple `AskUserQuestion` calls to cover all items.
       - **Handling "More context" responses**:
         - When user selects "More context", provide deeper explanation beyond the preemptive context (e.g., implementation specifics, examples, related patterns)
         - After providing additional context, re-ask the same question for that specific recommendation (without the "More context" option)
         - Handle inline: provide context immediately, get the answer, then continue to the next recommendation
       - **Collect all answers first**, then batch work:
         - Group all minor=Yes items AND future="Address now" items → Select workflow based on combined scope:
           - Single-domain items → `/PACT:comPACT` (invoke concurrently if independent)
           - Multi-domain items → `/PACT:orchestrate`
         - Group all future="Create GitHub issue" items → Create GitHub issues
       - If any items fixed (minor or future addressed now) → re-run review to verify fixes only (not a full PR re-review)

4. State merge readiness (only after ALL blocking fixes complete AND minor/future item handling is done): "Ready to merge" or "Changes requested: [specifics]"

5. Present to user and **stop** — merging requires explicit user authorization (S5 policy)

---

**After user-authorized merge**: Run `/PACT:pin-memory` to update the project `CLAUDE.md` with the latest changes.

---

## Signal Monitoring

Check TaskList for blocker/algedonic signals:
- After each agent dispatch (reviewers, remediation agents)
- When agent reports completion
- On any unexpected agent stoppage

On signal detected: Follow Task Lifecycle Management in CLAUDE.md.

---

## Agent Prompt Language

When dispatching reviewer or remediation agents, include this block in the agent prompt:

```
**Blocker/Signal Protocol**:
- If you hit a blocker, STOP work immediately and report: "BLOCKER: {description}"
- If you detect a viability threat (security, data, ethics), STOP immediately and report:
  "⚠️ ALGEDONIC [HALT|ALERT]: {category} — {description}"
- Do NOT attempt workarounds for blockers. Do NOT continue work after emitting algedonic signals.
- Always end your response with a structured HANDOFF, even if incomplete.
```
