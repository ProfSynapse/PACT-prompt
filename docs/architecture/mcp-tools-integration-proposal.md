# MCP Tools Integration Architecture for PACT Framework

**Architecture Date**: 2025-12-05
**Architect**: PACT Architect
**Phase**: Architect (PACT Framework)
**Status**: Design Proposal

---

## Executive Summary

This architecture defines how Model Context Protocol (MCP) tools should be integrated into the PACT framework across agents and skills. The design establishes clear boundaries between MCP tools (functional capabilities) and Skills (knowledge libraries), determines appropriate tool access patterns, and provides implementation guidelines for both existing and future PACT components.

**Key Architectural Decisions**:
1. **MCP Tools as Functional Capabilities**: MCP tools provide executable functionality (APIs, services), not static knowledge
2. **Skills Document Tool Usage**: Skills guide agents on when and how to use MCP tools
3. **Direct Agent Access**: Agents invoke MCP tools directly; Skills don't invoke MCP tools
4. **Phase-Appropriate Tools**: Different PACT phases benefit from different MCP capabilities
5. **Skill-Based Guidance**: MCP tool usage patterns and best practices documented in Skills

**Implementation Priority**: Update all Skills with MCP tool usage guidance, then update agent prompts with phase-appropriate MCP tool awareness.

---

## 1. MCP Tools vs Skills: Architectural Distinction

### 1.1 Core Distinction

Section 3.5 of the skills-expansion-design.md already establishes the fundamental distinction:

| Aspect | Claude Code Skills | MCP Tools |
|--------|-------------------|-----------|
| **Location** | `~/.claude/skills/` directory | External integrations via MCP servers |
| **Purpose** | Knowledge libraries (patterns, templates, checklists) | Functional capabilities (APIs, services) |
| **Invocation** | `Skill` tool (e.g., `Skill(pact-backend-patterns)`) | Direct function calls (e.g., `mcp__sequential-thinking__sequentialthinking()`) |
| **Prefix** | No prefix, hyphenated names | Always `mcp__` prefix |
| **Nature** | Static reference material | Dynamic executable functionality |

**Architectural Principle**: MCP tools DO things. Skills KNOW things.

### 1.2 Practical Examples

**MCP Tool (Functional)**:
```markdown
# Agent invokes sequential-thinking for complex reasoning
mcp__sequential-thinking__sequentialthinking(
  task: "Evaluate OAuth 2.0 vs JWT for this API based on requirements"
)
# Returns: Structured reasoning process and recommendation
```

**Skill (Knowledge)**:
```markdown
# Agent loads security patterns for reference knowledge
Read ~/.claude/skills/pact-security-patterns/SKILL.md
# Returns: Authentication patterns, security principles, threat models
```

**Combined Usage Pattern**:
```markdown
# 1. Load knowledge from Skill
Read ~/.claude/skills/pact-security-patterns/SKILL.md

# 2. Use MCP tool for complex reasoning based on that knowledge
mcp__sequential-thinking__sequentialthinking(
  task: "Given these security patterns, determine best auth strategy for microservices"
)

# 3. Apply combined knowledge + reasoning to implementation
```

### 1.3 Design Implication

**Skills guide MCP tool usage but don't invoke them.**

Skills document:
- WHEN to use specific MCP tools (contextual triggers)
- WHY a particular MCP tool is beneficial (use cases)
- HOW to structure prompts for MCP tools (effective patterns)
- WHAT knowledge to combine with MCP tool outputs

Agents orchestrate:
- Reading Skills for knowledge
- Invoking MCP tools for functionality
- Synthesizing both into project-specific solutions

---

## 2. Available MCP Tools Analysis

### 2.1 MCP Tools Inventory

Based on system context, these MCP tools are available:

