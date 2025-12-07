# Source Evaluation and Credibility Assessment

**Purpose**: Detailed criteria and frameworks for evaluating the credibility, accuracy, and reliability of information sources during research.

**When to Use**: Assessing documentation quality, evaluating conflicting information, determining which sources to trust, verifying claims from secondary sources.

---

## Source Credibility Hierarchy

### Tier 1: Official Sources (Highest Trust)

**Characteristics**:
- Published by the project maintainers or vendor
- Hosted on official domains
- Actively maintained and updated
- Versioned documentation aligned with releases

**Examples**:
- Official project websites (react.dev, nodejs.org, etc.)
- Official GitHub repositories and READMEs
- Vendor API documentation portals
- Official migration guides and changelogs
- Published RFCs and specifications

**Verification Checklist**:
- [ ] URL matches official domain
- [ ] Content matches version you're researching
- [ ] Recently updated (check last modified date)
- [ ] Cross-referenced with other official sources
- [ ] No conflicting information within official docs

**When to Be Cautious**:
- Outdated sections in otherwise current docs (check "last updated")
- Beta/experimental features marked as unstable
- Deprecated sections that may not apply to current version
- Regional variations (some features not available in all regions)

---

### Tier 2: Community Resources (Medium Trust)

**Characteristics**:
- Created by community members or recognized experts
- Generally reliable but may contain opinions or outdated info
- Varies in quality and maintenance
- Useful for practical insights not in official docs

**Examples**:
- Well-maintained GitHub projects with active communities
- Stack Overflow answers from high-reputation users
- GitHub Discussions and issue threads
- Community-maintained "Awesome" lists
- Conference talks from contributors

**Verification Checklist**:
- [ ] Author is recognizable contributor or expert
- [ ] Content is recent (prefer <6 months for fast-moving tech)
- [ ] Multiple community members confirm or upvote
- [ ] Cross-reference claims with official documentation
- [ ] Test code examples before relying on them

**Credibility Indicators**:

**Stack Overflow**:
- Answer score >10 (more community validation)
- Answerer has >1000 reputation
- Answer is accepted (green checkmark)
- Recent activity on the question (not abandoned)
- Multiple answers agreeing on approach

**GitHub Issues**:
- Issue has maintainer response
- Solution marked as resolved
- Multiple people confirm the fix works
- Issue is closed (problem solved)
- Recent activity (<6 months)

**GitHub Repositories**:
- Stars >100 (community validation)
- Recent commits (active maintenance)
- Multiple contributors (not abandoned)
- Good documentation in README
- Active issue resolution

**Community Guides**:
- Author has published other quality content
- Multiple citations to official sources
- Clear disclaimer when information is opinion
- Code examples are testable
- Comments show community engagement

---

### Tier 3: Secondary Sources (Verify First)

**Characteristics**:
- Individual blogs, tutorials, courses
- Quality varies significantly
- May be outdated or contain errors
- Can provide useful context but needs verification

**Examples**:
- Individual developer blogs
- Tutorial websites (freeCodeCamp, tutorials point, etc.)
- Medium articles and dev.to posts
- YouTube videos and courses
- Third-party documentation aggregators

**Verification Requirements**:
- [ ] Check publication date (prefer <1 year)
- [ ] Verify ALL code examples work
- [ ] Cross-reference with official docs
- [ ] Check author's credibility and expertise
- [ ] Look for corrections in comments
- [ ] Test claims before accepting them

**Red Flags**:
- Article >2 years old for fast-moving tech
- No version information provided
- Code examples don't work or have errors
- Contradicts official documentation
- Author unknown or unverifiable
- No sources or citations provided
- Comments point out errors not corrected
- Clickbait titles ("10 Tricks Experts Don't Want You to Know")

**When Secondary Sources Are Useful**:
- Explaining complex concepts in simpler terms
- Providing real-world examples and use cases
- Showing practical workflows not in official docs
- Sharing lessons learned from experience
- Comparing different approaches

**Always Verify By**:
1. Testing code examples yourself
2. Cross-referencing with official docs
3. Checking if information still applies to current version
4. Looking for other sources confirming the same information

