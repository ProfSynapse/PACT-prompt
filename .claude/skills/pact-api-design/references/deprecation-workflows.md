# API Deprecation Workflows

Overview guide to API deprecation strategies, implementation, and migration. This document provides a high-level introduction to the deprecation process and links to detailed guides for each phase.

## Table of Contents

1. [Deprecation Overview](#deprecation-overview)
2. [The Three Phases of Deprecation](#the-three-phases-of-deprecation)
3. [Quick Start Guide](#quick-start-guide)
4. [Detailed Guides](#detailed-guides)

## Deprecation Overview

### What is API Deprecation?

API deprecation is the formal process of marking an API version, endpoint, or feature as obsolete while providing:
- Clear communication about what's changing
- Timeline for when changes take effect
- Migration path to replacement functionality
- Support during transition period

### Why Deprecate APIs?

APIs need deprecation to:
- Remove outdated or poorly designed features
- Clean up technical debt
- Improve security by removing vulnerable endpoints
- Consolidate redundant functionality
- Evolve toward better architecture
- Reduce maintenance burden

### Deprecation vs Sunset vs Removal

| Term | Definition | Example |
|------|------------|---------|
| **Deprecation** | Mark as obsolete, discourage use | "v1 API is deprecated, migrate to v2" |
| **Sunset** | Set end-of-life date | "v1 will be removed on 2025-12-01" |
| **Removal** | Completely disable access | "v1 returns 410 Gone after 2025-12-01" |

**Timeline**: Deprecation → Sunset Date Announced → Grace Period → Removal

## The Three Phases of Deprecation

### Phase 1: Planning (Months 0-3)

**Focus**: Communication and timeline establishment

**Key Activities**:
- Announce deprecation across all channels
- Create comprehensive migration documentation
- Set sunset and removal dates
- Establish support channels
- Monitor usage and identify affected customers

**Outputs**:
- Deprecation announcement
- Migration guide
- Timeline with key dates
- Support plan

**See**: [deprecation-planning.md](./deprecation-planning.md) for detailed planning strategies, communication templates, monitoring approaches, and enterprise considerations.

### Phase 2: Implementation (Ongoing)

**Focus**: Technical implementation of deprecation indicators

**Key Activities**:
- Add HTTP deprecation headers (Deprecation, Sunset, Link)
- Implement version lifecycle state management
- Add code annotations and runtime warnings
- Configure feature flags for gradual rollout
- Set up monitoring and analytics

**Outputs**:
- Deprecation headers on all deprecated endpoints
- Version state machine (Active → Deprecated → Sunset → Removed)
- Code annotations and warnings
- Usage tracking and dashboards

**See**: [deprecation-implementation.md](./deprecation-implementation.md) for technical implementation details, code examples, and state management patterns.

### Phase 3: Migration (Months 3-12)

**Focus**: Customer migration and support

**Key Activities**:
- Provide comprehensive migration guides
- Create compatibility layers and adapters
- Build automated migration tooling
- Offer migration support programs
- Track migration progress

**Outputs**:
- Step-by-step migration guide
- Compatibility wrappers/proxies
- Automated migration scripts
- Migration progress tracking
- Customer support resources

**See**: [deprecation-migration.md](./deprecation-migration.md) for migration strategies, compatibility patterns, automated tooling, and client support approaches.

## Quick Start Guide

### Step 1: Plan the Deprecation (Week 1)

1. **Define the scope**:
   - What is being deprecated? (version, endpoint, feature)
   - Why is it being deprecated?
   - What is the replacement?

2. **Set the timeline**:
   ```
   Standard Timeline (6-12 months):
   - Month 0:  Announce deprecation
   - Month 1:  Add deprecation warnings
   - Month 3:  Migration guide published
   - Month 6:  Sunset mode (read-only)
   - Month 12: Complete removal
   ```

3. **Communicate the plan**:
   - Email all active users
   - Update developer portal
   - Post to changelog
   - Notify support team

**See**: [deprecation-planning.md](./deprecation-planning.md) for timeline templates and communication strategies.

### Step 2: Implement Deprecation Indicators (Week 2-3)

1. **Add HTTP headers**:
   ```http
   Deprecation: true
   Sunset: Mon, 01 Jun 2026 00:00:00 GMT
   Link: </api/v2>; rel="successor-version"
   ```

2. **Configure version states**:
   ```typescript
   const versionConfigs = {
     v1: {
       state: 'deprecated',
       sunset_date: new Date('2026-06-01'),
       successor: 'v2'
     }
   };
   ```

3. **Add monitoring**:
   - Log all deprecated API usage
   - Track unique users/customers
   - Monitor migration progress

**See**: [deprecation-implementation.md](./deprecation-implementation.md) for complete implementation examples.

### Step 3: Support Migration (Weeks 4-52)

1. **Create migration guide**:
   - List breaking changes
   - Provide before/after code examples
   - Include step-by-step instructions
   - Document common issues

2. **Build migration tools**:
   - Detection scripts to find v1 usage
   - Automated migration scripts
   - Progress tracking tools

3. **Provide support**:
   - Migration support email/channel
   - Office hours for questions
   - Dedicated engineers for enterprise customers

**See**: [deprecation-migration.md](./deprecation-migration.md) for migration guide templates and tooling examples.

### Step 4: Monitor and Enforce (Ongoing)

1. **Track migration progress**:
   ```sql
   SELECT
     COUNT(DISTINCT customer_id) as total_customers,
     SUM(CASE WHEN last_v1_usage IS NULL THEN 1 ELSE 0 END) as migrated_customers
   FROM customer_migration_status;
   ```

2. **Send reminders**:
   - Monthly emails to customers still on v1
   - Escalate urgency as deadline approaches
   - Personalized outreach for high-value customers

3. **Enforce sunset**:
   - Read-only mode at sunset date
   - Complete removal at end date
   - Enterprise grace periods as needed

**See**: [deprecation-planning.md](./deprecation-planning.md) for monitoring and outreach strategies.

## Detailed Guides

### [Deprecation Planning](./deprecation-planning.md)
Comprehensive guide to planning and communicating API deprecation:
- **Communication strategies**: Multi-channel announcement, documentation practices, embedded warnings
- **Sunset timelines**: Standard, aggressive, and enterprise timelines with minimum notice periods
- **Monitoring and tracking**: Usage logging, analytics dashboards, identifying stuck consumers
- **Enterprise considerations**: SLA commitments, dedicated support, grace periods
- **Outreach strategies**: Automated campaigns, personalized support, migration success tracking

**Use when**: Planning a deprecation, establishing timelines, creating communication plans, managing enterprise customers.

### [Deprecation Implementation](./deprecation-implementation.md)
Technical implementation guide for deprecation infrastructure:
- **HTTP headers**: Deprecation, Sunset, and Link headers with complete examples
- **Version lifecycle states**: State machine implementation (Active → Deprecated → Sunset → Removed)
- **Code annotations**: Documentation annotations and runtime warnings
- **Feature flags**: Gradual rollout and progressive migration
- **Complete examples**: End-to-end implementation with middleware and state management

**Use when**: Implementing deprecation headers, managing version states, adding runtime warnings, configuring feature flags.

### [Deprecation Migration](./deprecation-migration.md)
Comprehensive guide to customer migration support:
- **Migration guides**: Structure, step-by-step instructions, testing checklists, rollback plans
- **Compatibility layers**: Client-side wrappers, server-side proxies, version negotiation
- **Migration tooling**: Automated scripts, detection tools, progress tracking
- **Backward compatibility**: Dual-write patterns, field expansion, gradual rollout
- **Complete workflow**: Phase-by-phase migration from detection to verification

**Use when**: Creating migration documentation, building compatibility layers, automating migration, supporting customers through migration.

## Quick Reference

### Deprecation Checklist

**Planning Phase**:
- [ ] Define scope and replacement
- [ ] Set timeline with key dates
- [ ] Announce deprecation across all channels
- [ ] Create comprehensive migration guide
- [ ] Set up support channels

**Implementation Phase**:
- [ ] Add HTTP deprecation headers
- [ ] Implement version state management
- [ ] Add code annotations and warnings
- [ ] Configure monitoring and analytics
- [ ] Set up feature flags for rollout

**Migration Phase**:
- [ ] Provide migration documentation
- [ ] Build automated migration tools
- [ ] Offer migration support programs
- [ ] Track migration progress
- [ ] Send regular reminders

**Enforcement Phase**:
- [ ] Enter read-only mode at sunset
- [ ] Complete removal at end date
- [ ] Monitor for errors and complaints
- [ ] Maintain compatibility for enterprise

### Timeline Templates

**Standard (6-12 months)**:
- Month 0: Announce
- Month 1: Add warnings
- Month 6: Sunset
- Month 12: Removal

**Aggressive (3-6 months)**:
- Week 0: Announce
- Week 2: Add warnings
- Week 8: Sunset
- Week 12: Removal

**Enterprise (12-24 months)**:
- Quarter 1: Announce
- Quarter 2: Support
- Quarter 5: Sunset
- Quarter 8: Removal

### HTTP Headers

```http
Deprecation: true
Sunset: Mon, 01 Jun 2026 00:00:00 GMT
Link: </api/v2>; rel="successor-version"
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

### Error Codes

- **200 OK** + Deprecation headers: Deprecated but functional
- **403 Forbidden**: Sunset mode (read-only)
- **410 Gone**: Completely removed

### Communication Channels

1. Email notifications (primary)
2. Developer portal banners
3. Changelog/blog posts
4. In-app notifications
5. Support announcements
6. SMS for urgent warnings (enterprise)

### Support Resources

- Migration guides with code examples
- Automated migration scripts
- Office hours for questions
- Dedicated engineers for enterprise
- Extended timelines for SLA customers
- Compatibility layers/proxies