| MCP Tool | Category | Capability | Relevance to PACT |
|----------|----------|------------|-------------------|
| `mcp__sequential-thinking__sequentialthinking` | Reasoning | Structured problem-solving through extended reasoning | HIGH - All phases benefit from systematic reasoning |
| `mcp__context7__resolve-library-id` | Documentation | Find library identifiers for documentation lookup | MEDIUM - Prepare phase research |
| `mcp__context7__get-library-docs` | Documentation | Fetch up-to-date library documentation | MEDIUM - Prepare phase research |
| `mcp__github__*` | Version Control | GitHub operations (issues, PRs, repos) | LOW - Operational, not design-focused |
| `mcp__filesystem__*` | File Operations | Advanced file operations | LOW - Agents already have Read/Write tools |
| `mcp__playwright__*` | Browser Automation | Automated browser testing | LOW - Specific to test automation |
| `mcp__puppeteer__*` | Browser Automation | Automated browser testing | LOW - Specific to test automation |

### 2.2 Priority MCP Tools for PACT

**Priority 1: sequential-thinking**
- **Status**: Already referenced in all Skill frontmatter
- **Usage**: Complex decision-making, pattern selection, trade-off analysis
- **PACT Phases**: All phases benefit
- **Action Required**: Document usage patterns in Skills

**Priority 2: context7 tools**
- **Status**: Not yet integrated
- **Usage**: Up-to-date library documentation during research
- **PACT Phases**: Primarily Prepare phase
- **Action Required**: Add to pact-prepare-research skill guidance

**Priority 3: Browser automation (playwright/puppeteer)**
- **Status**: Not yet integrated
- **Usage**: E2E testing and validation
- **PACT Phases**: Test phase only
- **Action Required**: Add to pact-testing-patterns skill if E2E testing guidance added

**Deferred: GitHub, filesystem tools**
- **Rationale**: Agents already have equivalent capabilities or tools are operational rather than design-focused
- **Future Consideration**: May add if specific workflow gaps identified

---

## 3. Integration Architecture by PACT Phase

### 3.1 Prepare Phase

**Primary MCP Tools**:
1. **sequential-thinking**: Technology comparison, research prioritization, requirement analysis
2. **context7**: Up-to-date library documentation lookup

**Integration Point**: `pact-prepare-research` skill

**Skill Updates Required**:

```markdown
## Using MCP Tools in Preparation

### sequential-thinking for Technology Decisions

When evaluating multiple technology options, use sequential-thinking to reason through trade-offs:

**When to use**:
- Comparing 3+ framework/library options
- Complex requirement analysis with competing concerns
- Evaluating architectural implications of technology choices

**Example prompt**:
> "I need to choose between React, Vue, and Svelte for a new dashboard application.
> Requirements: TypeScript support, component reusability, team learning curve, ecosystem maturity.
> Let me think through the trade-offs systematically..."

### context7 for Current Documentation

When researching libraries, use context7 to fetch the latest documentation:

**Workflow**:
1. Identify library: `mcp__context7__resolve-library-id(library: "react")`
2. Fetch docs: `mcp__context7__get-library-docs(library_id: "react", version: "18")`
3. Synthesize with official sources for comprehensive view

**When to use**:
- Verifying latest API changes before documenting
- Checking current best practices for popular libraries
- Ensuring documentation matches specific version
```

**Agent Awareness**: pact-preparer agent should mention context7 tools in workflow guidance.

---

### 3.2 Architect Phase

**Primary MCP Tools**:
1. **sequential-thinking**: Architecture pattern selection, component boundary decisions, trade-off analysis

**Integration Point**: `pact-architecture-patterns` skill

**Skill Updates Required** (section already exists, enhance it):

```markdown
## Architectural Decision Workflow

For complex pattern selection and system design, use sequential-thinking to reason through decisions systematically.

**When to use sequential-thinking:**
- Choosing between multiple viable architectural patterns
- Evaluating trade-offs for a specific context
- Designing component boundaries for complex systems
- Resolving conflicting requirements (e.g., performance vs. simplicity)

**Workflow:**

1. **Frame the Decision**
   - What architectural question needs answering?
   - What are the constraints and requirements?
   - What patterns are candidates?

2. **Analyze Each Option** (use sequential-thinking)
   - How does each pattern address the requirements?
   - What are the trade-offs in this specific context?
   - What risks does each option introduce?

3. **Evaluate Against Principles**
   - Does it follow SOLID principles?
   - Does it avoid known anti-patterns?
   - Is it appropriate for the team's expertise?

4. **Document the Decision**
   - Record the chosen pattern and rationale
   - Note rejected alternatives and why
   - Identify risks and mitigations

**Example sequential-thinking prompt:**
> "I need to choose between microservices and modular monolith for a mid-size e-commerce
> platform with a team of 5 developers. Let me think through the trade-offs systematically..."

**Additional Use Cases**:
- Database choice (SQL vs NoSQL vs hybrid)
- API design (REST vs GraphQL vs RPC)
- State management strategy (Redux vs Context vs Zustand)
- Deployment architecture (serverless vs containers vs VMs)
```

