# Research Workflow Methodology

**Purpose**: Detailed step-by-step methodology for conducting systematic research during the PACT Prepare phase.

**When to Use**: Starting a new research task, evaluating technologies, documenting third-party integrations, or gathering requirements.

---

## Phase 1: Define Research Scope

### 1.1 Problem Statement

**Objective**: Clearly articulate what you're researching and why.

**Questions to Answer**:
- What problem are we trying to solve?
- What decisions need to be made based on this research?
- What are the success criteria for this research?
- Who will consume this research (Architect, developers, stakeholders)?

**Output Format**:
```markdown
## Research Objective

**Problem**: [1-2 sentence problem statement]

**Decision to Make**: [What choice or design decision depends on this research]

**Success Criteria**:
- [ ] [Specific outcome 1]
- [ ] [Specific outcome 2]
- [ ] [Specific outcome 3]

**Audience**: [Who needs this information and how they'll use it]
```

### 1.2 Requirements Gathering

**Identify Constraints**:
- **Functional**: What must the solution do?
- **Non-Functional**: Performance, security, scalability requirements
- **Team**: Existing skills, learning capacity, preferences
- **Technical**: Existing tech stack, integration requirements
- **Timeline**: When is this needed? (affects mature vs cutting-edge choices)
- **Budget**: Licensing costs, infrastructure costs, support costs

**Requirements Matrix Template**:
```markdown
| Requirement | Type | Priority | Constraint | Measurable Criteria |
|-------------|------|----------|------------|---------------------|
| User authentication | Functional | Must-have | OAuth 2.0 support | 99.9% uptime |
| Page load <2s | Performance | Must-have | Mobile 3G | Lighthouse score >90 |
| GDPR compliance | Security | Must-have | EU data residency | Pass compliance audit |
| Team can learn in 2 weeks | Team | Should-have | Moderate complexity | 80% team proficiency |
```

### 1.3 Scope Boundaries

**Define What's In Scope**:
- Specific technologies to research (list 3-5 candidates max)
- Integration points to document
- Security requirements to evaluate
- Performance benchmarks to measure

**Define What's Out of Scope**:
- Technologies that clearly don't meet must-have requirements
- Future requirements beyond current project
- Nice-to-have features that aren't priorities

**Anti-Pattern**: Researching everything tangentially related. Focus on decisions that need to be made now.

---

## Phase 2: Source Discovery

### 2.1 Primary Source Identification

**For Technologies/Frameworks**:
1. **Official Website**: Start with official project site
2. **Official Documentation**: Complete docs site walkthrough
3. **GitHub Repository**: README, wiki, issues, discussions
4. **Release Notes**: Changelog, migration guides, roadmap
5. **API Reference**: If applicable, comprehensive API docs

**For Third-Party Services/APIs**:
1. **Developer Portal**: Official developer documentation
2. **API Reference**: OpenAPI/Swagger specs, endpoint documentation
3. **SDKs**: Official client libraries and their docs
4. **Status Page**: Service reliability and incident history
5. **Pricing Page**: Cost structure, quotas, rate limits

**For Best Practices/Patterns**:
1. **Official Guides**: Framework-specific best practices
2. **Community Standards**: RFC-like documents, style guides
3. **Case Studies**: Official case studies from maintainers
4. **Conference Talks**: Official presentations from core team

### 2.2 Secondary Source Discovery

**Community Resources** (after primary sources):
- **Stack Overflow**: Search for common issues and patterns
- **GitHub Issues**: Known bugs, workarounds, feature requests
- **Reddit/Forums**: Community discussions about trade-offs
- **Awesome Lists**: Curated community resource collections

**Blog Posts and Tutorials** (verify against official docs):
- Check publication date (prefer <1 year old)
- Verify author credibility (contributors to the project?)
- Cross-reference with official documentation
- Test code examples before relying on them

### 2.3 Source Organization

