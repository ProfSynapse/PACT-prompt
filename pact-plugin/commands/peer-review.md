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

## Output Conciseness

**Default: Concise output.** User sees synthesis, not each reviewer's full output restated.

| Internal (don't show) | External (show) |
|----------------------|-----------------|
| Each reviewer's raw output | `Review: 2 issues (architect: 1, test: 1), 3 suggestions. See docs/review/` |
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
2. Categorize findings by severity with reviewer attribution:
   - Format: `Review: X issues (reviewer: N, ...), Y suggestions (reviewer: N major, reviewer: N minor)`
   - Example: `Review: 2 issues (architect: 1, test: 1), 3 suggestions (backend: 2 major, architect: 1 minor)`
   - State merge readiness: "Ready to merge" or "Changes requested: [specifics]"
3. Ask user: "Would you like to address any reviewer suggestions before merging?"
   - If yes → Select appropriate workflow based on fix complexity:
     - Simple/single-domain fixes → `/PACT:comPACT`
     - Complex/multi-domain fixes → `/PACT:orchestrate`
   - After fixes complete, re-run review to verify
   - If no → Proceed to step 4
4. Present to user and **stop** — merging requires explicit user authorization (S5 policy)
