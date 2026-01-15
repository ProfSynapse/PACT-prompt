---
description: Pin important context permanently to CLAUDE.md (bypasses rolling memory window)
argument-hint: [e.g., critical gotcha, key architectural decision]
---
Pin this to CLAUDE.md permanently: $ARGUMENTS

This bypasses the pact-memory rolling window. Use sparingly for truly critical context.

## When to Pin

- **Critical gotchas** that would waste hours if forgotten
- **Key architectural decisions** that explain "why" (not "what")
- **Build/deploy commands** needed every session
- **Non-obvious patterns** unique to this codebase

## When NOT to Pin

- Routine session context (pact-memory handles this automatically)
- Things easily found in code or docs
- Temporary information that will become stale

## Process

1. Read existing CLAUDE.md structure
2. Add to appropriate section (prefer existing sections)
3. Keep entries concise (~5-10 lines max)
4. Remove any outdated pinned content
5. Commit changes

**Remember**: Working memory syncs automatically. Only pin what's truly permanent and critical.
