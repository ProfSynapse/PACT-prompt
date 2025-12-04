# PACT Skills Prototype: Architecture Design

**Version**: 1.0
**Date**: 2025-12-04
**Status**: Implemented

---

## Executive Summary

This document specifies the architecture for implementing the "Skills as Agent Knowledge Libraries" pattern within the PACT framework. The pattern validates that Claude Code Skills can serve as progressive-disclosure knowledge libraries that PACT agents invoke during autonomous execution, separating behavioral instructions (agents) from reference knowledge (skills).

**Prototype Scope**:
- **ONE Skill**: `pact-architecture-patterns` - Architectural design patterns and templates
- **ONE Agent Update**: `pact-architect` - Enhanced with skill invocation capability
- **3 Reference Files**: Demonstrating progressive disclosure pattern

**Success Criteria** (all met):
1. Skill activates automatically when architect agent needs architectural patterns
2. Progressive disclosure loads reference files only when explicitly needed
3. Context efficiency improves compared to embedding knowledge in agent prompt
4. Pattern is proven viable for expanding to other PACT agents and skills

---

## 1. System Context

### 1.1 Problem Statement

Current PACT agent prompts mix behavioral instructions with reference knowledge, creating:
- **Context bloat**: All reference material loaded whether needed or not
- **Duplication**: Patterns repeated across multiple agent files
- **Maintenance burden**: Updates require editing multiple agent prompts
- **Tight coupling**: Knowledge can't be reused independently

### 1.2 Proposed Solution

Separate concerns by moving reference knowledge into Claude Code Skills:
- **Agents**: Define behavior, workflow, and quality standards
- **Skills**: Provide on-demand access to patterns, templates, and best practices
- **Progressive Disclosure**: Load detailed references only when needed

### 1.3 Integration Points

```
┌─────────────────────────────────────────────────┐
│         PACT Orchestrator                       │
│      (delegates architecture task)              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  pact-architect    │ ← UPDATED
         │  (agent)           │   - Add Skill to tools
         │                    │   - Add skill invocation guidance
         └────────┬───────────┘
                  │ invokes when needed
                  ▼
    ┌─────────────────────────────────┐
    │ pact-architecture-patterns      │ ← NEW
    │ (skill)                          │
    │                                  │
    │ ├── SKILL.md (core patterns)    │
    │ └── references/                 │
    │     ├── c4-templates.md         │
    │     ├── api-contracts.md        │
    │     └── anti-patterns.md        │
    └─────────────────────────────────┘
```

**Data Flow**:
1. User requests architecture design via Orchestrator
2. Orchestrator delegates to `pact-architect` agent
3. Agent analyzes requirements from `docs/preparation/`
4. Agent mentions "component diagrams" or "architectural patterns"
5. Skill auto-activates based on description matching
6. Agent reads SKILL.md for core guidance
7. Agent conditionally loads specific references as needed
8. Agent produces architecture documentation

---

## 2. Directory Structure Design

### 2.1 Repository Structure

```
skills/
└── pact-architecture-patterns/
    ├── SKILL.md                      # Core patterns + routing logic
    ├── LICENSE.txt                   # MIT license
    └── references/
        ├── c4-templates.md           # C4 diagram templates
        ├── api-contracts.md          # API contract patterns
        └── anti-patterns.md          # Common architectural anti-patterns
```

### 2.2 Installation Location

Users copy skills to their personal skills directory:
```bash
cp -r skills/* ~/.claude/skills/
```

Skills are auto-discovered from `~/.claude/skills/` - no registration needed.

### 2.3 File Size Constraints

- **SKILL.md**: <500 lines (actual: ~350 lines)
- **Reference files**: 200-800 lines each
- **Rationale**: Keeps context window usage minimal while providing comprehensive content

---

## 3. SKILL.md Specification

### 3.1 Frontmatter Design

