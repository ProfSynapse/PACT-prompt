# Codebase Context

> Single source of truth for understanding the PACT Framework Prompts repository.

## Repository Purpose

This is the **PACT Framework Prompts** repository - a collection of ready-to-use prompts, sub-agents, and skills that implement the PACT (Prepare, Architect, Code, Test) framework for principled AI-assisted software development.

**This repository IS the product** - the prompts and agent definitions themselves. There is no application code to build, test, or run.

## Current State

**Status**: Active development
**Last Updated**: 2025-12-05
**Current Branch**: `feat/add-commands`

### Recent Significant Changes

| Date | Change | Impact |
|------|--------|--------|
| 2025-12 | MCP Tools integration across all skills and agents | All agents now clarify when to use MCP tools vs Claude Code built-in tools |
| 2025-12 | Skills ecosystem expansion (8 skills total) | Comprehensive knowledge libraries for all PACT phases |
| 2025-12 | Knowledge migration from agents to skills | Agents are now leaner; duplicated knowledge moved to shared skills |
| 2025-12 | Added PACT slash commands | `/PACT:orchestrate`, `/PACT:peer-review`, `/PACT:update-context` |

## Repository Structure

```
.
├── PACT_Prompt.md              # Universal PACT framework prompt
├── PACT_Roo_Code.json          # Roo Code specialist modes (7 modes)
├── README.md                   # User-facing documentation
├── codebase-context.md         # This file - project state tracking
│
├── claude-agents/              # Claude Code sub-agents
│   ├── CLAUDE.md               # PACT Orchestrator (coordinator)
│   ├── pact-preparer.md        # Prepare phase specialist
│   ├── pact-architect.md       # Architect phase specialist
│   ├── pact-backend-coder.md   # Backend coding specialist
│   ├── pact-frontend-coder.md  # Frontend coding specialist
│   ├── pact-database-engineer.md # Database specialist
│   └── pact-test-engineer.md   # Testing specialist
│
├── claude-commands/            # PACT slash commands
│   └── PACT/
│       ├── orchestrate.md      # Delegate task to PACT agents
│       ├── peer-review.md      # Multi-agent PR review workflow
│       └── update-context.md   # Update this file
│
├── skills/                     # Claude Code Skills (knowledge libraries)
│   ├── README.md               # Skills installation guide
│   ├── pact-prepare-research/  # Research methodologies
│   ├── pact-architecture-patterns/ # C4, API contracts, anti-patterns
│   ├── pact-api-design/        # REST/GraphQL patterns
│   ├── pact-backend-patterns/  # Service patterns, error handling
│   ├── pact-frontend-patterns/ # Component patterns, state management
│   ├── pact-database-patterns/ # Schema design, query optimization
│   ├── pact-testing-patterns/  # Test strategies, coverage
│   └── pact-security-patterns/ # OWASP Top 10, auth patterns
│
└── docs/                       # Design documentation
    ├── skills-as-agent-knowledge-libraries.md  # Skills pattern doc
    ├── mcp-tools-reference.md  # MCP vs built-in tools guide
    ├── preparation/            # Research docs from Prepare phases
    ├── architecture/           # Architecture specs from Architect phases
    └── reviews/                # Multi-agent review outputs
```

## Key Architectural Patterns

### 1. Agent-Skill Separation

Agents contain behavioral instructions; skills contain reference knowledge:

```
Agent (lean prompt) ──invokes──> Skill (SKILL.md) ──loads──> References
```

**Benefits**: 60-85% context savings, progressive disclosure, shared knowledge

### 2. Hierarchical Delegation

```
PACT Orchestrator (coordinates, never codes)
    │
    ├── pact-preparer ──> docs/preparation/
    ├── pact-architect ──> docs/architecture/
    ├── pact-backend-coder ──> source code
    ├── pact-frontend-coder ──> source code
    ├── pact-database-engineer ──> schemas/migrations
    └── pact-test-engineer ──> test suites
```

### 3. Phase-Gated Workflow

Prepare → Architect → Code → Test

Each phase produces artifacts that feed into the next phase. Quality gates ensure phase completion before progression.

## Skills Ecosystem

| Skill | Phase | Purpose | Primary Users |
|-------|-------|---------|---------------|
| `pact-prepare-research` | Prepare | Research methodologies, source evaluation | pact-preparer |
| `pact-architecture-patterns` | Architect | C4 diagrams, system design patterns | pact-architect |
| `pact-api-design` | Cross-cutting | REST/GraphQL patterns, versioning | pact-architect, pact-backend-coder |
| `pact-backend-patterns` | Code | Service patterns, error handling | pact-backend-coder |
| `pact-frontend-patterns` | Code | Component patterns, state management | pact-frontend-coder |
| `pact-database-patterns` | Code | Schema design, query optimization | pact-database-engineer |
| `pact-testing-patterns` | Test | Test strategies, coverage guidelines | pact-test-engineer |
| `pact-security-patterns` | Cross-cutting | OWASP Top 10, auth patterns | All agents |

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/PACT:orchestrate` | Delegate a task to PACT specialist agents |
| `/PACT:peer-review` | Commit, create PR, run multi-agent review |
| `/PACT:update-context` | Update this codebase-context.md file |

## Important Conventions

### File Size Limits
- Maximum 500-600 lines per file for maintainability
- Split larger files into logical modules

### Documentation Locations
- Research outputs → `docs/preparation/`
- Architecture specs → `docs/architecture/`
- Review outputs → `docs/reviews/`

### MCP Tools vs Built-in Tools
- **MCP tools**: Use for specialized capabilities (GitHub, Playwright, filesystem operations on allowed directories)
- **Built-in tools**: Use for general operations (Read, Write, Edit, Grep, Glob, Bash)
- See `docs/mcp-tools-reference.md` for detailed guidance

## Known Constraints

1. **No Application Code**: This repo contains only prompts and configurations
2. **Cross-Platform Compatibility**: Changes must work across Claude Code, Roo Code, Cursor, Cline
3. **Skills Location**: Users must install skills to `~/.claude/skills/` for agent access
4. **Agent Metadata**: Frontmatter format must match Claude Code expectations

## Future Considerations

- Additional specialized agents for specific domains (mobile, DevOps, etc.)
- Enhanced skill cross-referencing capabilities
- Integration with additional AI coding assistants

---

## Changelog

### 2025-12-05
- Created initial `codebase-context.md`
- Documented current repository structure and patterns
- Captured skills ecosystem (8 skills)
- Documented MCP tools integration
- Added slash commands documentation
