---
description: Triage when stuck - determine if redo and/or help needed
argument-hint: [e.g., can't implement auth due to missing API spec]
---
You're stuck on: $ARGUMENTS

Triage with two questions:

1. **Redo prior phase?** — Is the issue upstream in P→A→C→T?
2. **Ask for help?** — Do I need subagents to assist?

Three possible outcomes:
- **Redo solo**: Loop back and fix the prior phase yourself
- **Redo with help**: Loop back with subagent assistance
- **Proceed with help**: Invoke subagents to help move forward

If neither question is "Yes," you're not actually stuck—continue working.

After triage, take the appropriate action. Document what went wrong in `docs/impact/` if it reveals a pattern worth capturing.