**Status**: pact-architecture-patterns already has this section (lines 71-103). Consider enhancing with more specific examples.

**Agent Awareness**: pact-architect agent already references this skill; no changes needed.

---

### 3.3 Code Phase

**Primary MCP Tools**:
1. **sequential-thinking**: Complex business logic design, error handling strategies, optimization decisions

**Integration Points**:
- `pact-backend-patterns` skill
- `pact-frontend-patterns` skill
- `pact-database-patterns` skill

**Skill Updates Required** (add to each coder skill):

```markdown
## Using sequential-thinking for Implementation Decisions

### Backend Implementation
**When to use**:
- Designing complex business logic workflows
- Planning error propagation and recovery strategies
- Optimizing database query patterns
- Architecting background job processing

**Example**:
> "I need to implement a payment processing flow with retries, refunds, and webhook notifications.
> Let me think through the state machine and error handling systematically..."

### Frontend Implementation
**When to use**:
- Complex state management architecture
- Performance optimization strategies (memoization, virtualization)
- Accessibility implementation for complex widgets
- Cross-browser compatibility planning

**Example**:
> "I need to implement an accessible data grid with sorting, filtering, and virtualization.
> Let me think through the component structure and state management..."

### Database Implementation
**When to use**:
- Schema migration strategies for production data
- Query optimization and index selection
- Data partitioning and sharding decisions
- Transaction isolation level selection

**Example**:
> "I need to add a new column to a table with 100M rows without downtime.
> Let me think through the migration strategy..."
```

**Agent Awareness**: Coder agents (backend, frontend, database) should be aware they can use sequential-thinking for complex implementation decisions.

---

### 3.4 Test Phase

**Primary MCP Tools**:
1. **sequential-thinking**: Test strategy design, coverage analysis, test data planning
2. **playwright/puppeteer** (if E2E testing): Browser automation for integration tests

**Integration Point**: `pact-testing-patterns` skill

**Skill Updates Required**:

```markdown
## Using MCP Tools in Testing

### sequential-thinking for Test Strategy

**When to use**:
- Designing comprehensive test coverage for complex features
- Planning test data and fixture strategies
- Evaluating test framework trade-offs
- Optimizing test suite performance

**Example**:
> "I need to test a multi-step checkout flow with payment processing, inventory updates,
> and email notifications. Let me think through the test pyramid strategy..."

### Browser Automation Tools (Advanced)

For E2E testing requiring browser automation:

**playwright**: Modern, cross-browser automation
**puppeteer**: Chrome/Chromium-focused automation

**When to use**:
- Visual regression testing
- Complex user interaction flows
- Testing SPAs with dynamic content
- Accessibility audits with real browsers

**Workflow**:
1. Define critical user journeys
2. Use playwright/puppeteer to automate browser interactions
3. Assert on UI state, network requests, console logs
4. Integrate with CI/CD for automated testing

**Note**: These tools require specific setup and are optional for most projects.
```

**Agent Awareness**: pact-test-engineer should be aware of browser automation tools if implementing E2E tests.

---

### 3.5 Cross-Cutting (All Phases)

**Primary MCP Tools**:
1. **sequential-thinking**: Universal reasoning tool applicable to any complex decision

**Integration Point**: `pact-security-patterns` skill

**Skill Updates Required**:

```markdown
## Using sequential-thinking for Security Analysis

Security decisions often involve complex trade-offs. Use sequential-thinking for:

**Threat Modeling**:
> "Given this microservices architecture with external API integrations,
> let me systematically identify potential threats using STRIDE methodology..."

**Authentication Strategy Selection**:
> "I need to choose between session-based, JWT, and OAuth for this application.
> Requirements: mobile app support, third-party integrations, security, scalability.
> Let me evaluate each option systematically..."

**Vulnerability Remediation Planning**:
> "We discovered a SQL injection vulnerability in the legacy search feature.
> Let me think through the safest remediation approach considering deployment constraints..."

**Compliance Analysis**:
> "We need to achieve SOC 2 compliance for our SaaS product.
> Let me map our current security controls to SOC 2 requirements systematically..."
```

---

## 4. Implementation Guidelines

### 4.1 Skill Update Pattern

For each skill that should reference MCP tools:

**Step 1: Add to Frontmatter** (if not already present)
```yaml
allowed-tools:
  - Read
  - [other tools...]
  - mcp__sequential-thinking__sequentialthinking
  - mcp__context7__resolve-library-id  # if relevant
  - mcp__context7__get-library-docs    # if relevant
```

**Step 2: Add Usage Section to SKILL.md**
```markdown
## Using MCP Tools with This Skill

### sequential-thinking
[When to use, example prompts, expected outcomes]

### [other MCP tools if relevant]
[When to use, example prompts, expected outcomes]
```

**Step 3: Reference in Workflows**
```markdown
## [Workflow Name]

1. Load relevant knowledge: Read this skill
2. For complex decisions: Use sequential-thinking
3. Apply combined knowledge to implementation
```

### 4.2 Agent Update Pattern

Agents should be aware of MCP tools but not duplicate Skill guidance.

**Agent Prompt Enhancement**:
```markdown
# AVAILABLE MCP TOOLS

You have access to Model Context Protocol tools for enhanced capabilities:

- **sequential-thinking**: Use for complex reasoning and decision-making
  Invoke when: Evaluating trade-offs, comparing multiple options, analyzing complex scenarios
  Pattern: `mcp__sequential-thinking__sequentialthinking(task: "description of decision")`

[Phase-specific tools based on agent role]

**Integration with Skills**: Skills provide patterns and knowledge; MCP tools provide reasoning
and functionality. Combine both for best results.
```

**Guideline**: Keep MCP tool descriptions brief in agents (2-3 lines each). Detailed usage patterns belong in Skills.

### 4.3 Documentation Update Checklist

For complete MCP tools integration:

**Skills Updates**:
- [ ] pact-prepare-research: Add sequential-thinking + context7 guidance
- [ ] pact-architecture-patterns: Enhance existing sequential-thinking section
- [ ] pact-backend-patterns: Add sequential-thinking for implementation
- [ ] pact-frontend-patterns: Add sequential-thinking for implementation
- [ ] pact-database-patterns: Add sequential-thinking for implementation
- [ ] pact-testing-patterns: Add sequential-thinking + browser automation
- [ ] pact-security-patterns: Add sequential-thinking for threat analysis
- [ ] pact-api-design: Add sequential-thinking for API design decisions

**Agent Updates** (optional, low priority):
- [ ] pact-preparer: Brief mention of context7 tools in research workflow
- [ ] pact-architect: Already references sequential-thinking via skill
- [ ] pact-backend-coder: Brief mention of sequential-thinking availability
- [ ] pact-frontend-coder: Brief mention of sequential-thinking availability
- [ ] pact-database-engineer: Brief mention of sequential-thinking availability
- [ ] pact-test-engineer: Brief mention of browser automation tools if E2E testing

---

## 5. Architectural Principles

### 5.1 Core Principles

**Principle 1: Skills Document, Agents Execute**
- Skills contain MCP tool usage patterns, examples, and best practices
- Agents read Skills, then invoke MCP tools based on guidance
- Avoids duplicating MCP tool guidance across agents

**Principle 2: MCP Tools Are First-Class Capabilities**
- MCP tools are not Skills; they are executable functions
- Agents invoke MCP tools directly, not via Skill tool
- Skills reference MCP tools in frontmatter `allowed-tools` but don't invoke them

**Principle 3: Phase-Appropriate Tool Access**
- Not all MCP tools are relevant to all phases
- Skills document which MCP tools are useful for their domain
- Agents have access to all MCP tools but use them selectively based on Skills guidance

