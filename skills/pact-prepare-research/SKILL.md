---
name: pact-prepare-research
description: |
  PREPARE PHASE: Research methodologies and documentation gathering workflows.

  Provides systematic research approaches, source evaluation criteria, documentation
  templates, API exploration techniques, and technology comparison frameworks.

  Use when: conducting technology research, evaluating documentation sources,
  comparing framework options, analyzing API documentation, gathering requirements.
allowed-tools:
  - Read
  - WebSearch
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Prepare"
  version: "1.0.0"
  primary-agent: "pact-preparer"
  related-skills:
    - pact-architecture-patterns
    - pact-security-patterns
  updated: "2025-12-04"
---

# PACT Prepare Research

## Overview

The Prepare phase is the foundation of principled software development. This skill provides systematic methodologies for conducting thorough research, evaluating information sources, documenting findings, and gathering requirements before moving to architecture and implementation.

**Core Principle**: Good preparation prevents poor performance. Time invested in research saves exponentially more time in later phases.

This skill helps you:
- Conduct systematic technology research with credible sources
- Evaluate and compare framework/library options objectively
- Document APIs, dependencies, and integration requirements
- Capture security, performance, and compatibility requirements
- Create comprehensive preparation documentation for the Architect phase

## Quick Reference

### Research Workflow Overview

```
1. DEFINE SCOPE
   └─> What problem are we solving?
   └─> What are the constraints and requirements?
   └─> What decisions need to be made?

2. GATHER SOURCES
   └─> Official documentation (highest priority)
   └─> Community resources (GitHub, Stack Overflow)
   └─> Blog posts and tutorials (lowest priority)

3. EVALUATE CREDIBILITY
   └─> Is the source authoritative?
   └─> Is the information current and maintained?
   └─> Does it match our version/context?

4. DOCUMENT FINDINGS
   └─> Use structured templates (see references/)
   └─> Capture version-specific information
   └─> Note security and performance implications

5. SYNTHESIZE DECISIONS
   └─> Compare options with objective criteria
   └─> Document trade-offs and rationale
   └─> Provide recommendations for Architect phase
```

### Source Credibility Hierarchy

**Tier 1 - Official Documentation (Highest Trust)**:
- Official project documentation sites
- Official GitHub repositories and READMEs
- Published API references from vendors
- Official migration guides and changelogs

**Tier 2 - Community Resources (Medium Trust)**:
- Well-maintained GitHub projects with active communities
- Stack Overflow answers from reputable users
- Official forum discussions and issue threads
- Community-maintained awesome-lists

**Tier 3 - Secondary Sources (Verify First)**:
- Technical blog posts (check date and author credibility)
- Tutorial sites (verify against official docs)
- Third-party documentation aggregators
- Social media discussions

**Red Flags - Avoid or Verify Heavily**:
- Outdated content (>2 years old for fast-moving tech)
- No version information provided
- Anonymous or unknown authors
- Contradicts official documentation
- No sources or references cited

### When to Use Sequential Thinking

The `mcp__sequential-thinking__sequentialthinking` tool is valuable for:

**Complex Technology Comparisons**:
- Evaluating 3+ framework options with multiple criteria
- Understanding trade-offs between architectural approaches
- Reasoning through version compatibility matrices

**Security Analysis**:
- Evaluating security implications of technology choices
- Understanding threat models for specific implementations
- Analyzing authentication/authorization patterns

**Dependency Chain Reasoning**:
- Understanding transitive dependencies
- Evaluating compatibility across multiple packages
- Reasoning through version constraint conflicts

**Example Sequential Thinking Trigger**:
```
When comparing React, Vue, and Svelte for a new project with these constraints:
- Team experience: Moderate JavaScript, no framework experience
- Performance: Critical (public-facing, high traffic)
- Ecosystem: Need robust component libraries
- Timeline: 3-month MVP

Use sequential-thinking to systematically evaluate:
1. Learning curve for team
2. Performance characteristics
3. Ecosystem maturity
4. Long-term maintainability
5. Final recommendation with rationale
```

### Documentation Gathering Checklist

For every technology/library researched, capture:

- [ ] **Version Information**: Exact version researched, compatibility range
- [ ] **Core Features**: What problems does it solve?
- [ ] **Installation**: How to install and configure
- [ ] **Integration**: How it integrates with our tech stack
- [ ] **API Surface**: Key APIs, methods, patterns we'll use
- [ ] **Dependencies**: What it requires (runtime and peer dependencies)
- [ ] **Security**: Known vulnerabilities, security best practices
- [ ] **Performance**: Performance characteristics, benchmarks if available
- [ ] **Limitations**: What it doesn't do well, known issues
- [ ] **Community Health**: Maintenance status, community size, update frequency
- [ ] **License**: Ensure compatibility with project requirements
- [ ] **Migration Path**: Upgrade path, breaking changes in roadmap

