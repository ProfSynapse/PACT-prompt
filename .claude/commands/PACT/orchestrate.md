---
description: Delegate a task to PACT specialist agents
argument-hint: [e.g., implement feature X]
---
Orchestrate specialist PACT agents through the PACT workflow (Prepare → Architect → Code → Test) to address: $ARGUMENTS

**Before starting**:
1. Create a feature branch if not already on one
2. Check for existing plan in `docs/plans/` for this task:
   - **APPROVED**: Use as implementation specification (see "Using a Plan" below)
   - **PENDING APPROVAL**: Ask user to approve first, or proceed without plan
   - **BLOCKED**: Plan has unresolved conflicts — ask user to resolve via `/PACT:plan-mode` or proceed without plan
   - **IN_PROGRESS**: Implementation already underway — confirm continuation or restart
   - **SUPERSEDED/IMPLEMENTED**: Confirm with user before proceeding

**Using a Plan**:

When an APPROVED plan exists, pass relevant sections to specialists:
- **Prepare phase**: Share "Preparation Phase" section + "Open Questions > Require Further Research"
- **Architect phase**: Share "Architecture Phase" section + "Key Decisions" + "Interface Contracts"
- **Code phase**: Share "Code Phase" section + "Implementation Sequence" + "Commit Sequence"
- **Test phase**: Share "Test Phase" section + "Test Scenarios" + "Coverage Targets"

Include in each specialist prompt: "Reference the approved plan at `docs/plans/{slug}-plan.md` for context."

**Status transitions** (orchestrator responsibility):
- After starting implementation: Update plan status from APPROVED → IN_PROGRESS
- After successful completion: Update plan status from IN_PROGRESS → IMPLEMENTED