**Principle 4: Progressive Disclosure**
- Basic MCP tool awareness in agent prompts (what exists)
- Detailed usage patterns in Skills (how to use effectively)
- Advanced patterns in Skill reference files (edge cases, optimizations)

**Principle 5: Knowledge + Reasoning = Better Outcomes**
- Skills provide domain knowledge (patterns, principles, examples)
- MCP tools provide reasoning capability (sequential-thinking) and functionality (context7, etc.)
- Agents combine both for optimal decision-making

### 5.2 Anti-Patterns to Avoid

**Anti-Pattern 1: Duplicating MCP Tool Guidance**
❌ Don't document MCP tool usage in both Skills and Agent prompts
✅ Do document once in Skills, reference briefly in Agents

**Anti-Pattern 2: Over-Relying on MCP Tools**
❌ Don't use sequential-thinking for trivial decisions
✅ Do use sequential-thinking for genuinely complex trade-offs

**Anti-Pattern 3: Treating MCP Tools as Skills**
❌ Don't try to invoke MCP tools via Skill tool: `Skill(mcp__sequential-thinking)`
✅ Do invoke MCP tools directly as functions: `mcp__sequential-thinking__sequentialthinking(task: "...")`

**Anti-Pattern 4: Skills Invoking MCP Tools**
❌ Don't put MCP tool invocations in Skill markdown
✅ Do document when and how agents should use MCP tools

**Anti-Pattern 5: Ignoring MCP Tool Output**
❌ Don't invoke MCP tools and ignore their structured output
✅ Do integrate MCP tool reasoning into decision documentation

---

## 6. MCP Tools by Phase Matrix

| MCP Tool | Prepare | Architect | Code | Test | Priority | Status |
|----------|---------|-----------|------|------|----------|--------|
| sequential-thinking | ✅ High | ✅ High | ✅ Medium | ✅ Medium | P1 | Documented in Skills frontmatter, needs usage patterns |
| context7 (resolve-library-id) | ✅ High | ❌ | ❌ | ❌ | P2 | Not yet integrated |
| context7 (get-library-docs) | ✅ High | ❌ | ❌ | ❌ | P2 | Not yet integrated |
| playwright | ❌ | ❌ | ❌ | ✅ Low | P3 | Conditional (if E2E testing) |
| puppeteer | ❌ | ❌ | ❌ | ✅ Low | P3 | Conditional (if E2E testing) |
| github | ⚠️ Optional | ⚠️ Optional | ⚠️ Optional | ⚠️ Optional | Deferred | Operational, not design-focused |
| filesystem | ❌ | ❌ | ❌ | ❌ | Deferred | Agents have Read/Write tools |

**Legend**:
- ✅ Recommended for this phase
- ⚠️ Optional/situational use
- ❌ Not applicable to this phase
- P1/P2/P3: Implementation priority

---

## 7. Implementation Roadmap

### 7.1 Phase 1: Document Core MCP Tool (sequential-thinking)

**Objective**: Enhance all Skills with sequential-thinking usage patterns

**Tasks**:
1. Update each Skill's SKILL.md with sequential-thinking section
2. Provide phase-specific examples of when to use sequential-thinking
3. Include example prompts for common decision scenarios
4. Document expected output integration patterns

**Success Criteria**:
- [ ] All 8 Skills have sequential-thinking usage guidance
- [ ] Each Skill has 2-3 concrete examples
- [ ] Guidance is phase-specific and actionable
- [ ] No duplication across Skills (each focuses on its domain)

**Estimated Effort**: 3-4 hours (30-40 minutes per Skill)

---

### 7.2 Phase 2: Integrate context7 for Prepare Phase

**Objective**: Add up-to-date documentation lookup to research workflow

**Tasks**:
1. Add context7 tools to pact-prepare-research frontmatter
2. Document when to use context7 vs WebSearch vs official docs
3. Provide workflow for combining context7 with other research methods
4. Update pact-preparer agent with brief context7 mention

**Success Criteria**:
- [ ] pact-prepare-research documents context7 usage
- [ ] Clear guidance on context7 vs other research methods
- [ ] Example workflow showing context7 integration
- [ ] pact-preparer agent aware of context7 availability