---

### Tier 4: Avoid or Verify Heavily

**Characteristics**:
- Highly unreliable or unverifiable
- Often outdated, incomplete, or wrong
- May be misleading or clickbait

**Examples**:
- Forums with no moderation or vetting
- Answers without sources or evidence
- Paywalled content you can't verify
- AI-generated content without human review
- Social media posts (Twitter, LinkedIn)
- Marketing materials disguised as documentation

**Why to Avoid**:
- No accountability for accuracy
- Often outdated without clear dates
- May be biased (selling a product/service)
- Difficult to verify claims
- Waste time chasing incorrect information

**If You Must Use These Sources**:
1. Treat as hypothesis, not fact
2. Verify with multiple authoritative sources
3. Test thoroughly before relying on
4. Document that source is low-confidence
5. Plan for contingency if information is wrong

---

## Evaluating Source Credibility

### Author Credibility Assessment

**For Individual Authors**:
```markdown
Author Credibility Checklist:
- [ ] Author identified by real name (not anonymous)
- [ ] Author has expertise in the domain
- [ ] Author has public track record (GitHub, portfolio)
- [ ] Author cites sources for claims
- [ ] Author acknowledges limitations and uncertainties
- [ ] Author responsive to corrections in comments
```

**Credibility Levels**:

**High Credibility**:
- Core maintainer or contributor to the project
- Recognized expert in the field (conference speaker, book author)
- Active open-source contributor with visible work
- Professional role aligned with topic (employed by vendor, tech lead)

**Medium Credibility**:
- Experienced developer with public portfolio
- Regular blogger with track record
- Active in community with positive reputation
- Clear professional experience in domain

**Low Credibility**:
- Anonymous or pseudonymous with no track record
- No verifiable expertise in the domain
- First-time blogger or commenter
- No public work to validate expertise

**Unknown Credibility**:
- Cannot verify author identity
- No information about author background
- Generic name with no web presence

**Action**: Treat low/unknown credibility sources as hypotheses requiring verification.

---

### Content Quality Indicators

**High-Quality Content Has**:
- Clear structure and organization
- Specific version information
- Concrete examples with working code
- Citations to official sources
- Acknowledgment of limitations
- Recent publication or update date
- Technical depth appropriate to topic
- Clear explanations of trade-offs

**Low-Quality Content Has**:
- Vague or generic information
- No version information
- Broken or incomplete examples
- No sources or citations
- Overly broad claims without evidence
- Old publication date with no updates
- Superficial coverage
- One-sided view (no trade-offs discussed)

**Warning Signs**:
- Absolute statements without caveats ("Always do X", "Never do Y")
- Claims without evidence or examples
- Contradictions within the content
- Code examples that don't run
- Poor grammar or machine-translated content
- Excessive marketing or promotional language
- Promises of shortcuts or magic solutions

---

### Timeliness Assessment

**How Recent Should Sources Be?**

**Technology Categories**:

| Category | Ideal Age | Acceptable Age | Too Old |
|----------|-----------|----------------|---------|
| Frontend frameworks (React, Vue, etc.) | <6 months | <1 year | >2 years |
| Languages (JavaScript, Python, etc.) | <1 year | <2 years | >3 years |
| Backend frameworks (Express, Django, etc.) | <1 year | <2 years | >3 years |
| Databases (PostgreSQL, MongoDB, etc.) | <1 year | <3 years | >5 years |
| DevOps tools (Docker, Kubernetes, etc.) | <6 months | <1 year | >2 years |
| Security practices | <6 months | <1 year | >1 year |
| Design patterns | <2 years | <5 years | >10 years |
| Core CS concepts | <5 years | <10 years | Never (if fundamental) |

**Checking Timeliness**:
```markdown
- [ ] Publication date clearly visible
- [ ] Last updated date shown (for living documents)
- [ ] Version information specified
- [ ] References to current versions, not deprecated ones
- [ ] No references to sunset products/services
- [ ] Examples use current syntax and APIs
```