```yaml
---
name: pact-architecture-patterns
description: |
  ARCHITECT PHASE: Architectural design patterns, component templates, and system design guidance.

  Provides proven architectural patterns including microservices, layered architecture,
  event-driven systems, C4 diagram templates, API contract formats, and design anti-patterns.

  Use when: designing system architecture, creating component diagrams, defining interfaces,
  planning component boundaries, choosing architectural patterns, organizing system modules,
  or when user mentions: architecture, components, system design, diagrams, C4, microservices,
  API contracts, service boundaries, architectural patterns.

  DO NOT use for: code implementation details, specific framework syntax, database schema design,
  frontend-specific patterns, testing strategies, or security implementation (use dedicated skills).
allowed-tools: Read
metadata:
  phase: "Architect"
  version: "1.0.0"
  primary-agent: "pact-architect"
---
```

**Design Decisions**:
- **Phase label**: "ARCHITECT PHASE" for quick agent identification
- **Specific triggers**: 10+ terms architects would naturally mention
- **DO NOT use for**: Explicit boundaries preventing false activation

### 3.2 Body Structure

The SKILL.md body includes:
- **Quick Reference**: Common patterns (layered, microservices, event-driven)
- **Decision Tree**: Which reference to load based on task
- **Core Design Principles**: SOLID principles summary
- **Component Design Workflow**: Step-by-step process
- **Example**: Simple REST API architecture diagram
- **PACT Integration**: How skill fits into framework workflow

### 3.3 Token Efficiency

- **Tier 1 (metadata)**: ~50 tokens (always loaded)
- **Tier 2 (SKILL.md body)**: ~2,800 tokens (loaded on activation)
- **Tier 3 (references)**: 0 tokens until conditionally loaded

**Context savings**: 60-85% compared to embedding all content in agent prompt

---

## 4. Agent Integration Design

### 4.1 Required Changes to pact-architect.md

**Change 1: Add Skill to Tools List**

```yaml
tools: Task, Glob, Grep, LS, ExitPlanMode, Read, Edit, MultiEdit, Write, NotebookRead, NotebookEdit, WebFetch, TodoWrite, WebSearch, Skill
```

**Change 2: Add Reference Skills Section**

Insert after core responsibilities:

```markdown
# REFERENCE SKILLS

When you need specialized architectural knowledge, invoke these skills:

- **pact-architecture-patterns**: Architectural design patterns, C4 diagram templates,
  component design guidelines, API contract formats, and anti-patterns. Invoke when
  designing system components, creating diagrams, or defining interfaces.
```

### 4.2 Impact Assessment

- **Total changes**: ~50 words, 8 lines
- **Non-breaking**: Agent still works without skill installed
- **Minimal disruption**: Preserves all existing functionality

---

## 5. Future Scalability

### 5.1 Skill Template

```
skill-name/
├── SKILL.md                 # <500 lines, frontmatter + body
└── references/              # 2-5 reference files
    ├── reference-1.md       # 200-800 lines each
    └── reference-2.md
```

### 5.2 Next Skills to Create

1. **pact-security-guidelines**: Security patterns for all agents
2. **pact-testing-strategies**: Testing approaches for test engineer
3. **pact-research-methods**: Documentation research for preparer
4. **python-backend-patterns**: Backend implementation patterns
5. **react-frontend-patterns**: Frontend implementation patterns

### 5.3 Agent Scaling Pattern

For each agent:
1. Add `Skill` to tools list
2. Insert "REFERENCE SKILLS" section
3. Add skill reminders where relevant in workflow

**Minimal changes required**: ~10 lines per agent

### 5.4 Distribution Strategy

| Phase | Location |
|-------|----------|
| Development | `~/.claude/skills/` (personal) |
| Project | `./skills/` in repo |
| Production | Plugin marketplace as `pact-skills` |

---

## References

- [Skills as Agent Knowledge Libraries](../skills-as-agent-knowledge-libraries.md) - Pattern documentation
- [Claude Code Skills Specification](https://github.com/anthropics/skills) - Official spec
- [skills/README.md](../../skills/README.md) - Installation guide