**Estimated Effort**: 1-2 hours

---

### 7.3 Phase 3: Add Browser Automation for Test Phase (Optional)

**Objective**: Enable E2E testing capabilities for projects that need it

**Tasks**:
1. Add playwright/puppeteer to pact-testing-patterns frontmatter
2. Document when E2E testing with browser automation is appropriate
3. Provide setup guidance and integration patterns
4. Note that these tools are optional and project-specific

**Success Criteria**:
- [ ] pact-testing-patterns has browser automation section
- [ ] Clear guidance on when to use vs skip
- [ ] Setup and integration patterns documented
- [ ] Marked as optional/advanced capability

**Estimated Effort**: 2-3 hours

**Conditional**: Only implement if E2E testing patterns are added to pact-testing-patterns

---

### 7.4 Phase 4: Agent Awareness Updates (Optional)

**Objective**: Add brief MCP tool mentions to agent prompts

**Tasks**:
1. Add "Available MCP Tools" section to each agent
2. List phase-appropriate tools with 1-2 line descriptions
3. Reference Skills for detailed usage patterns
4. Keep agent prompts lean (delegate details to Skills)

**Success Criteria**:
- [ ] Agents aware of MCP tools they can use
- [ ] No duplication of Skill content in agents
- [ ] Clear reference path: Agent → Skill → Detailed Guidance

**Estimated Effort**: 2-3 hours (20-30 minutes per agent)

**Priority**: Low - Skills already provide MCP tool guidance; agent updates are enhancement, not requirement

---

## 8. Decision Log

### Decision 1: Skills Document MCP Tool Usage, Not Agents

**Decision**: MCP tool usage patterns belong in Skills, not agent prompts

**Rationale**:
- Skills are already the knowledge repository for each domain
- Agents are orchestrators, not knowledge bases
- Reduces duplication across agents
- Follows "agents orchestrate, Skills provide knowledge" principle
- Easier to maintain MCP tool guidance in one place per domain

**Alternatives Considered**:
- Agent-centric: Each agent documents MCP tools they use
  - Rejected: Causes duplication, harder to maintain
- Hybrid: Basic in agents, detailed in Skills
  - Partially accepted: Optional brief mentions in agents, details in Skills

**Implications**:
- Skills receive updates first (higher priority)
- Agents receive optional awareness updates (lower priority)
- Skill frontmatter lists MCP tools in `allowed-tools`

---

### Decision 2: sequential-thinking as Priority 1

**Decision**: sequential-thinking is highest priority MCP tool for integration

**Rationale**:
- Already referenced in all Skill frontmatter
- Universally applicable across all PACT phases
- Addresses complex decision-making (core to principled development)
- Low integration cost (just document usage patterns)
- High value (improves decision quality in all phases)

**Alternatives Considered**:
- context7 first: Prepare-phase specific, narrower impact
- Browser automation first: Test-phase only, optional capability
- Equal priority: Dilutes implementation focus

**Implications**:
- Phase 1 focuses solely on sequential-thinking
- Other MCP tools deferred to later phases
- Quick win: All Skills enhanced within days

---

### Decision 3: context7 as Priority 2

**Decision**: context7 documentation tools are second priority

**Rationale**:
- Prepare phase is foundation of PACT workflow
- Up-to-date library docs critical for good research
- Complements existing WebSearch and official doc workflows
- Phase-specific (Prepare only), so lower priority than universal tools

**Alternatives Considered**:
- Skip context7: Agents can use WebSearch + official docs
  - Rejected: context7 provides version-specific, structured docs
- Higher priority than sequential-thinking
  - Rejected: Prepare-only vs all-phase impact

**Implications**:
- Implemented in Phase 2 after sequential-thinking
- Primarily benefits pact-prepare-research skill
- Optional enhancement (WebSearch still works)

---

### Decision 4: Browser Automation as Priority 3 (Conditional)

**Decision**: Browser automation tools are lowest priority and conditional

**Rationale**:
- Test-phase specific
- Not all projects need E2E testing
- Requires additional setup and infrastructure
- More advanced use case
- Playwright/puppeteer are specialized tools