**Create a Research Log**:
```markdown
## Research Sources

### Primary Sources
| Source | URL | Date Accessed | Version | Credibility | Notes |
|--------|-----|---------------|---------|-------------|-------|
| React Docs | https://react.dev | 2025-12-04 | 18.2 | Official | New docs site |
| GitHub Repo | https://github.com/facebook/react | 2025-12-04 | 18.2 | Official | Check security advisories |

### Secondary Sources
| Source | URL | Date Accessed | Credibility | Verified Against | Notes |
|--------|-----|---------------|-------------|------------------|-------|
| Stack Overflow | [link] | 2025-12-04 | Medium | Official docs | Workaround for issue X |
| Blog Post | [link] | 2025-12-04 | Low | Tested code | Performance tips |

### Excluded Sources
| Source | URL | Reason for Exclusion |
|--------|-----|---------------------|
| Tutorial Site X | [link] | Outdated (React 16), contradicts official docs |
```

---

## Phase 3: Information Extraction

### 3.1 Systematic Documentation Review

**For Each Technology Being Researched**:

**Step 1: Quick Start / Getting Started**
- Follow the official quick start guide
- Document installation steps
- Note any issues or platform-specific requirements
- Verify it works in your environment

**Step 2: Core Concepts**
- Read architecture/concepts sections
- Understand mental model and terminology
- Document key abstractions and patterns
- Note how it differs from alternatives

**Step 3: Feature Coverage**
- Map features to your requirements
- Test critical features in sandbox
- Document API usage for required features
- Identify gaps or missing capabilities

**Step 4: Advanced Topics**
- Performance optimization guidance
- Security best practices
- Error handling and debugging
- Testing strategies

**Step 5: Migration and Maintenance**
- Upgrade path between versions
- Breaking changes in recent releases
- Deprecation warnings
- Long-term support commitments

### 3.2 API Exploration Workflow

**For Third-Party APIs**:

**Authentication Setup**:
```markdown
1. Create developer account
2. Generate API credentials (keys, tokens)
3. Test authentication in sandbox/development environment
4. Document authentication flow:
   - Method: API key, OAuth 2.0, JWT, etc.
   - Where to store credentials (env vars, secrets manager)
   - Token refresh mechanism (if applicable)
   - Rate limits and quotas
```

**Endpoint Testing**:
```markdown
For each critical endpoint:
1. Read endpoint documentation
2. Test with sample request (Postman, curl, SDK)
3. Document request format:
   - HTTP method
   - Required headers
   - Request body schema
   - Query parameters
4. Document response format:
   - Success response structure
   - Error response structure
   - Status codes and meanings
5. Test error scenarios:
   - Invalid authentication
   - Malformed requests
   - Rate limit exceeded
   - Server errors
6. Document edge cases:
   - Pagination (for list endpoints)
   - Filtering and sorting
   - Null/empty values
   - Maximum sizes
```

**Working Examples**:
```markdown
Create minimal working code for each critical operation:
- Example 1: Create resource
- Example 2: Retrieve resource
- Example 3: Update resource
- Example 4: Delete resource
- Example 5: Handle webhook (if applicable)
- Example 6: Error handling

Store examples in docs/preparation/examples/ for reference
```

### 3.3 Security Research

**For Every Technology/API**:

**Known Vulnerabilities**:
```markdown
1. Check CVE database: https://cve.mitre.org/
2. Review GitHub Security Advisories
3. Check Snyk or npm audit for package vulnerabilities
4. Document findings:
   - CVE ID
   - Severity (Critical, High, Medium, Low)
   - Affected versions
   - Patched in version X
   - Mitigation strategy if no patch
```

**Security Best Practices**:
```markdown
From official documentation, capture:
1. Authentication recommendations
   - Supported methods
   - Token storage guidance
   - Session management
2. Authorization patterns
   - RBAC, ABAC, etc.
   - Permission models
3. Data protection
   - Encryption in transit (TLS version)
   - Encryption at rest
   - PII handling guidance
4. Input validation
   - Validation libraries
   - Sanitization patterns
5. Security headers
   - CORS configuration
   - CSP policies
   - Other security headers
```

**Compliance Considerations**:
```markdown
If applicable to your project:
- GDPR compliance features
- HIPAA compliance capabilities
- SOC 2 certification status
- Data residency options
- Audit logging capabilities
```

### 3.4 Performance Research

**Benchmarks and Characteristics**:
```markdown
1. Find official benchmarks or performance docs
2. Note performance characteristics:
   - Request latency (p50, p95, p99)
   - Throughput (requests/second)
   - Resource usage (CPU, memory)
   - Bundle size (for frontend libraries)
3. Document performance tuning options:
   - Caching strategies
   - Connection pooling
   - Lazy loading
   - Code splitting
4. Identify performance bottlenecks:
   - Known slow operations
   - Scaling limitations
   - Memory leaks or issues
```