### API Research Workflow

When exploring APIs (REST, GraphQL, SDK, etc.):

**1. Authentication & Setup**
- Obtain API credentials (keys, tokens, OAuth setup)
- Test authentication in development environment
- Document authentication flow and security requirements

**2. Endpoint Exploration**
- Identify all endpoints/methods needed for use cases
- Document request/response formats
- Note rate limits, pagination, filtering capabilities

**3. Error Handling**
- Document error codes and meanings
- Test error scenarios (invalid input, auth failures, rate limits)
- Capture error response formats

**4. Version Compatibility**
- Identify API version (v1, v2, etc.)
- Document deprecation notices
- Note breaking changes between versions

**5. Testing & Examples**
- Create minimal working examples for each endpoint
- Test edge cases and error conditions
- Document working code snippets for Architect phase

**Template**: See `references/api-documentation-guide.md` for detailed API documentation template.

### Technology Comparison Matrix

When comparing multiple options, use this framework:

| Criterion | Option A | Option B | Option C | Weight |
|-----------|----------|----------|----------|--------|
| **Functional Requirements** |
| Meets feature X | ✅ Native | ⚠️ Plugin | ❌ No | High |
| Meets feature Y | ✅ Yes | ✅ Yes | ✅ Yes | Medium |
| **Non-Functional Requirements** |
| Performance | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | High |
| Security | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | High |
| **Team & Ecosystem** |
| Learning curve | Moderate | Steep | Easy | High |
| Community size | Large | Medium | Small | Medium |
| Documentation | Excellent | Good | Poor | High |
| **Operational** |
| License | MIT | Apache 2.0 | GPL | High |
| Maintenance | Active | Active | Stale | High |
| Dependencies | 5 | 15 | 2 | Medium |

**Scoring System**:
- ✅ Fully supported
- ⚠️ Partial support or workaround needed
- ❌ Not supported
- ⭐ Rating scale (1-5 stars)

**Weights**: High (3x), Medium (2x), Low (1x)

For detailed comparison framework: See `references/technology-comparison.md`

### Version Compatibility Tracking

Critical for preventing integration issues:

**Package Matrix Template**:
```markdown
## Dependency Compatibility

| Package | Version | Compatible With | Incompatible With | Notes |
|---------|---------|----------------|-------------------|-------|
| React | 18.2.0 | Node ≥16 | React Router <6 | Concurrent features |
| TypeScript | 5.2.0 | React 18.x | ESLint <8.0 | Uses new decorators |
| Vite | 4.5.0 | React 18.x | Webpack - | Dev server only |
```

**Key Tracking Points**:
- Runtime version requirements (Node.js, Python, Ruby)
- Peer dependencies and version ranges
- Breaking changes in major version upgrades
- Deprecated features affecting our use cases
- Security vulnerabilities by version

### Security Research Guidance

During Prepare phase, identify and document:

**1. Known Vulnerabilities**
- Check CVE databases for technology/version
- Review GitHub Security Advisories
- Document CVE IDs and severity levels

**2. Security Best Practices**
- Authentication patterns recommended by official docs
- Authorization mechanisms
- Data encryption requirements (in transit, at rest)
- Input validation and sanitization guidance

**3. Compliance Requirements**
- GDPR, HIPAA, SOC2, or other compliance needs
- Data retention and deletion requirements
- Audit logging requirements

**4. Security Contacts**
- Security policy (SECURITY.md in repo)
- Responsible disclosure process
- Security mailing lists or advisories

For comprehensive security research: Reference `pact-security-patterns` skill

### Common Research Anti-Patterns

**❌ AVOID**:
- Relying solely on blog posts or tutorials
- Skipping version compatibility verification
- Not testing APIs/libraries before architectural decisions
- Copying code without understanding it
- Ignoring security advisories
- Researching only happy-path scenarios

**✅ DO INSTEAD**:
- Always verify against official documentation
- Test integrations in a sandbox environment
- Document error cases and limitations
- Understand trade-offs and design decisions
- Track security issues and mitigation strategies
- Research edge cases and failure scenarios

## Decision Tree: Which Reference to Load

Use this guide to determine which reference file to read for specific research tasks:

```
What are you researching?

├─ Need step-by-step research methodology?
│  └─> Read: references/research-workflow.md
│     (Detailed process for conducting systematic research)

├─ Evaluating credibility of sources?
│  └─> Read: references/source-evaluation.md
│     (Criteria for assessing source quality and reliability)

├─ Need templates for documentation output?
│  └─> Read: references/documentation-templates.md
│     (Templates for technology summaries, API docs, comparison matrices)

└─ All of the above for comprehensive guidance?
   └─> Read all three references in order:
      1. research-workflow.md (how to conduct research)
      2. source-evaluation.md (how to evaluate findings)
      3. documentation-templates.md (how to document results)
```

