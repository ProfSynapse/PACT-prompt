# MCP Tools Integration: Joint Recommendation

**Date**: 2025-12-05
**Authors**: PACT Preparer & PACT Architect (Joint Resolution)
**Status**: Final Recommendation
**Supersedes**: Conflicting positions in preparation and architecture documents

---

## Executive Summary

After systematic analysis of both the Preparer's and Architect's positions on MCP tool integration, we have identified that **both perspectives are correct** but address **different aspects** of MCP tool guidance. The disagreement stems from conflating two distinct types of knowledge:

1. **Pattern Knowledge** (belongs in Skills): WHEN and WHY to use MCP tools
2. **Workflow Knowledge** (belongs in Agents): HOW to integrate MCP tools into phase-specific workflows

**Joint Recommendation**: Use a **hybrid approach** that leverages the strengths of both Skills and Agents:

- **Skills**: Document MCP tool **applicability** (use cases, scenarios, decision triggers)
- **Agents**: Document MCP tool **integration** (workflow steps, invocation patterns, fallbacks)

This maintains architectural purity while providing comprehensive guidance.

**Interim Implementation**: As of 2025-12-05, a quick fix has been applied to all 6 PACT agents to prevent incorrect invocation of MCP tools through the Skill tool. This temporary solution establishes the correct invocation mechanism (direct function calls) while the full workflow integration guidance (Phase 2) is implemented. See Section 6.2.1 for details.

---

## 1. Understanding the True Disagreement

### 1.1 What Both Positions Agree On

Both the Preparer and Architect agree that:

✅ MCP tools are functional capabilities, not knowledge libraries
✅ MCP tools and Skills serve distinct, complementary purposes
✅ Skills should remain portable and not depend on MCP tool availability
✅ The principle "agents orchestrate, skills provide knowledge" is correct
✅ Duplication of MCP tool guidance should be avoided
✅ Skills reference MCP tools in frontmatter `allowed-tools`

### 1.2 Where They Differ

**Preparer's Concern**:
> "Skills become less portable (tied to MCP availability)"
> "Confuses the clean distinction between knowledge and execution"

**Key Insight**: Preparer sees detailed MCP usage as "execution" (workflow), not "knowledge"

**Architect's Concern**:
> "Agents are orchestrators, not knowledge bases"
> "Reduces duplication across agents"

**Key Insight**: Architect sees MCP usage patterns as "knowledge" (when/why to use), not "execution"

### 1.3 The Resolution

**Both are correct because they're talking about different things**:

| Type | What It Is | Where It Belongs | Example |
|------|-----------|------------------|---------|
| **Pattern Knowledge** | When to use MCP tools, why they're valuable, what problems they solve | **Skills** | "Use sequential-thinking for comparing 3+ technology options with complex trade-offs" |
| **Workflow Knowledge** | How to invoke MCP tools, integration with other tools, step-by-step workflows | **Agents** | "1. Read skill for patterns 2. Invoke `mcp__sequential-thinking(task: '...')` 3. Apply to implementation" |

**Analogy**:
- Skills are like a cookbook explaining WHEN to use a sous-vide machine (knowledge)
- Agents are like a chef knowing HOW to operate the sous-vide during service (workflow)

---

## 2. The Hybrid Solution

### 2.1 Skills: Document MCP Tool Applicability

**What Goes in Skills**:

```markdown
## MCP Tools for [Skill Domain]

### sequential-thinking

**What it provides**: Extended reasoning capability for complex decisions

**When to use**:
- Comparing 3+ technology options with multiple trade-off dimensions
- Evaluating architectural patterns with conflicting requirements
- Analyzing security implications across multiple attack vectors
- Planning complex refactoring with many dependencies

**When NOT to use**:
- Simple binary choices (use A vs use B)
- Decisions with clear best practices (follow the pattern)
- Time-sensitive situations requiring immediate action

**Value proposition**: Transparent, auditable reasoning process that reduces
unpredictable outputs in critical design decisions.

**Integration pattern**: Load this skill for domain knowledge → Use
sequential-thinking for complex reasoning → Apply combined insights to
project-specific implementation.

**See agent guidance for invocation syntax and workflow integration.**
```

**What Does NOT Go in Skills**:
❌ Step-by-step invocation instructions
❌ Specific parameter syntax examples
❌ Workflow integration with other tools
❌ Fallback strategies for tool unavailability

### 2.2 Agents: Document MCP Tool Integration

**What Goes in Agents**:

```markdown
## MCP Tools Available in [Phase] Phase

### sequential-thinking (All Phases)

**Invocation Pattern**:
mcp__sequential-thinking__sequentialthinking(
  task: "Clear description of the decision or problem to reason through"
)

**Integration Workflow**:
1. Identify complex decision requiring structured reasoning
2. Load relevant skill for domain knowledge (e.g., pact-architecture-patterns)
3. Invoke sequential-thinking with specific task description
4. Synthesize reasoning output with skill patterns
5. Document decision rationale in architecture/code

**Fallback Strategy**:
If sequential-thinking is unavailable:
- Use structured decision matrices from skills
- Document manual reasoning process
- Seek peer review for complex decisions

**Example Usage** (specific to this agent):
When choosing between microservices vs modular monolith:
mcp__sequential-thinking__sequentialthinking(
  task: "Evaluate microservices vs modular monolith for mid-size e-commerce
  platform with 5-person team. Requirements: ..."
)
```