**When Older Content Is Acceptable**:
- Explaining fundamental concepts (algorithms, patterns)
- Historical context for design decisions
- Understanding evolution of a technology
- Stable, mature technologies with infrequent changes

**Always Check**: Does the information still apply to the current version you're using?

---

## Handling Conflicting Information

### When Sources Disagree

**Common Scenarios**:
1. Official docs vs. community best practices
2. Older tutorial vs. newer official guidance
3. Different approaches recommended by different experts
4. Documentation vs. actual behavior (bugs)

**Resolution Strategy**:

**Step 1: Identify the Conflict**
```markdown
Document the conflicting claims:
- Source A says: [claim]
- Source B says: [contradictory claim]
- Conflict type: [Direct contradiction / Different approaches / Outdated info]
```

**Step 2: Check Source Hierarchy**
```markdown
- Which source is more authoritative? (Official > Community > Individual)
- Which source is more recent? (Prefer newer for changing tech)
- Which source is more specific to your context? (Version, platform)
```

**Step 3: Test Empirically**
```markdown
When possible, test both approaches:
1. Set up minimal test case
2. Try approach from Source A
3. Try approach from Source B
4. Document which works in your context
5. Document why (if discoverable)
```

**Step 4: Research Context**
```markdown
Look for version-specific differences:
- Did the API change between versions?
- Is one approach deprecated?
- Are there platform-specific differences?
- Is one approach a workaround for a bug since fixed?
```

**Step 5: Document the Resolution**
```markdown
Record what you discovered:
- Which approach you chose and why
- Why sources disagreed (if known)
- What testing revealed
- Conditions where each approach might be valid
```

### Official Docs vs. Reality

**Sometimes official documentation is wrong or outdated.** This happens.

**When Documentation Doesn't Match Behavior**:
1. **Test thoroughly**: Ensure you're using API correctly
2. **Check version**: Docs might be for different version
3. **Search issues**: Others may have reported the discrepancy
4. **File a bug**: If docs are wrong, help fix them
5. **Document workaround**: For your project's reference

**Document As**:
```markdown
## Known Documentation Issue

**Official docs claim**: [What docs say]
**Actual behavior**: [What actually happens]
**Versions affected**: [Your version]
**Source**: [Link to GitHub issue or test]
**Workaround**: [How you handled it]
**Tracking**: [Link to issue you filed or found]
```

---

## Version-Specific Research

### Matching Documentation to Your Version

**Critical Questions**:
- What version of the technology are you using?
- What version is the documentation for?
- Are there breaking changes between these versions?

**Version Checking Workflow**:

**Step 1: Identify Your Version**
```bash
# Package.json, requirements.txt, etc.
# Or runtime check:
node --version
python --version
react --version (from package)
```

**Step 2: Find Version-Specific Docs**
- Look for version switcher in docs (many modern doc sites have this)
- Check GitHub branch/tag for specific version
- Search for "v[X] documentation" or "[package] [version] docs"

**Step 3: Check Changelog**
- Read CHANGELOG.md or release notes
- Look for breaking changes between doc version and your version
- Note deprecations that affect your use case

**Step 4: Verify Examples Work**
```markdown
Test every code example you plan to use:
- [ ] Example runs without errors
- [ ] Example produces expected output
- [ ] Example uses APIs available in your version
- [ ] Example doesn't use deprecated features
```

### Migration Guides and Breaking Changes

**When Researching Upgrades**:

**Find Migration Documentation**:
- UPGRADING.md or MIGRATION.md in repo
- "Migrating from v[X] to v[Y]" guides
- Release notes for major versions
- Community migration guides and tools

**Document Migration Complexity**:
```markdown
## Upgrade Path: [Package] v[X] → v[Y]

**Breaking Changes**:
1. [Breaking change 1] - Impact: [High/Medium/Low]
   - What changed: [Description]
   - How to migrate: [Steps]
   - Estimated effort: [Hours/days]

**Deprecations**:
1. [Deprecated feature] - Removed in v[Z]
   - We use this: [Yes/No]
   - Replacement: [New API]
   - Migration priority: [High/Medium/Low]

**Migration Steps**:
1. [Step 1]
2. [Step 2]
...

**Estimated Migration Time**: [Time estimate]
**Risk Level**: [High/Medium/Low]
**Recommendation**: [Upgrade now / Defer / Plan for v[Z]]
```