---

## Phase 4: Comparative Analysis

### 4.1 Technology Comparison Framework

**When Comparing Multiple Options**:

**Step 1: Define Evaluation Criteria**
```markdown
Criteria categories:
1. Functional fit (does it meet requirements?)
2. Performance (speed, resource usage)
3. Security (built-in features, track record)
4. Developer experience (learning curve, documentation)
5. Ecosystem (community, libraries, tools)
6. Operational (maintenance, support, licensing)
7. Future-proofing (activity, roadmap, adoption trends)
```

**Step 2: Research Each Option Against Criteria**
```markdown
For each criterion:
- Gather objective data where possible (metrics, benchmarks)
- Document subjective assessments with rationale
- Note uncertainties or unknowns
- Cite sources for all claims
```

**Step 3: Create Comparison Matrix**
```markdown
| Criterion | Weight | Option A | Option B | Option C | Notes |
|-----------|--------|----------|----------|----------|-------|
| Meets Requirement X | High | ✅ Yes | ⚠️ Plugin | ❌ No | A has native support |
| Performance | High | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | B fastest in benchmarks |
| Security | High | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | C has built-in RBAC |
| Learning Curve | Medium | Moderate | Steep | Easy | Based on team feedback |
| Community | Medium | Large | Medium | Small | GitHub stars, npm downloads |
| License | High | MIT | Apache 2.0 | GPL v3 | C may have restrictions |
| Maintenance | High | Active | Active | Stale | Last commit dates |

Weights: High (3x), Medium (2x), Low (1x)
Scoring: ✅ (3), ⚠️ (2), ❌ (0) | Stars: 1-5
```

**Step 4: Calculate Weighted Scores** (if objective scoring possible)
```markdown
Option A Total: (3*3) + (4*3) + (4*3) + (2*2) + (2*2) + (3*3) + (3*3) = 69
Option B Total: (2*3) + (5*3) + (3*3) + (1*2) + (2*2) + (3*3) + (3*3) = 61
Option C Total: (0*3) + (3*3) + (5*3) + (3*2) + (1*2) + (1*3) + (2*3) = 41

Recommendation: Option A (highest weighted score, strong functional fit)
```

### 4.2 Trade-Off Analysis

**For Each Option, Document**:
```markdown
## Option A: [Technology Name]

### Strengths
- [Specific advantage with evidence]
- [Specific advantage with evidence]

### Weaknesses
- [Specific limitation with evidence]
- [Specific limitation with evidence]

### Trade-Offs
- Choosing this means: [What you gain]
- But it also means: [What you give up or accept]

### Best For
- [Scenario where this is the best choice]

### Avoid If
- [Scenario where this is not suitable]

### Risks
- [Potential future risk]
- [Mitigation strategy]
```

### 4.3 Using Sequential Thinking for Complex Decisions

**When to Use Sequential Thinking**:
- Comparing 3+ options with 5+ weighted criteria
- Complex trade-offs requiring deep reasoning
- Scenarios with conflicting requirements
- High-stakes decisions with long-term implications

**Sequential Thinking Prompt Template**:
```markdown
Context: [Describe the decision context and constraints]

Options: [List all options being considered]

Evaluation Criteria:
1. [Criterion 1 with weight and why it matters]
2. [Criterion 2 with weight and why it matters]
...

Please systematically evaluate each option against these criteria, considering:
- Direct evidence from documentation and testing
- Trade-offs between competing criteria
- Long-term implications for maintenance and scaling
- Risk factors and mitigation strategies

Provide a final recommendation with clear rationale.
```

---

## Phase 5: Documentation and Synthesis

### 5.1 Documentation Organization

**Create in `docs/preparation/` directory**:

**File Structure**:
```
docs/preparation/
├── technology-research.md      # Technology choices and rationale
├── api-documentation.md        # Third-party API integration details
├── dependencies.md             # Dependency analysis and compatibility
├── security-requirements.md    # Security findings and requirements
├── requirements-analysis.md    # Functional and non-functional requirements
└── examples/                   # Working code examples
    ├── api-auth-example.js
    ├── api-crud-example.js
    └── error-handling-example.js
```