## Additional Resources

### Reference Files

**references/research-workflow.md**
- Complete step-by-step research methodology
- Detailed guidance for each research phase
- Integration with PACT workflow
- **Load when**: Starting a new research task or need systematic approach

**references/source-evaluation.md**
- Detailed criteria for assessing source credibility
- How to verify information accuracy
- Handling conflicting information
- **Load when**: Evaluating reliability of documentation or community resources

**references/documentation-templates.md**
- Complete templates for all Prepare phase outputs
- Technology summary template
- API documentation template
- Comparison matrix template
- Requirements documentation template
- **Load when**: Creating documentation for handoff to Architect phase

### Related Skills

**pact-architecture-patterns**
- System design patterns that inform research priorities
- Architectural constraints that affect technology choices
- **Use together**: Prepare research feeds into Architect patterns

**pact-security-patterns**
- Security research requirements during Prepare phase
- Threat modeling frameworks
- Security evaluation criteria
- **Use together**: Reference security patterns when evaluating technology security

## Integration with PACT Workflow

### Inputs to Prepare Phase

**From User/Project Requirements**:
- Problem statement or feature request
- Constraints (timeline, budget, team skills)
- Existing tech stack and integration points
- Performance and security requirements

### Prepare Phase Research Activities

1. **Technology Research**: Evaluate frameworks, libraries, tools
2. **API Documentation**: Document third-party APIs and integrations
3. **Dependency Analysis**: Map dependencies and version compatibility
4. **Security Research**: Identify security requirements and best practices
5. **Best Practices**: Research established patterns and conventions

### Outputs to Architect Phase

**Deliverables** (created in `docs/preparation/`):
- `technology-research.md`: Technology choices with rationale
- `api-documentation.md`: Third-party API integration details
- `dependencies.md`: Dependency tree and version compatibility
- `security-requirements.md`: Security findings and recommendations
- `requirements-analysis.md`: Functional and non-functional requirements

**Key Information for Architects**:
- Recommended technology stack with trade-offs
- Integration points and API contracts
- Security constraints and compliance needs
- Performance expectations and benchmarks
- Version compatibility matrix
- Known risks and mitigation strategies

### Handoff to Architect

The Architect phase uses Prepare phase outputs to:
- Design system architecture aligned with technology constraints
- Define component boundaries based on integration requirements
- Specify API contracts informed by third-party API research
- Incorporate security requirements into architectural design
- Plan for version management and dependency updates

**Quality Gate**: Architecture cannot begin until Prepare phase delivers comprehensive research covering:
- ✅ All technology choices documented with rationale
- ✅ Security requirements identified
- ✅ Dependencies mapped with version compatibility
- ✅ Integration points documented with examples
- ✅ Performance and scalability requirements captured

## MCP Tools for Research

This section provides guidance on WHEN and WHY to use MCP tools during the Prepare phase. See agent documentation for invocation syntax.

### Available MCP Tools

The following MCP tools enhance research activities:
- **sequential-thinking**: Complex decision-making and technology comparisons
- **context7**: Library documentation lookup

---

### sequential-thinking

**Purpose**: Extended reasoning capability for systematic technology evaluation and research decisions

**When to use**:
- Comparing 3+ technology options with multiple competing criteria (e.g., React vs Vue vs Svelte with team expertise, performance, ecosystem maturity, and timeline constraints)
- Evaluating security trade-offs across multiple threat vectors (e.g., authentication mechanisms with different attack surfaces)
- Analyzing version compatibility matrices with complex dependency chains
- Resolving conflicting documentation sources or community opinions with transparent reasoning
- Planning integration strategies for unfamiliar third-party services with multiple configuration options

**When NOT to use**:
- Simple binary technology choices with clear best practices (e.g., HTTPS vs HTTP)
- Time-sensitive exploratory research where quick iteration is preferred
- Well-established patterns with official recommendation (e.g., password hashing with bcrypt)
- Research gathering facts rather than evaluating trade-offs

**Value for Prepare phase**: Transparent reasoning process creates auditable documentation of research decisions. Reduces risk of overlooking critical evaluation criteria during technology selection.

**Integration approach**: Define research scope → Gather sources from official docs and community → Use sequential-thinking to evaluate complex trade-offs → Synthesize reasoning into preparation markdown with clear recommendations.

**See pact-preparer agent for invocation syntax and workflow integration.**

---

### context7 (Library Documentation Lookup)

**Purpose**: Fetch current, version-specific documentation directly from official library sources

**When to use**:
- Researching popular JavaScript/TypeScript libraries with rapidly evolving APIs (React, Next.js, Vue, Angular, Express, Nest.js)
- Researching Python frameworks and libraries (FastAPI, Django, Flask, SQLAlchemy, Pydantic)
- Verifying version-specific features before documenting technology recommendations
- Confirming breaking changes between major versions during migration research
- Getting canonical code examples for integration planning from official sources

