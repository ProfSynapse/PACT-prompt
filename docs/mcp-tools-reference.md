# MCP Tools Reference Index

**Purpose**: Centralized reference for MCP tool guidance across PACT framework Skills and Agents.

**Last Updated**: 2025-12-05

---

## Overview

This document provides a reverse lookup index for MCP tool documentation in the PACT framework. Use this to quickly find:
- **WHEN/WHY to use an MCP tool** → Check the linked Skill
- **HOW to use an MCP tool** → Check the linked Agent

---

## sequential-thinking

**Full Tool Name**: `mcp__sequential-thinking__sequentialthinking`

**What it does**: Extended reasoning capability for complex decisions. Enables systematic, transparent reasoning through multi-step problems with auditable thought processes.

### When to Use Guidance (Skills)

| Skill | Domain Focus |
|-------|--------------|
| `pact-architecture-patterns` | Architectural decisions, pattern selection, component boundaries |
| `pact-prepare-research` | Technology comparisons, framework evaluation, trade-off analysis |
| `pact-backend-patterns` | Backend architecture choices, service design decisions |
| `pact-frontend-patterns` | Frontend framework selection, state management decisions |
| `pact-database-patterns` | Database design decisions, schema modeling choices |
| `pact-testing-patterns` | Test strategy planning, coverage decisions |
| `pact-security-patterns` | Threat modeling, security architecture decisions |
| `pact-api-design` | API design decisions, versioning strategies |

### How to Use Guidance (Agents)

| Agent | Phase | Focus |
|-------|-------|-------|
| `pact-preparer` | Prepare | Research-phase reasoning, technology evaluation |
| `pact-architect` | Architect | Design-phase reasoning, architectural decisions |
| `pact-backend-coder` | Code | Implementation reasoning, backend patterns |
| `pact-frontend-coder` | Code | Implementation reasoning, frontend patterns |
| `pact-database-engineer` | Code | Data modeling reasoning, schema decisions |
| `pact-test-engineer` | Test | Test planning reasoning, coverage strategy |

---

## context7

**Full Tool Name**: `mcp__context7__resolve-library-id`, `mcp__context7__get-library-docs`

**What it does**: Fetch up-to-date, version-specific documentation from official library sources. Provides authoritative API references and code examples.

### When to Use Guidance (Skills)

| Skill | Domain Focus |
|-------|--------------|
| `pact-prepare-research` | Library documentation research, API exploration |

### How to Use Guidance (Agents)

| Agent | Phase | Focus |
|-------|-------|-------|
| `pact-preparer` | Prepare | Research workflow integration, documentation gathering |
| `pact-backend-coder` | Code | Just-in-time API reference (optional) |
| `pact-frontend-coder` | Code | Just-in-time API reference (optional) |

---

## playwright / puppeteer

**Full Tool Names**: `mcp__playwright__*`, `mcp__puppeteer__*`

**What it does**: Browser automation and testing tools. Enable UI testing, screenshot capture, form filling, and browser interaction.

### When to Use Guidance (Skills)

| Skill | Domain Focus |
|-------|--------------|
| `pact-testing-patterns` | E2E testing strategies, UI test automation patterns |

### How to Use Guidance (Agents)

| Agent | Phase | Focus |
|-------|-------|-------|
| `pact-test-engineer` | Test | E2E test implementation, browser automation |
| `pact-frontend-coder` | Code | UI verification during development (optional) |

---

## github

**Full Tool Name**: `mcp__github__*`

**What it does**: GitHub API integration for repository management, issues, pull requests, code search, and collaboration.

### When to Use Guidance (Skills)

| Skill | Domain Focus |
|-------|--------------|
| `pact-prepare-research` | Repository exploration, documentation discovery |

### How to Use Guidance (Agents)

| Agent | Phase | Focus |
|-------|-------|-------|
| All agents | All phases | PR creation, issue management, code collaboration |

---

## Quick Decision Guide

**"Should I use this MCP tool?"**
→ Read the relevant **Skill** for decision criteria and use cases

**"How do I invoke this MCP tool?"**
→ Read the relevant **Agent** for syntax and workflow integration

**"What MCP tools are relevant to my domain?"**
→ Check this index, find your Skill, see associated MCP tools

**"What if the MCP tool is unavailable?"**
→ Read the relevant **Agent** for fallback strategies

---

## Cross-Reference Pattern

Each MCP tool's documentation follows the hybrid pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                         USER QUESTION                        │
│                                                              │
│  "Should I use sequential-thinking for this decision?"       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                          SKILL                               │
│  (pact-architecture-patterns, pact-prepare-research, etc.)  │
│                                                              │
│  - WHEN to use (use case scenarios)                         │
│  - WHY to use (value proposition)                           │
│  - WHEN NOT to use (anti-patterns)                          │
│                                                              │
│  → Points to Agent for HOW                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ If YES, proceed to Agent
┌─────────────────────────────────────────────────────────────┐
│                          AGENT                               │
│  (pact-architect, pact-preparer, etc.)                      │
│                                                              │
│  - HOW to invoke (syntax, parameters)                       │
│  - HOW to integrate (workflow steps)                        │
│  - WHAT IF unavailable (fallback strategies)                │
│                                                              │
│  → Points to Skill for WHEN/WHY                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Maintenance Notes

**Adding New MCP Tools**:
1. Add entry to this index with tool name and description
2. Identify relevant Skills and Agents
3. Update Skills with WHEN/WHY guidance
4. Update Agents with HOW guidance
5. Verify bidirectional cross-references

**Updating Existing MCP Tools**:
1. Update this index if tool name or description changes
2. Update Agents for syntax changes (HOW)
3. Update Skills only if capabilities change (WHEN/WHY)
4. Add version notes to Agent documentation

**Deprecating MCP Tools**:
1. Mark `[DEPRECATED]` in this index
2. Add deprecation notice to Skills and Agents
3. Document migration path to replacement tool
4. Remove from index 12 months after deprecation

---

## Related Documents

- **Joint Recommendation**: `docs/architecture/mcp-tools-joint-recommendation.md`
- **Skills Directory**: `skills/pact-*/SKILL.md`
- **Agents Directory**: `claude-agents/pact-*.md`
