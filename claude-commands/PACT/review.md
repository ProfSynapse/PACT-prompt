---
description: Review the current work (commit, create PR, review)
argument-hint: [e.g., feature X implementation]
---
Review the current work: $ARGUMENTS

1. Commit any uncommitted work
2. Create a PR if one doesn't exist
3. Review the PR

**PR Review Workflow**

Pull request reviews should mirror real-world team practices where multiple reviewers sign off before merging. Invoke **2-3 agents in parallel** to provide comprehensive review coverage:

Recommended reviewer combinations:
- **General PR**: pact-architect + pact-optimizer + relevant coder (backend/frontend/database)
- **Backend-heavy PR**: pact-architect + pact-optimizer + pact-backend-coder
- **Frontend-heavy PR**: pact-architect + pact-optimizer + pact-frontend-coder
- **Database PR**: pact-architect + pact-optimizer + pact-database-engineer
- **Full-stack PR**: pact-architect + pact-backend-coder + pact-frontend-coder

Each reviewer focuses on their expertise:
- **pact-architect**: Design coherence, architectural patterns, interface contracts, separation of concerns
- **pact-optimizer**: Performance implications, algorithmic efficiency, resource usage
- **pact-backend-coder**: Server-side implementation quality, API design, error handling
- **pact-frontend-coder**: UI implementation quality, accessibility, state management
- **pact-database-engineer**: Query efficiency, schema design, data integrity

Synthesize findings from all reviewers into a unified review summary with consolidated recommendations.