**When NOT to use**:
- Internal or proprietary libraries (not indexed in context7)
- Very new libraries released within last 2-3 months (may not be indexed yet)
- Broad ecosystem research requiring comparison discussions (use WebSearch for community insights and comparisons)
- Historical context about technology evolution (WebSearch better for blog posts, migration guides, lessons learned)
- Researching configuration tools, build tools, or CLI utilities (context7 focuses on application libraries)

**Value for Prepare phase**: Ensures research documentation is based on current, authoritative sources rather than outdated blog posts. Reduces risk of documenting deprecated APIs or incorrect version assumptions.

**Integration approach**: Identify libraries from project requirements → Use context7 for official API documentation → Complement with WebSearch for community insights and real-world patterns → Synthesize official docs + community wisdom into comprehensive preparation markdown.

**See pact-preparer agent for invocation workflow.**

---

## Self-Verification Checklist

Before completing Prepare phase research, verify:

**Completeness**:
- [ ] All technology options evaluated with objective criteria
- [ ] Security requirements identified and documented
- [ ] API integrations tested with working examples
- [ ] Version compatibility verified across all dependencies
- [ ] Performance expectations documented
- [ ] All research sources cited with links

**Quality**:
- [ ] Sources are credible (prefer official documentation)
- [ ] Information is current (check dates and versions)
- [ ] Trade-offs clearly documented
- [ ] Recommendations have clear rationale
- [ ] Edge cases and limitations captured

**Handoff Readiness**:
- [ ] Documentation is in `docs/preparation/` folder
- [ ] Templates followed for consistency
- [ ] Architect has all information needed to proceed
- [ ] No blocking questions or undefined requirements
- [ ] Security and performance constraints clear

**PACT Principles Applied**:
- [ ] Documentation First: All findings documented before moving forward
- [ ] Context Gathering: Full scope and requirements understood
- [ ] Dependency Mapping: All dependencies identified and verified
- [ ] API Exploration: Third-party APIs tested and documented
- [ ] Research Patterns: Established solutions researched
- [ ] Requirement Validation: Requirements confirmed with stakeholders

## Common Prepare Phase Scenarios

### Scenario 1: Evaluating Authentication Solutions

**Context**: Need to add authentication to an application

**Research Workflow**:
1. Read official docs for candidate solutions (Auth0, Firebase Auth, Passport.js, etc.)
2. Compare features against requirements (social login, MFA, SSO, etc.)
3. Test authentication flows in sandbox
4. Document security model and token management
5. Evaluate pricing and scaling implications
6. Provide recommendation with rationale

**Key Outputs**: Authentication comparison matrix, security requirements, integration examples

### Scenario 2: Third-Party API Integration

**Context**: Integrate with payment processor (Stripe, PayPal, etc.)

**Research Workflow**:
1. Obtain sandbox API credentials
2. Read API reference documentation
3. Test key endpoints (create payment, handle webhooks, refunds)
4. Document error handling and edge cases
5. Capture rate limits and quotas
6. Document security requirements (PCI compliance, data handling)

**Key Outputs**: API documentation, working code examples, security requirements

### Scenario 3: Framework Selection

**Context**: Choose frontend framework for new project

**Research Workflow**:
1. Define evaluation criteria (performance, team skills, ecosystem, etc.)
2. Research candidate frameworks (React, Vue, Svelte, etc.)
3. Use sequential-thinking for complex trade-off analysis
4. Create comparison matrix with weighted scoring
5. Build proof-of-concept for top 2 candidates
6. Document recommendation with rationale

**Key Outputs**: Technology comparison matrix, POC code, recommendation document

## Tips for Effective Preparation

**Time Management**:
- Allocate 15-25% of total project time to Prepare phase
- Complex integrations may require more research time
- Set research time-box to prevent analysis paralysis

**Collaboration**:
- Involve team members with domain expertise
- Review findings with security team early
- Validate assumptions with stakeholders

**Documentation**:
- Use consistent templates for easy reference
- Include links to all sources
- Keep it concise but comprehensive
- Focus on decisions and rationale, not just facts

**Iteration**:
- Prepare phase may need revisiting during Architect phase
- New discoveries may require additional research
- Keep documentation updated as understanding evolves

## Summary

The Prepare phase builds the knowledge foundation for successful implementation. By conducting systematic research, evaluating sources critically, and documenting findings comprehensively, you enable the Architect phase to make informed design decisions aligned with project requirements and constraints.

**Remember**: Time invested in thorough preparation prevents costly rework in later phases. Good research is an investment, not an expense.

For detailed methodologies and templates, reference the files in the `references/` directory based on your specific research needs.