### 5.2 Technology Research Documentation Template

```markdown
# Technology Research: [Technology Name]

**Research Date**: [Date]
**Researcher**: [Name]
**Decision**: [Technology choice or recommendation]

## Executive Summary

[2-3 paragraph summary of research findings and recommendation]

## Technology Overview

**Name**: [Official name]
**Version Researched**: [Exact version]
**Official Site**: [URL]
**Repository**: [GitHub URL]
**License**: [License type]

**Purpose**: [What problem does this solve?]

**Core Features**:
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Requirements Coverage

| Requirement | Supported | How | Notes |
|-------------|-----------|-----|-------|
| [Requirement 1] | ✅ Yes | [Method/feature] | [Additional context] |
| [Requirement 2] | ⚠️ Partial | [Workaround needed] | [Limitation details] |
| [Requirement 3] | ❌ No | N/A | [Alternative approach] |

## Technical Details

### Installation
```[language]
[Installation commands]
```

### Configuration
```[language]
[Configuration example]
```

### Integration
[How this integrates with existing stack]

### API Usage
[Key APIs and usage patterns]

## Performance

**Benchmarks**: [Link to benchmarks or measurements]
**Characteristics**:
- Latency: [Measurements]
- Throughput: [Measurements]
- Resource usage: [CPU/Memory]

**Optimization options**: [List available optimizations]

## Security

**Known Vulnerabilities**:
- [CVE ID if any, or "None found"]

**Security Features**:
- [Built-in security feature 1]
- [Built-in security feature 2]

**Best Practices**: [Link to security guidance or summary]

## Dependencies

**Runtime Dependencies**:
- [Dependency 1]: [version range]
- [Dependency 2]: [version range]

**Peer Dependencies**:
- [Peer dependency 1]: [version range]

**Compatibility Matrix**:
| Package | Version | Compatible? | Notes |
|---------|---------|-------------|-------|
| [Package] | [Version] | ✅ Yes | [Context] |

## Community and Ecosystem

**Community Size**: [GitHub stars, npm downloads, etc.]
**Maintenance Status**: [Active, last commit date]
**Major Contributors**: [Organizations/individuals]
**Ecosystem**:
- [Available plugin 1]
- [Available plugin 2]
- [Integration 1]

## Limitations and Gotchas

- [Known limitation 1]
- [Known limitation 2]
- [Gotcha or edge case 1]

## Recommendation

**Decision**: [Recommend / Don't Recommend / Conditional]

**Rationale**:
[Clear explanation of why this is or isn't the right choice]

**Conditions** (if conditional):
[What needs to be true for this to be the right choice]

**Alternatives Considered**:
- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]

## Next Steps for Architect Phase

- [Action item 1]
- [Action item 2]
- [Decision or design needed]

## Sources

1. [Source 1 name and URL]
2. [Source 2 name and URL]
...
```

### 5.3 API Documentation Template