---

## Specialized Source Evaluation

### Evaluating Security Information

**Security information is critical to get right.**

**Trusted Security Sources**:
- CVE database (cve.mitre.org)
- GitHub Security Advisories
- Official security mailing lists
- OWASP (Open Web Application Security Project)
- Vendor security bulletins
- Snyk, npm audit, or similar tools

**Verification Requirements**:
```markdown
For any security claim:
- [ ] CVE ID provided (if vulnerability)
- [ ] Versions affected clearly specified
- [ ] Severity rating included (CVSS score)
- [ ] Patch or mitigation available
- [ ] Verified in official security advisory
- [ ] Tested mitigation in your environment
```

**Red Flags for Security Info**:
- Vague claims without CVE reference
- Severity not specified
- No mitigation guidance
- Can't verify with official sources
- Spread via social media without official confirmation

**Always**: Verify security claims with official sources before acting.

### Evaluating Performance Claims

**Performance benchmarks require scrutiny.**

**Trustworthy Benchmarks**:
- Official benchmarks from project maintainers
- Third-party benchmarks with methodology published
- Benchmarks you can reproduce
- Benchmarks with version and environment details

**Benchmark Evaluation Checklist**:
```markdown
- [ ] Benchmark methodology described
- [ ] Hardware/environment specifications provided
- [ ] Software versions specified
- [ ] Benchmark code is available
- [ ] Results are reproducible
- [ ] Multiple runs averaged (not cherry-picked)
- [ ] Compared fairly (same task, similar config)
```

**Questions to Ask**:
- Is this a synthetic benchmark or real-world workload?
- What specific use case does this measure?
- Are the conditions comparable to your use case?
- Who ran the benchmark? (Vendor benchmarks may be biased)
- Can you reproduce the results?

**Red Flags**:
- No methodology provided
- Missing version or environment details
- Results too good to be true
- Vendor benchmark without third-party validation
- Cherry-picked best-case scenarios

**Best Practice**: Run your own benchmarks for critical performance requirements.

---

## Documentation Quality Assessment

### Evaluating Official Documentation

**Even official docs vary in quality.**

**High-Quality Official Docs**:
- Clear getting started guide
- Comprehensive API reference
- Architecture and concepts explanation
- Migration guides between versions
- Active maintenance (recent updates)
- Searchable and well-organized
- Code examples that work
- Community contribution process

**Warning Signs in Official Docs**:
- Last updated >1 year ago
- Broken links or missing pages
- Code examples don't work
- No version switcher (older projects)
- Incomplete API coverage
- No search functionality
- Poor organization or navigation

**When Official Docs Are Poor**:
1. Rely more heavily on source code
2. Search GitHub issues for clarification
3. Join official community forums/chat
4. Read test suites for API examples
5. Consider if poor docs indicate poor maintenance

---

## Cross-Verification Strategies

### Multi-Source Verification

**For Critical Information, Use Multiple Sources**:

**Verification Levels**:

**Level 1 - Single Source** (Low Confidence):
- One blog post or tutorial
- Unverified Stack Overflow answer
- Single comment in an issue

**Level 2 - Dual Verification** (Medium Confidence):
- Official docs + community confirmation
- Multiple Stack Overflow answers agreeing
- Tutorial + successful personal testing

**Level 3 - Triple Verification** (High Confidence):
- Official docs + community sources + personal testing
- Multiple official sources (docs, issue, release notes)
- Official docs + source code inspection + working example

**Level 4 - Authoritative** (Highest Confidence):
- Official docs + tested in your environment + community consensus
- Direct communication with maintainers
- Specification or RFC + reference implementation

