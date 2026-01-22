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
       - Single-domain items → `/PACT:comPACT` (parallelize if independent)
       - Multi-domain items → `/PACT:orchestrate`
       - Mixed (both single and multi-domain) → Use `/PACT:comPACT` for the single-domain batch AND `/PACT:orchestrate` for the multi-domain batch (can run in parallel if independent)
     - After all fixes complete, re-run review to verify fixes only (not a full PR re-review)
     - **Termination**: If blocking items persist after 2 fix-verify cycles → escalate via `/PACT:imPACT`
   - **Minor + Future**:
     - **Before proceeding**: Ask user "Would you like to review the remaining minor and future recommendations together?"
       - If **No**: Skip to step 4 directly
       - If **Yes**: Continue with recommendation review flow below:
         - Use `AskUserQuestion` tool with one question per recommendation (table from step 2 provides context):
           - Each minor: "Address [recommendation] now?" with description explaining the issue context
           - Each future: "Create GitHub issue for [recommendation]?" with description explaining the issue context
           - Note: Tool supports up to 4 questions per call. If >4 recommendations exist, make multiple `AskUserQuestion` calls to cover all items.
         - **Collect all answers first**, then batch work:
           - Group all minor=Yes items → Select workflow based on combined scope:
             - Single-domain items → `/PACT:comPACT` (parallelize if independent)
             - Multi-domain items → `/PACT:orchestrate`
           - Group all future=Yes items → Create GitHub issues
         - If any minor items fixed → re-run review to verify fixes only (not a full PR re-review)

4. State merge readiness (only after ALL blocking fixes complete AND minor/future item handling is done): "Ready to merge" or "Changes requested: [specifics]"

5. Present to user and **stop** — merging requires explicit user authorization (S5 policy)

---

**After user-authorized merge**: Run `/PACT:pin-memory` to update the project `CLAUDE.md` with the latest changes.