```markdown
# API Documentation: [API Name]

**Research Date**: [Date]
**API Version**: [Version]
**Documentation URL**: [URL]

## Overview

[Brief description of what this API provides]

## Authentication

**Method**: [API Key / OAuth 2.0 / JWT / etc.]

**Setup**:
1. [Step 1]
2. [Step 2]
...

**Credentials Storage**: [Environment variables, secrets manager, etc.]

**Example**:
```[language]
[Authentication code example]
```

## Endpoints

### [Endpoint Name]

**Purpose**: [What this endpoint does]

**HTTP Method**: [GET/POST/PUT/DELETE/PATCH]
**URL**: `[endpoint URL pattern]`

**Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Request Body** (if applicable):
```json
{
  "field1": "value",
  "field2": "value"
}
```

**Success Response** (200):
```json
{
  "id": "123",
  "field1": "value",
  "field2": "value"
}
```

**Error Responses**:
- **400 Bad Request**: [When this occurs]
  ```json
  {"error": "Invalid input", "details": "..."}
  ```
- **401 Unauthorized**: [When this occurs]
- **429 Too Many Requests**: [When this occurs]

**Rate Limits**: [X requests per Y time period]

**Pagination** (if applicable): [How pagination works]

**Example**:
```[language]
[Working code example]
```

[Repeat for each critical endpoint]

## Webhooks

[If API supports webhooks, document format and handling]

## Error Handling

**Error Response Format**:
```json
{
  "error": "string",
  "message": "string",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes**:
| Code | Meaning | Action |
|------|---------|--------|
| [CODE] | [Meaning] | [How to handle] |

## Rate Limits and Quotas

**Rate Limits**: [Requests per time period]
**Quotas**: [Daily/monthly limits]
**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

**Handling Rate Limits**: [Retry strategy, backoff algorithm]

## Security

**TLS**: [Minimum version required]
**Authentication Tokens**: [Where to store, rotation policy]
**Data Sensitivity**: [PII handling, encryption requirements]
**Compliance**: [Any compliance requirements]

## Testing

**Sandbox Environment**: [URL if available]
**Test Credentials**: [How to obtain]
**Test Data**: [What test data is available]

## SDK / Client Libraries

**Official SDKs**:
- [Language]: [Package name, version]
- [Language]: [Package name, version]

**Example with SDK**:
```[language]
[Code example using official SDK]
```

## Known Issues

- [Known issue 1]
- [Known issue 2]

## Next Steps for Architect Phase

- [How this API fits into architecture]
- [Which endpoints to use for each use case]
- [Error handling strategy]

## Sources

1. [API documentation URL]
2. [Additional references]
```

### 5.4 Handoff to Architect Phase

**Create Summary Document**:
```markdown
# Prepare Phase Summary

## Research Completed

- ✅ Technology Research: [Technology name]
- ✅ API Documentation: [API name]
- ✅ Security Requirements: Documented
- ✅ Dependencies: Mapped
- ✅ Requirements Analysis: Complete

## Key Findings

**Recommended Technology Stack**:
- [Component 1]: [Technology] - [Rationale]
- [Component 2]: [Technology] - [Rationale]

**Critical Requirements**:
- [Requirement 1]
- [Requirement 2]

**Security Constraints**:
- [Constraint 1]
- [Constraint 2]

**Performance Expectations**:
- [Expectation 1]
- [Expectation 2]

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| [Risk 1] | [High/Med/Low] | [How to mitigate] |

## Recommendations for Architecture

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Open Questions for Architect

- [ ] [Question that architecture needs to answer]
- [ ] [Design decision needed]

## Documentation Location

All research documentation available in:
`docs/preparation/`

- technology-research.md
- api-documentation.md
- dependencies.md
- security-requirements.md
- requirements-analysis.md
- examples/
```

---

## Quality Checklist

Before marking Prepare phase complete:

**Completeness**:
- [ ] All technology options evaluated with objective criteria
- [ ] Security requirements identified and documented
- [ ] API integrations tested with working examples
- [ ] Version compatibility verified across all dependencies
- [ ] Performance expectations documented
- [ ] All research sources cited with links and dates

**Quality**:
- [ ] Sources are credible (prioritized official documentation)
- [ ] Information is current (checked dates and versions)
- [ ] Trade-offs clearly documented with rationale
- [ ] Recommendations have clear, evidence-based rationale
- [ ] Edge cases and limitations captured
- [ ] Working code examples provided for integrations

**Handoff Readiness**:
- [ ] Documentation is in `docs/preparation/` folder
- [ ] Templates followed for consistency
- [ ] Architect has all information needed to proceed
- [ ] No blocking questions or undefined requirements
- [ ] Security and performance constraints clear
- [ ] Summary document created for quick reference

**PACT Principles Applied**:
- [ ] Documentation First: All findings documented comprehensively
- [ ] Context Gathering: Full scope and requirements understood
- [ ] Dependency Mapping: All dependencies identified and verified
- [ ] API Exploration: Third-party APIs tested and documented
- [ ] Research Patterns: Established solutions researched and referenced
- [ ] Requirement Validation: Requirements confirmed with stakeholders

---

## Summary

This research workflow ensures systematic, thorough preparation that sets up the Architecture phase for success. By following these steps methodically, you create comprehensive documentation that enables informed design decisions and reduces risk of costly rework in later phases.

**Key Principles**:
- Start with clear scope and success criteria
- Prioritize official sources over secondary content
- Test integrations, don't just read about them
- Document objectively with evidence and citations
- Consider security and performance from the start
- Create actionable handoff documentation

**Time Investment**: Proper preparation takes time, but saves exponentially more in later phases. Invest the time upfront.
