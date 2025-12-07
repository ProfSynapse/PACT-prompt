# Codebase Context

> Single source of truth for understanding the PACT Framework Prompts repository.

## Repository Purpose

This is the **PACT Framework Prompts** repository - a collection of ready-to-use prompts, sub-agents, and skills that implement the PACT (Prepare, Architect, Code, Test) framework for principled AI-assisted software development.

**This repository IS the product** - the prompts and agent definitions themselves. There is no application code to build, test, or run.

## Current State

**Status**: Active development
**Last Updated**: 2025-12-07
**Current Branch**: `feat/add-commands`

### Recent Significant Changes

| Date | Change | Impact |
|------|--------|--------|
| 2025-12-07 | **Phase 5 Optional Enhancements Complete** | Test suites, coupling-metrics docs, examples, component-graph template, C4 patterns reference |
| 2025-12-07 | **Phase 5 Complete: Experimental Skills** | 2 new skills with executable code (pact-code-analyzer, pact-diagram-generator) |
| 2025-12-05 | **MCP Tools Hybrid Integration** | Skills document WHEN/WHY; Agents document HOW; Validated with 3 pairings |
| 2025-12 | Skills ecosystem expansion (10 skills total) | Comprehensive knowledge libraries for all PACT phases |
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
│   ├── pact-security-patterns/ # OWASP Top 10, auth patterns
│   ├── pact-code-analyzer/     # Executable code analysis (Python/Node.js)
│   └── pact-diagram-generator/ # Mermaid diagram templates
│
└── docs/                       # Design documentation
    ├── skills-as-agent-knowledge-libraries.md  # Skills pattern doc
    ├── mcp-tools-reference.md  # MCP tool reference index (for maintainers)
    ├── preparation/            # Research docs from Prepare phases
    ├── architecture/           # Architecture specs from Architect phases
    │   └── mcp-tools-joint-recommendation.md  # MCP integration design
    └── reviews/                # Multi-agent review outputs
        └── mcp-integration-validation-report.md  # Phase 3 validation
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

### 4. MCP Tools Hybrid Approach

MCP tools guidance is split between Skills and Agents:

```
Skills (WHEN/WHY)              Agents (HOW)
─────────────────              ────────────
• Use case scenarios           • Invocation syntax
• Decision criteria            • Workflow integration
• Anti-patterns                • Fallback strategies
• Value proposition            • Phase-specific examples
```

**Key principle**: Skills remain portable (valuable even if MCP tools unavailable); Agents provide operational workflow integration.

**Reference**: `docs/architecture/mcp-tools-joint-recommendation.md`

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
| `pact-code-analyzer` | Code | **Experimental** - Executable code metrics analysis | pact-architect, pact-backend-coder |
| `pact-diagram-generator` | Architect | **Experimental** - Mermaid diagram templates | pact-architect |

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
- **MCP tools**: Invoked directly as function calls (e.g., `mcp__sequential-thinking__sequentialthinking(...)`)
- **Skills**: Loaded via Skill tool for knowledge libraries in `~/.claude/skills/`
- **Built-in tools**: Read, Write, Edit, Grep, Glob, Bash for general operations
- Skills document WHEN/WHY to use MCP tools; Agents document HOW
- See `docs/mcp-tools-reference.md` for tool-to-documentation mapping

## Known Constraints

1. **No Application Code**: This repo contains only prompts and configurations
2. **Cross-Platform Compatibility**: Changes must work across Claude Code, Roo Code, Cursor, Cline
3. **Skills Location**: Users must install skills to `~/.claude/skills/` for agent access
4. **Agent Metadata**: Frontmatter format must match Claude Code expectations

## Experimental Skills (Phase 5)

Two new skills push the boundaries of what skills can do, introducing executable code capabilities:

### pact-code-analyzer
Provides executable scripts for objective code quality measurement:
- **Python scripts**: `complexity_analyzer.py`, `coupling_detector.py`, `dependency_mapper.py`, `file_metrics.py`
- **Node.js AST analyzer**: `js-complexity-analyzer.js` for accurate JS/TS cyclomatic complexity
- **Metrics**: Cyclomatic complexity, coupling analysis, dependency mapping, file-level metrics
- **References**: `complexity-calculation.md`, `dependency-analysis.md`, `coupling-metrics.md`, `script-integration.md`
- **Examples**: `pre-refactoring-analysis.md`, `test-prioritization.md`
- **Test suite**: 73 test cases with fixtures for Python/JavaScript/TypeScript
- **Design spec**: `docs/architecture/phase5-code-analyzer-design.md`

### pact-diagram-generator
Provides Mermaid diagram templates for consistent architecture visualization:
- **Templates**: C4 context, C4 container, sequence diagrams, ER diagrams, component dependency graphs
- **References**: `mermaid-syntax-guide.md`, `validation-guide.md`, `troubleshooting.md`, `c4-mermaid-patterns.md`
- **Examples**: `e-commerce-architecture.md`, `authentication-flow.md`
- **Design spec**: `docs/architecture/phase5-diagram-generator-design.md`

**Security considerations**: See `docs/architecture/phase5-security-analysis.md`

## Future Considerations

- Additional specialized agents for specific domains (mobile, DevOps, etc.)
- Enhanced skill cross-referencing capabilities
- Integration with additional AI coding assistants
- Production validation of experimental skills (pact-code-analyzer, pact-diagram-generator)

---

## Changelog

### 2025-12-07 (Update 2)
- Completed Phase 5 optional enhancements via parallel PACT agent delegation:
  - **pact-code-analyzer**:
    - Added `references/coupling-metrics.md` - comprehensive coupling analysis guide
    - Added `examples/` directory with `pre-refactoring-analysis.md` and `test-prioritization.md`
    - Added `scripts/tests/` with 73 test cases and fixtures for Python/JS/TS
  - **pact-diagram-generator**:
    - Added `templates/component-graph-mermaid.md` - component dependency visualization
    - Added `references/c4-mermaid-patterns.md` - comprehensive C4 patterns guide
    - Added `examples/` directory with `e-commerce-architecture.md` and `authentication-flow.md`
  - **Agent integration**:
    - Updated `pact-architect.md` with skill references to both experimental skills
    - Added skill consultation order guidance for existing codebase analysis

### 2025-12-07
- Documented Phase 5 completion: experimental skills implementation
  - Added `pact-code-analyzer` skill with executable Python scripts and Node.js AST analyzer
  - Added `pact-diagram-generator` skill with Mermaid diagram templates
  - Design specs: `phase5-code-analyzer-design.md`, `phase5-diagram-generator-design.md`
  - Security analysis: `phase5-security-analysis.md`
- Updated skills count from 8 to 10 (total skills in ecosystem)
- Updated repository structure to include new experimental skills
- Added "Experimental Skills (Phase 5)" section documenting new capabilities
- Updated Future Considerations to include experimental skills validation

### 2025-12-05 (Update 2)
- Documented MCP Tools Hybrid Integration completion
  - Phase 1: All 8 skills updated with "MCP Tools for [Domain]" sections
  - Phase 2: All 6 agents updated with "MCP Tools in [Phase] Phase" sections
  - Phase 3: Validation report created (`docs/reviews/mcp-integration-validation-report.md`)
- Added MCP Tools Hybrid Approach as architectural pattern #4
- Updated repository structure to include architecture and review artifacts
- Clarified MCP tools vs Skills vs built-in tools distinction

### 2025-12-05
- Created initial `codebase-context.md`
- Documented current repository structure and patterns
- Captured skills ecosystem (8 skills)
- Documented MCP tools integration
- Added slash commands documentation