**Alternatives Considered**:
- Skip entirely: Focus on unit/integration testing only
  - Partially accepted: Marked as optional/conditional
- Higher priority: E2E testing is critical for web apps
  - Rejected: Not all PACT projects are web apps

**Implications**:
- Implemented only if E2E testing section added to pact-testing-patterns
- Marked as optional/advanced in documentation
- Lower priority than core workflow MCP tools

---

## 9. Success Metrics

### 9.1 Integration Completeness

**Skill Documentation**:
- 100% of Skills reference sequential-thinking in frontmatter ✅ (already done)
- 100% of Skills document sequential-thinking usage patterns (target)
- pact-prepare-research documents context7 tools (target)
- pact-testing-patterns documents browser automation (conditional)

**Agent Awareness**:
- Agents reference Skills for MCP tool guidance (already true via Skill references)
- Optional: Agents have brief MCP tool awareness section (enhancement)

### 9.2 Quality Metrics

**Documentation Quality**:
- Each MCP tool has clear "when to use" guidance
- Each MCP tool has 2-3 concrete examples
- No duplication of MCP tool guidance across Skills
- Guidance is phase-specific and actionable

**Practical Utility**:
- Developers report using sequential-thinking for complex decisions
- context7 tools reduce time spent searching for docs
- Browser automation tools enable comprehensive E2E testing

### 9.3 Maintenance Metrics

**Sustainability**:
- MCP tool guidance consolidated in Skills (single source of truth per domain)
- Updates to MCP tools require Skill updates only (not agent updates)
- New MCP tools follow established integration pattern

---

## 10. Risk Assessment

### Risk 1: MCP Tools Change or Deprecate

**Impact**: Medium - Documented MCP tools become unavailable or change APIs
**Likelihood**: Low - MCP is standardized protocol
**Mitigation**:
- Document MCP tools in Skills (easier to update than agent prompts)
- Monitor MCP server updates and API changes
- Version MCP tool guidance in Skill metadata

### Risk 2: Over-Reliance on MCP Tools

**Impact**: Low - Agents invoke MCP tools too frequently, causing latency
**Likelihood**: Low - Guidance emphasizes complex decisions only
**Mitigation**:
- Document when NOT to use MCP tools
- Emphasize MCP tools for genuinely complex scenarios
- Monitor MCP tool invocation patterns

### Risk 3: Confusion Between MCP Tools and Skills

**Impact**: Medium - Agents try to invoke MCP tools via Skill tool
**Likelihood**: Medium - Naming overlap, conceptual similarity
**Mitigation**:
- Clear distinction in documentation (Section 1)
- Skills reference MCP tools in frontmatter `allowed-tools`
- Agent guidance emphasizes direct MCP tool invocation pattern

### Risk 4: Incomplete MCP Tool Guidance

**Impact**: Medium - Agents don't know when to use MCP tools effectively
**Likelihood**: Low - Comprehensive usage patterns documented
**Mitigation**:
- Phase 1 provides sequential-thinking examples across all Skills
- Each Skill includes phase-specific examples
- Reference existing pact-architecture-patterns sequential-thinking section as template

---

## 11. Appendices

### Appendix A: MCP Tool Invocation Patterns

**Sequential-Thinking**:
```markdown
mcp__sequential-thinking__sequentialthinking(
  task: "Clear description of the decision or problem to reason through"
)
```

**Context7 Library Lookup**:
```markdown
# Step 1: Resolve library ID
library_id = mcp__context7__resolve-library-id(
  library: "react"
)

# Step 2: Fetch documentation
docs = mcp__context7__get-library-docs(
  library_id: library_id,
  version: "18"  # optional, defaults to latest
)
```

**Playwright Browser Automation** (advanced):
```markdown
# Typically used via test framework integration, not direct invocation
# Requires playwright setup and configuration
# See playwright documentation for detailed usage
```

---

### Appendix B: Skill Update Template

When adding MCP tool guidance to a Skill:

```markdown
## Using MCP Tools with [Skill Domain]

### sequential-thinking

**When to use**:
- [Specific scenario 1 for this domain]
- [Specific scenario 2 for this domain]
- [Specific scenario 3 for this domain]

**Example Prompts**:

**[Scenario 1 Name]**:
> "[Example prompt showing how to frame the decision for sequential-thinking]"

**[Scenario 2 Name]**:
> "[Example prompt showing how to frame the decision for sequential-thinking]"

**Integration Pattern**:
1. Load knowledge from this Skill
2. Use sequential-thinking for complex decision
3. Apply combined knowledge + reasoning to implementation
4. Document decision rationale in architecture/code

### [Other MCP tools if relevant to this domain]

[Similar structure as above]
```

---

### Appendix C: Agent MCP Tool Awareness Template (Optional)

If adding brief MCP tool awareness to agents:

```markdown
# AVAILABLE MCP TOOLS

You have access to Model Context Protocol tools for enhanced capabilities:

**Core Tools** (all phases):
- **sequential-thinking**: Complex reasoning and decision-making
  Use when: Evaluating trade-offs, comparing options, analyzing complex scenarios
  See Skills for detailed usage patterns

**[Phase-Specific Tools]**:
- **[tool-name]**: [One-line description]
  Use when: [Brief trigger]
  See [skill-name] for detailed guidance

**Integration**: Skills provide knowledge; MCP tools provide functionality.
Read relevant Skills first, then invoke MCP tools as needed.
```

---

### Appendix D: Example Skill Update (sequential-thinking)

**Before** (pact-backend-patterns):
```markdown
# PACT Backend Patterns

## Overview
This skill provides backend implementation patterns...

[Rest of skill content]
```

**After** (pact-backend-patterns):
```markdown
# PACT Backend Patterns

## Overview
This skill provides backend implementation patterns...

## Using MCP Tools in Backend Development

### sequential-thinking for Complex Logic

**When to use**:
- Designing multi-step business logic with complex state transitions
- Planning error handling and recovery strategies
- Optimizing database query patterns with multiple constraints
- Architecting background job processing workflows

**Example Prompts**:

**Payment Processing Flow**:
> "I need to implement a payment processing flow with retry logic, refund capability,
> and webhook notifications to external systems. The flow must handle: payment
> authorization, capture, partial refunds, and notification of order systems.
> Let me think through the state machine and error handling systematically..."

**Error Propagation Strategy**:
> "Our microservices architecture needs a consistent error handling strategy.
> Considerations: service-to-service errors, client errors, timeout handling,
> retry logic, circuit breakers, and observability. Let me evaluate different
> error propagation patterns systematically..."

**Integration Pattern**:
1. Read pact-backend-patterns for service layer and error handling knowledge
2. Use sequential-thinking to reason through complex implementation
3. Apply patterns from skill + reasoning to implementation
4. Document decision rationale in code comments and architecture docs

[Rest of skill content]
```

---

## Conclusion

This architecture establishes a clear integration pattern for MCP tools within the PACT framework. By treating MCP tools as functional capabilities (not knowledge) and documenting their usage in Skills (not duplicating across agents), we maintain the "agents orchestrate, Skills provide knowledge" principle while extending PACT with powerful external capabilities.

**Recommended Implementation Order**:
1. **Phase 1**: Document sequential-thinking usage in all 8 Skills (Priority 1, 3-4 hours)
2. **Phase 2**: Integrate context7 tools into pact-prepare-research (Priority 2, 1-2 hours)
3. **Phase 3**: Add browser automation to pact-testing-patterns if E2E guidance added (Priority 3, conditional)
4. **Phase 4**: Optional agent awareness updates (Low priority, 2-3 hours)

**Success Indicators**:
- ✅ MCP tools enhance PACT workflow without adding complexity
- ✅ Skills provide comprehensive MCP tool usage guidance
- ✅ No duplication of MCP tool documentation across components
- ✅ Agents effectively combine Skill knowledge with MCP tool functionality
- ✅ Developers understand when and how to use MCP tools in each phase

This architecture positions the PACT framework to leverage MCP tool ecosystem while maintaining clarity, maintainability, and adherence to established design principles.

---

**Document Status**: 📋 PROPOSAL - Awaiting approval for implementation
**Next Steps**: Review and approve → Implement Phase 1 (sequential-thinking documentation)