**Verification Template**:
```markdown
## Claim: [Statement to verify]

### Source 1 (Official Docs)
- Says: [Summary]
- Link: [URL]
- Date: [When accessed]

### Source 2 (Community)
- Says: [Summary]
- Link: [URL]
- Date: [When accessed]

### Source 3 (Testing)
- Test: [What you tested]
- Result: [What happened]
- Date: [When tested]

### Confidence Level: [Low/Medium/High/Authoritative]
### Decision: [Proceed / Defer / Reject]
```

---

## Source Documentation Best Practices

### Recording Source Information

**For Every Source You Use, Record**:

```markdown
## Source Record

**Title**: [Article/doc title]
**URL**: [Full URL]
**Author**: [Name or organization]
**Date Published**: [Original date]
**Date Accessed**: [When you accessed it]
**Last Updated**: [If shown]
**Version**: [Software version discussed]
**Credibility Tier**: [1/2/3/4]
**Confidence Level**: [High/Medium/Low]

**Key Information Extracted**:
- [Point 1]
- [Point 2]

**Verification Status**:
- [ ] Cross-referenced with official docs
- [ ] Code examples tested
- [ ] Information confirmed by other sources

**Notes**:
[Any context, caveats, or additional observations]
```

### Organizing Research Sources

**File Structure**:
```
docs/preparation/
├── sources/
│   ├── official-sources.md       # Tier 1 sources
│   ├── community-sources.md      # Tier 2 sources
│   ├── secondary-sources.md      # Tier 3 sources
│   └── source-evaluation-log.md  # Verification decisions
```

**Source Tracking Template**:
```markdown
# Research Sources Log

## Official Sources (Tier 1)

| Title | URL | Date Accessed | Version | Key Info | Verified |
|-------|-----|---------------|---------|----------|----------|
| [Title] | [URL] | [Date] | [Version] | [Summary] | ✅ |

## Community Sources (Tier 2)

| Title | Author | URL | Date | Verified Against | Confidence |
|-------|--------|-----|------|------------------|------------|
| [Title] | [Name] | [URL] | [Date] | [Official source] | Medium |

## Secondary Sources (Tier 3)

| Title | URL | Date | Tested | Issues Found | Use? |
|-------|-----|------|--------|--------------|------|
| [Title] | [URL] | [Date] | ✅ | [Problems] | ⚠️ Partial |

## Excluded Sources

| Title | URL | Reason for Exclusion |
|-------|-----|---------------------|
| [Title] | [URL] | Outdated (2019), contradicts v5 docs |
```

---

## Quality Assurance Checklist

Before finalizing research based on sources:

**Source Quality**:
- [ ] Primary sources are official and current
- [ ] Secondary sources verified against official docs
- [ ] All sources documented with dates and versions
- [ ] Conflicting information resolved and documented
- [ ] Author credibility assessed for non-official sources

**Information Quality**:
- [ ] Version-specific information verified
- [ ] Code examples tested and working
- [ ] Claims supported by multiple sources or testing
- [ ] Security information verified with official advisories
- [ ] Performance claims supported by reproducible benchmarks

**Documentation Quality**:
- [ ] All sources cited with complete information
- [ ] Confidence levels assigned to findings
- [ ] Assumptions and limitations clearly stated
- [ ] Verification steps documented
- [ ] Update process established for living documents

---

## Summary

Source evaluation is a critical skill for effective research. By systematically assessing credibility, verifying claims, and documenting your evaluation process, you ensure that architectural and implementation decisions are based on reliable, accurate information.

**Key Principles**:
- **Hierarchy of Trust**: Official > Community > Secondary > Unverified
- **Verify Claims**: Test examples, cross-reference multiple sources
- **Check Timeliness**: Ensure information applies to your version
- **Document Everything**: Record sources, evaluation, and verification
- **When in Doubt, Test**: Empirical verification beats assumptions

**Red Flags to Watch For**:
- Outdated information without version context
- Claims without sources or evidence
- Contradictions with official documentation
- Anonymous or unverifiable authors
- Code examples that don't work
- Absolute statements without caveats

**Trust, but Verify**: Even official sources can be outdated or wrong. Always test critical information in your environment.