**What Does NOT Go in Agents**:
❌ When to use MCP tools (that's in Skills)
❌ Why MCP tools are valuable (that's in Skills)
❌ Use case scenarios (that's in Skills)
❌ Detailed value propositions (that's in Skills)

### 2.3 The Clear Boundary

**Skills Answer**:
- "Should I use this MCP tool for my current situation?" → YES/NO with reasoning
- "What problems does this MCP tool solve?" → Use case catalog
- "What's the value proposition?" → Benefits and limitations

**Agents Answer**:
- "How do I invoke this MCP tool?" → Syntax and parameters
- "How does this MCP tool fit into my workflow?" → Step-by-step integration
- "What if this MCP tool fails?" → Fallback strategies

**Visual Boundary**:
```
User asks: "Should I use sequential-thinking here?"
    ↓
Read Skill → Decision criteria → YES/NO
    ↓
If YES, ask: "How do I use it in my workflow?"
    ↓
Check Agent → Invocation pattern → Execute
```

---

## 3. Implementation Guidelines

### 3.1 Skill Update Pattern

**Template for Skills**:

```markdown
## MCP Tools for [Domain]

### [MCP Tool Name]

**Purpose**: [What this MCP tool provides]

**When to use**:
- [Scenario 1 specific to this domain]
- [Scenario 2 specific to this domain]
- [Scenario 3 specific to this domain]

**When NOT to use**:
- [Anti-pattern 1]
- [Anti-pattern 2]

**Value for [Domain]**: [Why this MCP tool enhances this domain's work]

**Integration approach**: [High-level pattern of combining skill + MCP tool]

**See agent workflow documentation for invocation syntax.**
```

**Key Characteristics**:
- Focus on WHEN and WHY
- Domain-specific use cases
- No invocation syntax
- Reference to agent for HOW

### 3.2 Agent Update Pattern

**Template for Agents**:

```markdown
## MCP Tools in [Phase] Phase

### [MCP Tool Name]

**Availability**: [Always available / Conditional on setup]

**Invocation Pattern**:
[Exact syntax with parameter examples]

**Workflow Integration**:
1. [Step 1: When to consider using this tool]
2. [Step 2: Load relevant skills if needed]
3. [Step 3: Invoke MCP tool with specific parameters]
4. [Step 4: Process and apply output]

**Fallback if Unavailable**:
- [Alternative approach 1]
- [Alternative approach 2]

**Phase-Specific Example**:
[Concrete example relevant to this agent's phase]

**See [skill-name] for use case guidance and decision criteria.**
```

**Key Characteristics**:
- Focus on HOW
- Invocation syntax included
- Workflow steps explicit
- Fallback strategies clear

### 3.3 Documentation Checklist

**For Each MCP Tool Integration**:

Skills Documentation:
- [ ] What the MCP tool provides (capability description)
- [ ] When to use (3+ domain-specific scenarios)
- [ ] When NOT to use (anti-patterns)
- [ ] Value proposition for this domain
- [ ] High-level integration pattern
- [ ] Reference to agent for syntax

Agent Documentation:
- [ ] Availability status (always/conditional)
- [ ] Invocation pattern with syntax
- [ ] Workflow integration steps
- [ ] Fallback strategies
- [ ] Phase-specific example
- [ ] Reference to skill for decision criteria

Cross-Check:
- [ ] No duplication between skill and agent
- [ ] Clear handoff: Skill → "when/why" → Agent → "how"
- [ ] Both documents reference each other
- [ ] Complete coverage (all questions answered somewhere)

---

## 4. Resolution of Original Positions

### 4.1 Preparer's Concerns: ADDRESSED

**Concern 1**: "Skills become less portable (tied to MCP availability)"

**Resolution**: Skills document WHEN to use MCP tools (portable knowledge about use cases), but don't include invocation syntax (which would tie them to availability). If MCP tools are unavailable, skills still provide value by explaining scenarios where extended reasoning is beneficial.

**Concern 2**: "Confuses the clean distinction between knowledge and execution"

**Resolution**: We now clearly distinguish:
- **Knowledge** = Use case patterns, decision criteria (Skills)
- **Execution** = Invocation syntax, workflow steps (Agents)

**Concern 3**: Skills should not provide "step-by-step MCP invocation"

**Resolution**: AGREED. Step-by-step invocation goes in Agents, not Skills.

### 4.2 Architect's Concerns: ADDRESSED

**Concern 1**: "Agents are orchestrators, not knowledge bases"

**Resolution**: Agents remain orchestrators. They contain workflow knowledge (how to orchestrate tools), not pattern knowledge (when to use patterns). Workflow knowledge is a form of orchestration, not knowledge in the "pattern library" sense.

**Concern 2**: "Reduces duplication across agents"

**Resolution**: PARTIALLY TRUE. Use case patterns are centralized in Skills (no duplication). Workflow integration may vary by agent because each phase has different workflows. We accept this as necessary variation, not duplication.

**Concern 3**: "Skills document which MCP tools are useful for their domain"

**Resolution**: AGREED. Skills document WHICH tools are relevant and WHEN to use them.

### 4.3 Synthesized Position

**What We Now Agree On**:

1. **Skills contain pattern knowledge**: Use cases, scenarios, decision criteria
2. **Agents contain workflow knowledge**: Invocation syntax, integration steps, fallbacks
3. **Both are necessary**: You can't effectively use MCP tools with only one or the other
4. **Clear boundary exists**: WHEN/WHY (Skills) vs HOW (Agents)
5. **Cross-references required**: Skills point to Agents for syntax; Agents point to Skills for use cases
6. **Minimal duplication**: Each type of guidance appears in exactly one place
7. **Architectural purity maintained**: Skills remain portable knowledge; Agents remain orchestrators

---

## 5. Practical Examples

### 5.1 Example 1: sequential-thinking in pact-architecture-patterns

**In Skill (pact-architecture-patterns/SKILL.md)**:

```markdown
## MCP Tools for Architectural Decisions

### sequential-thinking

**Purpose**: Extended reasoning capability for complex architectural decisions

**When to use**:
- Choosing between 3+ viable architectural patterns (microservices, modular monolith, serverless)
- Evaluating trade-offs with multiple competing constraints (scalability, cost, team expertise)
- Designing component boundaries for systems with complex domain logic
- Resolving conflicting non-functional requirements (security vs performance vs maintainability)

**When NOT to use**:
- Well-established patterns with clear best practices (use the standard pattern)
- Time-sensitive architectural spikes (defer reasoning to implementation phase)
- Simple binary choices with obvious answers (REST vs GraphQL when all requirements favor one)

**Value for architecture phase**: Transparent reasoning process creates auditable
architectural decision records (ADRs). Reduces risk of overlooking critical trade-offs.

**Integration approach**: Load architecture patterns from this skill → Identify
decision requiring extended reasoning → Use sequential-thinking to evaluate
options → Document decision rationale in architecture specification.

**See pact-architect agent for invocation syntax and workflow integration.**
```

**In Agent (pact-architect.md)**:

```markdown
## MCP Tools in Architect Phase

### sequential-thinking

**Availability**: Always available (core MCP tool)

**Invocation Pattern**:
mcp__sequential-thinking__sequentialthinking(
  task: "Evaluate [options] for [context]. Requirements: [list]. Let me think
  through the trade-offs systematically..."
)

**Workflow Integration**:
1. Identify architectural decision requiring systematic reasoning
2. Read pact-architecture-patterns for relevant patterns and principles
3. Frame decision with clear context, options, and requirements
4. Invoke sequential-thinking with structured task description
5. Review reasoning output for completeness and accuracy
6. Synthesize decision with architectural patterns from skill
7. Document rationale in architecture specification markdown

**Fallback if Unavailable**:
- Use decision matrix template from pact-architecture-patterns
- Document manual reasoning in structured format
- Schedule peer review for complex decisions
- Create ADR (Architectural Decision Record) with pros/cons analysis

**Phase-Specific Example**:
When designing authentication strategy for microservices:

mcp__sequential-thinking__sequentialthinking(
  task: "Evaluate session-based, JWT, and OAuth 2.0 authentication for
  microservices architecture. Requirements: mobile app support, third-party
  integrations, 5-year lifespan, team has React + Node.js expertise.
  Constraints: Budget-conscious startup, security-critical (healthcare data).
  Let me analyze each option systematically..."
)

**See pact-architecture-patterns for decision criteria and use case guidance.**
```

### 5.2 Example 2: context7 in pact-prepare-research

**In Skill (pact-prepare-research/SKILL.md)**:

```markdown
## MCP Tools for Research

### context7 (Library Documentation Lookup)

**Purpose**: Fetch up-to-date, version-specific documentation from official sources

**When to use**:
- Researching popular libraries with rapidly evolving APIs (React, Next.js, FastAPI)
- Verifying version-specific features before documenting technology recommendations
- Getting official code examples for integration planning
- Confirming breaking changes between versions during migration research

**When NOT to use**:
- Internal/proprietary libraries (not in context7 index)
- Very new libraries (may not be indexed yet)
- Broader ecosystem research (use WebSearch for comparisons and discussions)
- Historical context or migration guides (WebSearch better for community insights)

**Value for preparation phase**: Ensures documentation is based on current,
authoritative sources. Reduces risk of outdated API information in research outputs.

**Integration approach**: Identify libraries to research → Use context7 for
official documentation → Complement with WebSearch for community insights →
Synthesize into preparation markdown.

**See pact-preparer agent for invocation workflow.**
```

**In Agent (pact-preparer.md)**:

```markdown
## MCP Tools in Prepare Phase

### context7 Library Documentation

**Availability**: Conditional (requires context7 MCP server setup)

**Invocation Pattern**:
# Step 1: Resolve library identifier
library_id = mcp__context7__resolve-library-id(library: "react")

# Step 2: Fetch documentation
docs = mcp__context7__get-library-docs(
  library_id: library_id,
  version: "18"  # optional, defaults to latest
)

**Workflow Integration**:
1. Identify libraries/frameworks from project requirements
2. For each library, check if context7 is appropriate (see skill guidance)
3. Resolve library ID using context7
4. Fetch documentation for specific version if known, or latest
5. Extract relevant API information, examples, and best practices
6. Complement context7 docs with WebSearch for:
   - Community comparisons and discussions
   - Real-world usage patterns
   - Troubleshooting and gotchas
7. Synthesize official docs + community insights into preparation markdown

**Fallback if Unavailable**:
- Use WebSearch with query: "[library] official documentation [version]"
- Visit library's official website directly
- Check GitHub repository README and docs folder
- Use existing knowledge base if documentation is well-known

**Phase-Specific Example**:
When researching React for new dashboard project:

1. Resolve: `mcp__context7__resolve-library-id(library: "react")`
   Returns: "react-18.2.0"

2. Fetch: `mcp__context7__get-library-docs(library_id: "react-18.2.0")`
   Returns: Official React 18 documentation, hooks API, concurrent features

3. Synthesize: Combine official docs with WebSearch for "React 18 dashboard
   best practices" to get complete picture

**See pact-prepare-research for use case guidance and decision criteria.**
```

---

## 6. Implementation Roadmap

### 6.1 Phase 1: Update All Skills (Priority 1)

**Objective**: Add MCP tool applicability guidance to all 8 skills

**Tasks**:
1. Add "MCP Tools for [Domain]" section to each skill
2. Document WHEN to use each relevant MCP tool
3. Document WHEN NOT to use (anti-patterns)
4. Provide domain-specific value proposition
5. Reference agent for invocation syntax

**Skills to Update**:
- [ ] pact-prepare-research (sequential-thinking + context7)
- [ ] pact-architecture-patterns (sequential-thinking) - enhance existing
- [ ] pact-backend-patterns (sequential-thinking)
- [ ] pact-frontend-patterns (sequential-thinking)
- [ ] pact-database-patterns (sequential-thinking)
- [ ] pact-testing-patterns (sequential-thinking + playwright/puppeteer)
- [ ] pact-security-patterns (sequential-thinking)
- [ ] pact-api-design (sequential-thinking)

**Success Criteria**:
- [ ] Each skill has MCP tool section following template
- [ ] Use cases are domain-specific, not generic
- [ ] No invocation syntax in skills
- [ ] Cross-references to agents present

**Estimated Effort**: 4-6 hours (30-45 minutes per skill)

---

### 6.2 Phase 2: Update All Agents (Priority 2)

**Objective**: Add MCP tool workflow integration to all agents

**Tasks**:
1. Add "MCP Tools in [Phase] Phase" section to each agent
2. Document HOW to invoke each relevant MCP tool
3. Provide workflow integration steps
4. Include fallback strategies
5. Reference skills for use case guidance

**Agents to Update**:
- [ ] pact-preparer (sequential-thinking + context7)
- [ ] pact-architect (sequential-thinking)
- [ ] pact-backend-coder (sequential-thinking)
- [ ] pact-frontend-coder (sequential-thinking)
- [ ] pact-database-engineer (sequential-thinking)
- [ ] pact-test-engineer (sequential-thinking + playwright/puppeteer)

**Success Criteria**:
- [ ] Each agent has MCP tool section following template
- [ ] Invocation syntax is clear and accurate
- [ ] Workflow steps are phase-specific
- [ ] Fallback strategies provided
- [ ] Cross-references to skills present

**Estimated Effort**: 3-4 hours (30-40 minutes per agent)

---

### 6.3 Phase 3: Validation and Refinement

**Objective**: Ensure hybrid approach works in practice

**Tasks**:
1. Test a skill + agent pairing for completeness
2. Verify no duplication between skill and agent
3. Check cross-references work correctly
4. Validate use case → syntax → workflow path
5. Refine templates based on findings

**Test Cases**:
- [ ] pact-architecture-patterns + pact-architect (sequential-thinking)
- [ ] pact-prepare-research + pact-preparer (context7)
- [ ] pact-testing-patterns + pact-test-engineer (playwright)

**Success Criteria**:
- [ ] User can determine WHEN to use MCP tool from skill alone
- [ ] User can determine HOW to use MCP tool from agent alone
- [ ] No confusion about where to find specific information
- [ ] Cross-references create seamless navigation

**Estimated Effort**: 2-3 hours

---

## 7. Architectural Principles

### 7.1 Separation of Concerns (Refined)

**Principle**: Different types of knowledge belong in different places

| Knowledge Type | Definition | Location | Rationale |
|---------------|------------|----------|-----------|
| **Pattern Knowledge** | Use cases, scenarios, decision criteria | **Skills** | Portable, domain-specific, reusable across projects |
| **Workflow Knowledge** | Integration steps, invocation syntax, fallbacks | **Agents** | Phase-specific, orchestration logic, context-dependent |
| **Reference Knowledge** | Detailed patterns, checklists, templates | **Skill References** | On-demand, deep dives, optional reading |

**Corollary**: Workflow knowledge is NOT the same as execution. Agents document workflows (which is orchestration), they don't execute arbitrary code (which would violate separation).

### 7.2 Single Source of Truth (Maintained)

**Principle**: Each piece of information appears in exactly one canonical location

**Application**:
- Use case scenarios: ONE skill (domain-appropriate)
- Invocation syntax: ONE agent (phase-appropriate)
- Decision criteria: ONE skill (domain-appropriate)
- Workflow steps: ONE agent (phase-appropriate)

**Cross-References**: When information in one location depends on information in another, use explicit cross-references rather than duplication.

### 7.3 Portability (Maintained for Skills)

**Principle**: Skills remain valuable even if MCP tools are unavailable

**How We Achieve This**:
- Skills document WHEN to use extended reasoning (concept remains valuable)
- Skills don't include invocation syntax (which ties to availability)
- Skills provide decision criteria usable manually if needed
- Skills point to agents for optional MCP tool enhancement

**Example**: If sequential-thinking is unavailable, skill still explains when complex reasoning is needed. User can apply manual structured thinking instead.

### 7.4 Discoverability (Enhanced)

**Principle**: Users can find the right information when they need it

**Discovery Paths**:

**Path 1: Start with Skill** (common)
```
User has question: "Should I use this MCP tool here?"
  → Read Skill → Find decision criteria → Make decision
  → If YES: Skill points to Agent for syntax
  → Read Agent → Get invocation pattern → Execute
```

**Path 2: Start with Agent** (less common)
```
User knows they need MCP tool: "How do I use this?"
  → Read Agent → Find invocation syntax → Execute
  → Agent points to Skill for use case validation
  → Read Skill → Verify this is appropriate scenario
```

**Path 3: Exploration** (learning)
```
User exploring PACT framework: "What MCP tools exist?"
  → Read Skills → Discover tools relevant to each domain
  → Skills point to Agents for each tool
  → Read Agents → Understand how to use in workflows
```

---

## 8. FAQ: Resolving Remaining Ambiguities

### Q1: What if a use case could go in either Skills or Agents?

**A**: Apply this decision tree:

1. Is it about WHEN/WHY to use the tool? → **Skill**
2. Is it about HOW/WHERE in workflow? → **Agent**
3. Is it generic across phases? → **Skill** (reusable knowledge)
4. Is it phase-specific? → **Agent** (workflow context)

**Example**: "Use sequential-thinking for complex decisions" → Skill (generic, WHEN)
**Example**: "After reading architecture patterns, invoke sequential-thinking before documenting decision" → Agent (workflow, WHERE)

### Q2: Can Agents reference multiple Skills for one MCP tool?

**A**: YES. Agents orchestrate multiple knowledge sources.

**Example**: pact-architect agent can say:
> "For architectural decisions, use sequential-thinking (see pact-architecture-patterns for use cases). For security-critical decisions, also consult pact-security-patterns for threat modeling guidance."

### Q3: Can Skills reference Agents?

**A**: YES, but only to point to invocation syntax.

**Pattern**: "See [agent-name] for invocation syntax and workflow integration."

**Don't**: Include agent-specific workflow details in Skills.

### Q4: What about MCP tool examples in Skills?

**A**: Conceptual examples of WHEN to use are OK. Invocation syntax examples are NOT.

**OK in Skill**:
> "Use sequential-thinking when comparing React vs Vue vs Svelte with requirements for TypeScript, team expertise, ecosystem maturity, and performance."

**NOT OK in Skill**:
> "Invoke `mcp__sequential-thinking(task: 'Compare React vs Vue...')` to get structured reasoning."

### Q5: How much cross-referencing is too much?

**A**: Each document should have ONE cross-reference to its complement:

**In Skill**: One sentence pointing to agent for syntax (end of MCP tool section)
**In Agent**: One sentence pointing to skill for use cases (end of MCP tool section)

**Don't**: Create circular references within content.

---

## 9. Success Metrics

### 9.1 Architectural Integrity

- [ ] Skills contain ZERO invocation syntax for MCP tools
- [ ] Agents contain ZERO use case scenarios (only workflow examples)
- [ ] Each MCP tool has complete coverage: use cases (skill) + syntax (agent)
- [ ] Cross-references are bidirectional and complete
- [ ] No duplication of MCP tool information between skill and agent

### 9.2 User Experience

- [ ] User can answer "Should I use this MCP tool?" from skill alone
- [ ] User can answer "How do I use this MCP tool?" from agent alone
- [ ] Navigation between skill and agent is seamless via cross-references
- [ ] Fallback strategies allow graceful degradation if MCP tools unavailable
- [ ] Documentation feels cohesive, not fragmented

### 9.3 Maintainability

- [ ] MCP tool use cases updated in ONE place (skill)
- [ ] MCP tool syntax updated in ONE place (agent)
- [ ] New MCP tools follow established template pattern
- [ ] Changes to MCP tools require minimal updates (single source of truth)

---

## 10. Conclusion

### 10.1 The Unified Position

**We jointly recommend a hybrid approach** that:

1. **Places pattern knowledge in Skills**: Use cases, scenarios, decision criteria, value propositions
2. **Places workflow knowledge in Agents**: Invocation syntax, integration steps, fallback strategies
3. **Establishes clear boundary**: WHEN/WHY (Skills) vs HOW (Agents)
4. **Requires bidirectional cross-references**: Skills → Agents for syntax; Agents → Skills for use cases
5. **Maintains architectural principles**: Skills remain portable knowledge; Agents remain orchestrators
6. **Eliminates duplication**: Each type of guidance appears exactly once
7. **Enhances discoverability**: Clear paths from question to answer

### 10.2 Why This Resolves the Disagreement

**Preparer's concerns are met**:
- ✅ Skills don't include invocation workflows (execution remains in agents)
- ✅ Skills remain portable (use cases valuable even if MCP unavailable)
- ✅ Clean distinction maintained (pattern knowledge vs workflow knowledge)

**Architect's concerns are met**:
- ✅ Skills document MCP tool knowledge (use cases, scenarios)
- ✅ Agents aren't knowledge bases (workflow is orchestration, not patterns)
- ✅ Duplication reduced (use cases centralized in skills)

**Both perspectives enhanced**:
- ✅ Clear boundary prevents future confusion (WHEN/WHY vs HOW)
- ✅ Complete coverage ensured (every question answered somewhere)
- ✅ Discoverability improved (cross-references create navigation)

### 10.3 Implementation Consensus

We jointly endorse the implementation roadmap:

**Phase 1**: Update all Skills with MCP tool applicability guidance (4-6 hours)
**Phase 2**: Update all Agents with MCP tool workflow integration (3-4 hours)
**Phase 3**: Validation and refinement (2-3 hours)

**Total effort**: 9-13 hours for complete MCP tools integration

### 10.4 Next Steps

**Immediate**:
1. Approve this joint recommendation
2. Begin Phase 1: Skills updates
3. Use provided templates for consistency

**Follow-up**:
1. Test hybrid approach with one skill+agent pairing
2. Refine templates based on real usage
3. Document lessons learned for future integrations

---

## Appendix: Side-by-Side Comparison

### Example: sequential-thinking in Architecture Phase

| Aspect | Preparer's Original Position | Architect's Original Position | Joint Recommendation |
|--------|------------------------------|-------------------------------|---------------------|
| **Use Cases** | Agent prompt | Skill body | **Skill body** ✅ |
| **Invocation Syntax** | Agent prompt | Skill body | **Agent prompt** ✅ |
| **When to Use** | Agent prompt | Skill body | **Skill body** ✅ |
| **Workflow Steps** | Agent prompt | Skill body (rejected) | **Agent prompt** ✅ |
| **Value Proposition** | Agent prompt | Skill body | **Skill body** ✅ |
| **Fallback Strategy** | Agent prompt | Not addressed | **Agent prompt** ✅ |

**Result**: Hybrid approach takes best elements from both positions.

---

---

## 11. Maintenance Strategy

### 11.1 Handling MCP Tool Version Changes

**Monitoring**:
- Quarterly review of MCP tools used in PACT (see official repos)
- Subscribe to MCP tool release notes and changelogs
- Test MCP tool integrations with each Claude Code update

**When MCP Tool API Changes**:

**Impact on Skills**: LOW
- Use cases remain conceptually valid (update only if capability changes)
- Anti-patterns remain relevant
- Value propositions unchanged unless feature additions/removals

**Impact on Agents**: HIGH
- Invocation syntax must be updated immediately
- Workflow steps may need revision
- Fallback strategies may change
- Examples require updating

**Update Checklist**:
- [ ] Review MCP tool changelog for breaking changes
- [ ] Update agent invocation syntax sections
- [ ] Test updated workflows with real MCP tool
- [ ] Update skill use cases only if capabilities changed
- [ ] Validate cross-references still accurate
- [ ] Document migration notes for users with old syntax

**Versioning Strategy**: Include MCP tool version in agent documentation

**Example**:
```markdown
### sequential-thinking (v1.2.0)

**Invocation Pattern** (updated 2025-12-05):
mcp__sequential-thinking__sequentialthinking(
  task: "Clear description..."  # Changed from 'prompt' in v1.1.0
)
```

---

### 11.2 Deprecating MCP Tools

**When to deprecate MCP tool guidance**:
- MCP tool is officially deprecated by maintainers
- MCP tool becomes unmaintained for 12+ months
- Better alternative MCP tool becomes standard
- Claude Code deprecates MCP tool integration

**Deprecation Process**:

**Phase 1: Mark as Deprecated** (immediately upon deprecation announcement)
- Add `[DEPRECATED]` marker to skill section
- Add deprecation notice to agent section
- Upgrade fallback strategy to primary recommendation
- Document migration path to alternative

**Example**:
```markdown
### sequential-thinking [DEPRECATED as of 2026-01-15]

**Deprecation Notice**: This MCP tool has been replaced by `mcp__reasoning-engine__think`.
See migration guide below.

**When to use** (legacy projects): [existing guidance]

**Migration to reasoning-engine**:
- Old: `mcp__sequential-thinking__sequentialthinking(task: "...")`
- New: `mcp__reasoning-engine__think(prompt: "...", strategy: "sequential")`
[detailed migration steps]
```

**Phase 2: Remove from Active Guidance** (6 months after deprecation)
- Move deprecated MCP tool sections to "Legacy Tools" appendix
- Update cross-references to point to replacement tool
- Archive old examples but keep accessible for legacy projects

**Phase 3: Full Removal** (12 months after deprecation)
- Remove from skills entirely
- Remove from agents entirely
- Keep deprecation notice in changelog

---

## 12. MCP Tool Reference Index

Create `/Users/mj/Sites/collab/PACT-prompt/docs/mcp-tools-reference.md`:

### sequential-thinking

**What it does**: Extended reasoning capability for complex decisions

**When to use guidance** (Skills):
- pact-architecture-patterns (architectural decisions)
- pact-prepare-research (technology comparisons)
- pact-backend-patterns (backend architecture choices)
- pact-frontend-patterns (frontend framework selection)
- pact-database-patterns (database design decisions)
- pact-testing-patterns (test strategy planning)
- pact-security-patterns (threat modeling and security architecture)
- pact-api-design (API design decisions)

**How to use guidance** (Agents):
- pact-preparer (research phase reasoning)
- pact-architect (design phase reasoning)
- pact-backend-coder (implementation reasoning)
- pact-frontend-coder (implementation reasoning)
- pact-database-engineer (data modeling reasoning)
- pact-test-engineer (test planning reasoning)

### context7

**What it does**: Fetch up-to-date library documentation

**When to use guidance** (Skills):
- pact-prepare-research (library documentation research)

**How to use guidance** (Agents):
- pact-preparer (research workflow integration)
- pact-backend-coder (optional: just-in-time API reference)
- pact-frontend-coder (optional: just-in-time API reference)

---

## 13. Enhanced FAQ

### Q6: What about "integration pattern" examples that span both Skills and Agents?

**A**: Split the example across both documents with cross-references.

**In Skill** (conceptual pattern):
> **Integration approach**: Load architecture patterns from this skill → Identify
> decision requiring extended reasoning → Use sequential-thinking to evaluate
> options → Document decision rationale in architecture specification.
>
> See pact-architect for specific invocation syntax.

**In Agent** (concrete workflow):
> **Integration Workflow**:
> 1. Identify architectural decision requiring systematic reasoning
> 2. Read pact-architecture-patterns for relevant patterns (from skill guidance above)
> 3. Invoke sequential-thinking with structured task description
> [... rest of workflow with syntax]

This maintains separation while providing complete end-to-end guidance.

---

### Q7: What if a MCP tool is generic but has phase-specific patterns?

When an MCP tool is universally applicable but used differently in each phase:

**In Skills** (multiple skills may reference it):
- Each skill documents domain-specific use cases
- Example: pact-architecture-patterns shows architectural decision use cases
- Example: pact-testing-patterns shows test strategy use cases

**In Agents** (each agent may have different invocation patterns):
- Each agent documents phase-specific workflow integration
- Example: pact-preparer shows research-phase task framing
- Example: pact-architect shows design-phase task framing

**Duplication vs Variation**:
- ✅ **Variation is OK**: Different use cases in different skills (domain-specific)
- ✅ **Variation is OK**: Different workflow integrations in different agents (phase-specific)
- ❌ **Duplication is NOT OK**: Same use case copy-pasted across multiple skills

**Test**: If use cases are truly domain-specific, they should differ in meaningful ways.

---

## 14. Enhanced Implementation Roadmap

### 6.1 Phase 1: Update All Skills (Priority 1)

**Objective**: Add MCP tool applicability guidance to all 8 skills

**Tasks**:
1. Add "MCP Tools for [Domain]" section to each skill
2. Document WHEN to use each relevant MCP tool
3. Document WHEN NOT to use (anti-patterns)
4. Provide domain-specific value proposition
5. Reference agent for invocation syntax
6. Create phase-specific examples from real PACT project scenarios

**Skills to Update**:
- [ ] pact-prepare-research (sequential-thinking + context7)
- [ ] pact-architecture-patterns (sequential-thinking) - enhance existing
- [ ] pact-backend-patterns (sequential-thinking)
- [ ] pact-frontend-patterns (sequential-thinking)
- [ ] pact-database-patterns (sequential-thinking)
- [ ] pact-testing-patterns (sequential-thinking + playwright/puppeteer)
- [ ] pact-security-patterns (sequential-thinking)
- [ ] pact-api-design (sequential-thinking)

**Success Criteria**:
- [ ] Each skill has MCP tool section following template
- [ ] Use cases are domain-specific, not generic
- [ ] Each use case is specific to the domain (not copy-paste across skills)
- [ ] At least one use case is unique to this skill's domain
- [ ] Anti-patterns reference domain-specific misuses
- [ ] No invocation syntax in skills
- [ ] Cross-references to agents present

**Portability Validation**:
- [ ] Use cases make sense without any MCP tool available
- [ ] Value proposition explains conceptual benefit, not just tool feature
- [ ] Anti-patterns are tool-agnostic principles
- [ ] User could manually implement the pattern described
- [ ] No dependency on specific MCP tool behavior or output format

**Estimated Effort**: 4-6 hours (30-45 minutes per skill)

---

### 6.2 Phase 2: Update All Agents (Priority 2)

**Objective**: Add MCP tool workflow integration to all agents

**INTERIM IMPLEMENTATION STATUS**: A quick fix has been applied to all agents as of 2025-12-05 to resolve an immediate issue where agents were incorrectly attempting to invoke MCP tools through the Skill tool. See Section 6.2.1 below for details. This interim fix establishes the foundation for the full Phase 2 implementation.

**Tasks**:
1. Add "MCP Tools in [Phase] Phase" section to each agent
2. Document HOW to invoke each relevant MCP tool
3. Provide workflow integration steps
4. Include fallback strategies
5. Reference skills for use case guidance
6. Ensure examples demonstrate integration with other phase tools
7. Validate examples would actually occur in that phase's workflow

**Agents to Update**:
- [ ] pact-preparer (sequential-thinking + context7)
- [ ] pact-architect (sequential-thinking)
- [ ] pact-backend-coder (sequential-thinking)
- [ ] pact-frontend-coder (sequential-thinking)
- [ ] pact-database-engineer (sequential-thinking)
- [ ] pact-test-engineer (sequential-thinking + playwright/puppeteer)

**Success Criteria**:
- [ ] Each agent has MCP tool section following template
- [ ] Invocation syntax is clear and accurate
- [ ] Workflow steps are phase-specific
- [ ] Fallback strategies provided and meet quality requirements
- [ ] Cross-references to skills present

**Fallback Strategy Requirements**:

A complete fallback strategy must provide:

1. **Equivalent Capability**: How to achieve same outcome without MCP tool
2. **Quality Trade-off**: What's lost (speed, accuracy, automation) vs gained (availability, control)
3. **Step-by-Step Alternative**: Concrete steps, not just "use WebSearch instead"
4. **Skill Reference**: Point to skill for manual decision frameworks if applicable

**Example - Adequate Fallback**:
```markdown
**Fallback if sequential-thinking Unavailable**:

**Option 1: Manual Decision Matrix** (Recommended)
1. Read pact-architecture-patterns for decision matrix template
2. List all options as columns (React, Vue, Svelte)
3. List all requirements as rows (TypeScript, team expertise, ecosystem)
4. Score each option 1-5 for each requirement
5. Weight requirements by importance
6. Calculate weighted scores and document reasoning

**Trade-off**: More time-consuming (15-20 min vs 2 min), but ensures systematic analysis.

**Option 2: Peer Review Discussion**
1. Document options and requirements in architecture draft
2. Schedule 30-min review with technical stakeholder
3. Discuss trade-offs verbally with note-taking
4. Document consensus decision in ADR format

**Trade-off**: Requires human availability, but adds diverse perspectives.
```

**Estimated Effort**: 3-4 hours (30-40 minutes per agent)

---

#### 6.2.1 Interim Implementation: Quick Fix Applied (2025-12-05)

**Problem Addressed**: Agents were attempting to invoke MCP tools through the Skill tool, which is incorrect. The Skill tool is for loading knowledge libraries from `~/.claude/skills/`, not for calling MCP tools.

**Quick Fix Applied**: Added the following clarifying section to all 6 PACT agent prompts:

```markdown
# MCP TOOL USAGE

MCP tools (like `mcp__sequential-thinking__sequentialthinking`, `mcp__context7__*`) are invoked
**directly as function calls**, NOT through the Skill tool.

- **Skill tool**: For knowledge libraries in `~/.claude/skills/` (e.g., `pact-backend-patterns`)
- **MCP tools**: Call directly as functions (e.g., `mcp__sequential-thinking__sequentialthinking(...)`)

If a skill mentions using an MCP tool, invoke that tool directly—do not use the Skill tool.
```

**Agents Updated**:
- ✅ pact-preparer.md
- ✅ pact-architect.md
- ✅ pact-backend-coder.md
- ✅ pact-frontend-coder.md
- ✅ pact-database-engineer.md
- ✅ pact-test-engineer.md

**Status**: **TEMPORARY SOLUTION** - This quick fix prevents incorrect invocation patterns but does not provide the comprehensive MCP tool guidance described in this recommendation.

**Relationship to Phase 2**: This interim implementation provides immediate clarity on HOW NOT to invoke MCP tools (not through Skill tool). The full Phase 2 implementation will **build upon** this foundation by adding comprehensive guidance on HOW TO invoke MCP tools correctly, including:

- Detailed invocation syntax with parameters
- Workflow integration steps specific to each phase
- Fallback strategies when MCP tools are unavailable
- Phase-specific examples demonstrating realistic usage
- Cross-references to skills for use case guidance

**Next Steps**: The quick fix should **remain in place** during Phase 2 implementation. As comprehensive MCP tool sections are added to each agent (following the template in Section 3.2), the quick fix section can be:

1. **Enhanced** with a reference to the detailed MCP tool section: "See 'MCP Tools in [Phase] Phase' section below for complete usage guidance"
2. **Retained** as a quick reference reminder, even after full documentation is added
3. **Eventually replaced** if the comprehensive documentation makes the distinction sufficiently clear

**Recommendation**: Retain the quick fix as a prominent reminder even after Phase 2 completion. It serves as a valuable quick-reference guard against the common mistake of conflating Skills with MCP tools.

**Impact on Implementation Timeline**: This interim fix does NOT reduce Phase 2 effort. The quick fix addresses only invocation mechanism (Skills vs direct calls), not the comprehensive workflow integration, syntax documentation, and fallback strategies that Phase 2 requires.

---

### 6.3 Phase 3: Validation and Refinement (REVISED)

**Objective**: Ensure hybrid approach works in practice

**Tasks**:
1. Test a skill + agent pairing for completeness (30 min per pairing, 1.5 hours total)
2. Verify no duplication between skill and agent (30 min per pairing, 1.5 hours total)
3. Check cross-references work correctly (15 min per pairing, 45 min total)
4. Validate use case → syntax → workflow path (30 min per pairing, 1.5 hours total)
5. **User journey testing** (see below)
6. **Identify template improvements from findings (1 hour)**
7. **Update templates and re-test one pairing (1 hour)**
8. **Document lessons learned for future MCP integrations (30 min)**

**Test Cases**:
- [ ] pact-architecture-patterns + pact-architect (sequential-thinking)
- [ ] pact-prepare-research + pact-preparer (context7)
- [ ] pact-testing-patterns + pact-test-engineer (playwright)

**User Journey Testing**:

**Persona 1: New PACT User** (unfamiliar with MCP tools)
- Journey: "What MCP tools exist and should I use them?"
- Start: Browse skills directory
- Expected: Discover MCP tools via skill sections
- Validation: Can they understand WHEN to use without reading agents?

**Persona 2: Experienced Developer** (knows MCP tools, new to PACT)
- Journey: "How do I integrate sequential-thinking into PACT workflow?"
- Start: Read agent prompt
- Expected: Find invocation syntax and workflow integration
- Validation: Can they integrate tool without reading skills?

**Persona 3: PACT Practitioner** (using PACT, needs quick reference)
- Journey: "Should I use sequential-thinking for this decision?"
- Start: Consult skill during work
- Expected: Quickly determine yes/no from use cases
- Validation: Decision made in <2 minutes without agent reference

**Success Criteria**:
- [ ] User can determine WHEN to use MCP tool from skill alone
- [ ] User can determine HOW to use MCP tool from agent alone
- [ ] All three personas can complete journeys without confusion
- [ ] Cross-references feel helpful, not obstructive
- [ ] No circular navigation (bouncing between skill and agent repeatedly)
- [ ] Each document feels complete for its purpose
- [ ] No confusion about where to find specific information
- [ ] Cross-references create seamless navigation

**Estimated Effort**: 4-6 hours (revised from 2-3 hours)

**REVISED TOTAL EFFORT**: 11-16 hours (vs original 9-13 hours)

---

## 15. Clarification: Workflow Knowledge Is Not Execution

### Why "Workflow Knowledge" Isn't "Execution"

**Common Misconception**: Workflow knowledge violates the "agents orchestrate, don't execute" principle.

**Clarification**:
- **Workflow knowledge** = Instructions for orchestrating tools (legitimate agent content)
- **Execution** = Running arbitrary code or scripts (not agent responsibility)

**Example**:
✅ **Workflow knowledge** (OK in agents): "Step 1: Read skill. Step 2: Invoke mcp__tool(). Step 3: Apply output"
❌ **Execution** (NOT OK in agents): "Run this Python script: [code that executes independently]"

Agents document workflows because orchestration IS their purpose. They don't execute code, they orchestrate tool usage.

---

## 16. Review History

### Preparer Review (2025-12-05)

**Overall Assessment**: ✅ APPROVE with minor improvements recommended

**Key Feedback**:
1. **Portability testing criteria** needed in Phase 3 validation - INCORPORATED (Section 14.1)
2. **Expanded Phase 3 time estimate** more realistic (4-6 hours vs 2-3 hours) - INCORPORATED (Section 14.3)
3. **User journey testing** critical for usability validation - INCORPORATED (Section 14.3)
4. **MCP tool reference index** solves discovery problem - INCORPORATED (Section 12)
5. **Integration pattern example split** prevents future ambiguity - INCORPORATED (Section 13, Q6)
6. **Fallback strategy requirements** defines quality standards - INCORPORATED (Section 14.2)
7. **Workflow vs execution clarification** prevents philosophical confusion - INCORPORATED (Section 15)
8. **MCP tool maintenance strategy** for version changes and deprecation - INCORPORATED (Section 11)
9. **Edge case guidance** for generic tools and deprecation - INCORPORATED (Section 13, Q7 and Section 11.2)

**Strengths Identified by Preparer**:
- Excellent cross-referencing strategy (bidirectional, prevents navigation fatigue)
- Strong template structure (consistency aids maintenance)
- Comprehensive FAQ section (reduces future confusion)
- Clear boundary definition (WHEN/WHY vs HOW)

**All high-priority improvements incorporated.**

---

### Architect Update: Interim Implementation Documentation (2025-12-05)

**Change**: Added Section 6.2.1 to document the quick fix applied to all agents on 2025-12-05.

**Rationale**: The joint recommendation must reflect the actual state of implementation. The quick fix that prevents incorrect MCP tool invocation through the Skill tool is now deployed to all agents. This interim implementation:

1. **Establishes foundation for Phase 2**: Clarifies correct invocation mechanism (direct calls vs Skill tool)
2. **Prevents immediate errors**: Stops agents from attempting `Skill(skill: "mcp__sequential-thinking")`
3. **Maintains architectural alignment**: Reinforces the distinction between Skills (knowledge) and MCP tools (functions)
4. **Does not replace Phase 2**: The quick fix is temporary guidance, not comprehensive workflow integration

**Documentation Updates**:
- Executive Summary: Added note about interim implementation
- Section 6.2: Added "INTERIM IMPLEMENTATION STATUS" header
- Section 6.2.1: New subsection documenting quick fix details, relationship to Phase 2, and next steps

**Key Clarifications in Section 6.2.1**:
- Quick fix should **remain in place** even after Phase 2 completion (serves as valuable reminder)
- Phase 2 implementation will **build upon** the quick fix, not replace it
- Interim fix does **not reduce** Phase 2 effort (addresses mechanism, not comprehensive guidance)
- Recommendation to enhance quick fix with reference to full documentation once added

**Impact on Implementation Roadmap**: No changes to Phase 1, 2, or 3 effort estimates. The quick fix is supplementary guidance that complements, rather than substitutes for, the full Phase 2 implementation.

---

### Architect Review (2025-12-05)

**Systematic Evaluation**:

**1. Does the hybrid approach maintain architectural integrity?**

✅ **YES** - The hybrid approach successfully maintains all core architectural principles:

- **Separation of Concerns**: Pattern knowledge (Skills) vs Workflow knowledge (Agents) is a clear, enforceable boundary
- **Single Source of Truth**: Each piece of information appears in exactly one canonical location
- **Skills Portability**: Skills document conceptual applicability (WHEN/WHY) without invocation syntax, remaining valuable even if MCP tools unavailable
- **Agents as Orchestrators**: Workflow knowledge is orchestration logic, not pattern knowledge
- **Discoverability**: Bidirectional cross-references create clear navigation paths

**2. Agreement with Preparer's suggested improvements?**

✅ **FULL AGREEMENT** - All nine improvements strengthen the recommendation:

1. **Portability testing criteria**: Essential validation that skills remain valuable without MCP tools
2. **Expanded Phase 3 timeline**: Realistic estimate including template refinement
3. **User journey testing**: Critical validation from practitioner perspectives
4. **MCP tool reference index**: Solves reverse discovery problem (tool → skill lookup)
5. **Integration pattern examples**: Clarifies edge case of examples spanning both documents
6. **Fallback strategy requirements**: Prevents vague "use manual reasoning" fallbacks
7. **Workflow vs execution clarification**: Addresses philosophical objection clearly
8. **Maintenance strategy**: Essential for long-term sustainability
9. **Edge case guidance**: Handles generic tools and deprecation scenarios

**3. Architectural concerns not yet addressed?**

**One minor addition recommended**:

**Skill Discovery Enhancement**: While Section 12 provides a reference index, consider adding a brief "Available MCP Tools" section to each skill's SKILL.md that lists all MCP tools relevant to that domain upfront (before detailed sections). This aids quick scanning.

**Example addition to pact-architecture-patterns SKILL.md**:
```markdown
## Available MCP Tools for Architecture

This skill provides guidance for using these MCP tools in architectural decisions:
- **sequential-thinking**: Complex decision-making and trade-off analysis
- See sections below for detailed usage patterns and integration workflows
```

**Benefits**:
- Quick scan reveals which MCP tools are relevant to this skill
- Complements the reverse index in Section 12
- No duplication (detailed guidance still in dedicated sections)

**4. Refinements that strengthen the recommendation?**

**All preparer refinements are architecturally sound**. No additional refinements needed beyond the minor discovery enhancement above.

**5. Implementation readiness assessment**

✅ **READY FOR IMPLEMENTATION** with preparer improvements incorporated

**Evidence**:
- Clear templates for both Skills (Section 3.1) and Agents (Section 3.2)
- Comprehensive checklists (Section 3.3)
- Realistic effort estimates (11-16 hours total)
- Well-defined success criteria (Sections 9.1, 9.2, 9.3)
- Validation strategy (Section 14.3)
- Maintenance plan (Section 11)
- Risk mitigation (Section 10 - original document)
- Complete coverage of edge cases (Section 13)

**Architectural sign-off criteria met**:
- ✅ Maintains separation of concerns
- ✅ Preserves single source of truth
- ✅ Ensures skills portability
- ✅ Keeps agents as orchestrators
- ✅ Provides discoverability
- ✅ Includes maintenance strategy
- ✅ Handles edge cases and deprecation
- ✅ Realistic implementation plan

---

## 17. Final Consolidated Recommendation

### Status: ✅ APPROVED FOR IMPLEMENTATION

**Joint Position**: The hybrid approach successfully resolves the original Preparer-Architect disagreement by distinguishing between pattern knowledge (Skills: WHEN/WHY) and workflow knowledge (Agents: HOW). All architectural principles are maintained, all concerns addressed, and all improvements incorporated.

**Implementation Authority**: This document supersedes individual preparation and architecture proposals. It represents the unified, implementation-ready specification for MCP tools integration in the PACT framework.

**Changes from Original Joint Recommendation**:
1. Added Section 11: Maintenance Strategy (version changes, deprecation)
2. Added Section 12: MCP Tool Reference Index (reverse lookup)
3. Added Section 13: Enhanced FAQ (Q6, Q7)
4. Enhanced Section 14: Implementation Roadmap with portability validation, fallback requirements, user journey testing
5. Added Section 15: Workflow vs Execution Clarification
6. Added Section 16: Review History (Preparer and Architect reviews)
7. Revised Phase 3 timeline: 4-6 hours (was 2-3 hours)
8. Revised total effort: 11-16 hours (was 9-13 hours)
9. Added Section 6.2.1: Interim Implementation documenting quick fix applied to all agents (2025-12-05)

**Recommended Phase 1 Enhancement**: Add brief "Available MCP Tools" summary to each skill's SKILL.md for quick discovery (see Architect Review, Section 16).

**Next Steps**:
1. Create `/Users/mj/Sites/collab/PACT-prompt/docs/mcp-tools-reference.md` (Section 12)
2. Begin Phase 1: Skills updates (4-6 hours)
3. Implement Phase 2: Agents updates (3-4 hours)
4. Execute Phase 3: Validation with user journey testing (4-6 hours)

---

**Document Status**: ✅ FINAL RECOMMENDATION - Ready for implementation
**Review Status**: ✅ REVIEWED by Preparer and Architect - All improvements incorporated
**Next Steps**: Begin implementation with Phase 1 (Skills updates)

---

**Signed**:
- 📚 PACT Preparer (Research & Analysis) - APPROVED with improvements
- 🏛️ PACT Architect (Design & Integration) - APPROVED with improvements

**Agreement**: Both agents endorse this consolidated recommendation as the authoritative, implementation-ready guidance for MCP tools integration in the PACT framework. All architectural concerns addressed, all improvements incorporated.
