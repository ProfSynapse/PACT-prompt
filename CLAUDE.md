# Project Memory

This file contains project-specific memory managed by the PACT framework.
The global PACT Orchestrator is loaded from `~/.claude/CLAUDE.md`.

## Release Process

**When to bump version**: Bump version number in BOTH files:
- Before merging any PR
- When making direct changes to main (no PR)

**Files to update**:
- `.claude-plugin/marketplace.json` (line 15: `"version"`)
- `pact-plugin/.claude-plugin/plugin.json` (version field)

**Process**:
1. Review changes to recommend appropriate version bump (MAJOR.MINOR.PATCH)
2. Get user approval on the recommended version number
3. Update both files with approved version
4. Commit:
   - **PRs**: Version bump as a separate commit before merge
   - **Direct to main**: Combine version bump with the change commit

Users update via `/plugin marketplace update pact-marketplace` then `/plugin update PACT`.

## Key Features

### Workflow Compaction Refresh (PR #88)
PreCompact and SessionStart hooks that preserve PACT workflow state across context compaction:
- `hooks/precompact_refresh.py` - Captures workflow state before compaction
- `hooks/compaction_refresh.py` - Injects refresh instructions after compaction
- `hooks/refresh/` - Shared utilities for workflow detection and checkpoint building
- 661 tests covering all PACT workflows (orchestrate, peer-review, plan-mode, comPACT, rePACT, imPACT)

Enables seamless workflow resumption when Claude Code auto-compacts mid-session.

## Retrieved Context
<!-- Auto-managed by pact-memory skill. Last 3 retrieved memories shown. -->

## Working Memory
<!-- Auto-managed by pact-memory skill. Last 5 memories shown. Full history searchable via pact-memory skill. -->
<!-- Hook test: 2026-01-22 -->
