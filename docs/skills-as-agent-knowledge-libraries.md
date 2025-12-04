# Skills as Agent Knowledge Libraries

> An architectural pattern for enhancing PACT agents with Claude Code Skills

## Overview

This document describes an integration pattern where Claude Code **Skills** serve as shared knowledge libraries that PACT **Agents** invoke during autonomous execution. This separates concerns: agents define *behavior*, skills provide *knowledge*.

## The Problem

Current PACT agent prompts mix two concerns:

1. **Behavioral instructions** - What the agent does and how it operates
2. **Reference knowledge** - Templates, checklists, patterns, best practices

This creates several issues:

- **Duplication**: Security guidelines repeated across backend, frontend, and database agents
- **Maintenance burden**: Updating a template requires editing multiple agent files
- **Context bloat**: Agents load all reference material even when not needed
- **Tight coupling**: Knowledge can't be shared or reused independently

## The Solution

Separate behavioral instructions (agents) from reference knowledge (skills):

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                            │
│               (delegates to agents, may invoke skills)       │
└──────────────────────────┬──────────────────────────────────┘
                           │ delegates
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐       ┌─────────┐        ┌─────────┐
   │ AGENTS  │       │ AGENTS  │        │ AGENTS  │
   │preparer │       │architect│        │ coders  │
   └────┬────┘       └────┬────┘        └────┬────┘
        │ invokes         │ invokes          │ invokes
        ▼                 ▼                  ▼
   ┌─────────┐       ┌─────────┐        ┌─────────┐
   │ SKILLS  │       │ SKILLS  │        │ SKILLS  │
   │research │       │patterns │        │standards│
   │templates│       │diagrams │        │security │
   └─────────┘       └─────────┘        └─────────┘
```

**Agents** remain autonomous executors with the `Task` tool, handling complex multi-step work.

**Skills** become on-demand knowledge libraries invoked via the `Skill` tool when agents need reference material.

## Benefits

| Benefit | Description |
|---------|-------------|
| **Separation of concerns** | Agents define behavior; skills provide knowledge |
| **DRY principle** | Security guidelines shared across all coders via one skill |
| **Lighter agent prompts** | Move bulky reference material to skills |
| **Progressive disclosure** | Skills loaded only when agents need them |
| **Easier maintenance** | Update a skill once, all agents benefit |
| **Composability** | Agents invoke multiple skills as needed |
| **Cross-platform reach** | Skills also work on Claude.ai and API |

## Implementation

### 1. Enable Skills in Agent Frontmatter

Add `Skill` to each agent's tools list:

```yaml
---
name: pact-architect
description: ...
tools: Task, Glob, Grep, LS, Read, Edit, Write, WebFetch, TodoWrite, WebSearch, Skill
---
```

### 2. Add Skill Invocation Guidance to Agent Prompts

Include instructions for when to invoke skills:

```markdown
## Reference Skills

When you need specialized reference material, invoke these skills:

- **pact-architecture-patterns**: C4 diagram templates, microservices patterns,
  API contract templates. Invoke when designing system components.
- **pact-security-guidelines**: OWASP checklist, input validation patterns,
  authentication best practices. Invoke when implementing security-sensitive code.
```

### 3. Create the Skills

Each skill follows the standard Claude Code skill format:

```
pact-architecture-patterns/
├── SKILL.md                      # Frontmatter + core instructions
└── references/
    ├── c4-diagram-templates.md   # Component/container diagram templates
    ├── api-contract-template.md  # OpenAPI/GraphQL contract patterns
    ├── microservices-patterns.md # Common architectural patterns
    └── anti-patterns.md          # What to avoid
```

**SKILL.md structure:**

```markdown
---
name: pact-architecture-patterns
description: Architecture pattern references for system design. Invoke when
  designing components, APIs, or system boundaries. Provides C4 templates,
  microservices patterns, and API contract formats.
---

# Architecture Patterns Reference

