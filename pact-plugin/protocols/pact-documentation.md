## Documentation Locations

| Phase | Output Location |
|-------|-----------------|
| Plan | `docs/plans/` |
| Prepare | `docs/preparation/` |
| Architect | `docs/architecture/` |

**Plan vs. Architecture artifacts**:
- **Plans** (`docs/plans/`): Pre-approval roadmaps created by `/PACT:plan-mode`. Created *before* implementation begins.
- **Architecture** (`docs/architecture/`): Formal specifications created by `pact-architect` *during* the Architect phase.

**No persistent logging for CODE/TEST phases.** Context passes via structured handoffs between agents. Git commits capture the audit trail.

---

## Session Continuity

If work spans sessions, update CLAUDE.md with:
- Current phase and task
- Blockers or open questions
- Next steps

---
