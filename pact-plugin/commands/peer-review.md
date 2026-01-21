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
2. Present findings as a simple table:
   | Recommendation | Severity | Reviewer |
   |----------------|----------|----------|
   | [the finding]  | Blocking / Minor / Future | architect / test / backend / etc. |

   - **Blocking**: Must fix before merge
   - **Minor**: Optional fix for this PR
   - **Future**: Out of scope; track as GitHub issue

3. Handle recommendations by severity:
   - **Blocking**: Automatically address by selecting appropriate workflow:
     - Simple/single-domain → `/PACT:comPACT`
     - Complex/multi-domain → `/PACT:orchestrate`
     - After fixes complete, re-run review to verify
   - **Minor + Future**: Use `AskUserQuestion` tool with one question per recommendation:
     - Each minor: "Address [recommendation] now?" → Yes / No
     - Each future: "Create GitHub issue for [recommendation]?" → Yes / No
     - Note: Tool supports up to 4 questions per call; batch accordingly
     - **Collect all answers first**, then batch work:
       - Group all minor=Yes items → Select workflow based on combined scope:
         - Single-domain items → `/PACT:comPACT` (parallelize if independent)
         - Multi-domain items → `/PACT:orchestrate`
       - Group all future=Yes items → Create GitHub issues
     - If any minor items fixed → re-run review to verify

4. State merge readiness: "Ready to merge" or "Changes requested: [specifics]"

5. Present to user and **stop** — merging requires explicit user authorization (S5 policy)