Use these patterns when designing system architecture...

[Core patterns and guidance here]

## Additional References

For detailed templates, see the `references/` directory:
- `c4-diagram-templates.md` - Component and container diagram formats
- `api-contract-template.md` - REST and GraphQL contract patterns
...
```

### 4. Install Skills

Skills can be installed via:

- **Plugin marketplace**: `/plugin marketplace add pact-skills`
- **Local directory**: Place in `.claude/skills/` or project `skills/` folder
- **Direct upload**: Upload to Claude.ai settings (for non-Claude Code use)

## Proposed Skill Set

| Skill | Primary Users | Contents |
|-------|---------------|----------|
| `pact-research-patterns` | pact-preparer | Source evaluation criteria, API documentation templates, technology comparison matrices, documentation structure guidelines |
| `pact-architecture-patterns` | pact-architect | C4 diagram templates, microservices patterns, event-driven patterns, API contract templates, database schema patterns |
| `pact-code-standards` | all coders | Language-specific best practices, error handling patterns, naming conventions, code organization guidelines |
| `pact-security-guidelines` | all coders, tester | OWASP Top 10 checklist, input validation patterns, authentication/authorization patterns, secrets management |
| `pact-testing-patterns` | pact-test-engineer | Test strategy templates, coverage requirements, E2E testing patterns, performance testing guidelines |

## Usage Flow Example

1. Orchestrator delegates architecture task to `pact-architect` agent
2. Agent analyzes requirements from preparation docs
3. Agent invokes `pact-architecture-patterns` skill for C4 templates
4. Skill provides diagram templates and pattern guidance
5. Agent applies templates to current project context
6. Agent produces architecture documentation with proper diagrams

```
Orchestrator: "Design the authentication system architecture"
     │
     ▼
pact-architect agent (autonomous execution)
     │
     ├── Reads docs/preparation/*.md
     │
     ├── Invokes Skill: pact-architecture-patterns
     │        └── Gets: C4 templates, auth patterns
     │
     ├── Invokes Skill: pact-security-guidelines
     │        └── Gets: OAuth patterns, session management
     │
     └── Produces: docs/architecture/auth-system.md
```

## Comparison: Before and After

### Before (Knowledge in Agent Prompts)

```markdown
# pact-architect.md (500+ lines)

You are the PACT Architect...

## How to Create C4 Diagrams
[50 lines of C4 guidance]

## API Contract Templates
[100 lines of templates]

## Microservices Patterns
[80 lines of patterns]

## Security Architecture Patterns
[70 lines duplicated from other agents]
...
```

### After (Knowledge in Skills)

```markdown
# pact-architect.md (150 lines)

You are the PACT Architect...

## Reference Skills

Invoke these skills when you need reference material:
- pact-architecture-patterns: Diagrams, patterns, contracts
- pact-security-guidelines: Security architecture patterns

[Focus on behavioral instructions, workflow, quality gates]
```

## Relationship to Cross-Platform Usage

This pattern provides a bonus: skills work beyond Claude Code.

- **Claude.ai users**: Can invoke skills directly for PACT methodology guidance
- **API integrations**: Skills provide structured knowledge for custom tooling
- **Learning/onboarding**: Skills teach PACT patterns without requiring full agent setup

A user on Claude.ai could invoke `pact-architecture-patterns` to get C4 templates even without the full PACT agent infrastructure.

## Next Steps

1. **Prototype one skill**: Start with `pact-architecture-patterns` as proof of concept
2. **Update one agent**: Add Skill tool to `pact-architect` and test invocation
3. **Validate the pattern**: Confirm skills load correctly and provide value
4. **Expand**: Create remaining skills and update other agents
5. **Package**: Create `pact-skills` plugin for marketplace distribution

## References

- [Claude Code Skills Documentation](https://github.com/anthropics/skills)
- [How to Create Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/spec/agent-skills-spec.md)
