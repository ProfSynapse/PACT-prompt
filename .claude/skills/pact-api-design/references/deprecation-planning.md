# API Deprecation Planning

Comprehensive guide to deprecation timeline strategies, communication plans, and stakeholder management for API deprecation.

## Table of Contents

1. [Deprecation Overview](#deprecation-overview)
2. [Communication Strategies](#communication-strategies)
3. [Sunset Timelines](#sunset-timelines)
4. [Monitoring and Tracking](#monitoring-and-tracking)
5. [Enterprise Considerations](#enterprise-considerations)
6. [Quick Reference](#quick-reference)

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

## Communication Strategies

### 1. Announcement Channels

Use multiple channels to maximize reach:

**Email Notifications**:
```
Subject: [Action Required] API v1 Deprecation - Migrate by June 2025

Dear Developer,

We're writing to inform you that API v1 will be deprecated effective
December 6, 2025, with full removal on June 1, 2026.

What's changing:
- v1 endpoints will return deprecation warnings starting Dec 6, 2025
- v1 will be sunset (read-only) on April 1, 2026
- v1 will be completely removed on June 1, 2026

Action required:
- Migrate to v2 API before June 1, 2026
- Review migration guide: https://api.example.com/docs/v1-to-v2
- Test v2 in staging: https://staging-api.example.com/v2

Need help? Contact api-support@example.com
```

**Developer Portal Banner**:
```html
⚠️ API v1 is deprecated and will be removed on June 1, 2026.
Migrate to v2 now: [Migration Guide] [Contact Support]
```

**Changelog Entry**:
```markdown
## 2025-12-06 - API v1 Deprecation Announced

**Breaking Change**: API v1 is officially deprecated and will be removed.

**Timeline**:
- Dec 6, 2025: Deprecation warnings added to all v1 responses
- Apr 1, 2026: v1 becomes read-only (POST/PUT/DELETE disabled)
- Jun 1, 2026: v1 completely removed, returns 410 Gone

**Migration**: See [v1 to v2 Migration Guide](link)
**Questions**: Contact api-support@example.com
```

**In-App Notifications** (for dashboard/console):
```typescript
interface DeprecationNotice {
  id: string;
  severity: 'warning' | 'critical';
  title: string;
  message: string;
  action_url: string;
  dismissible: boolean;
  expires_at: string;
}

const notice: DeprecationNotice = {
  id: 'api-v1-deprecation',
  severity: 'critical',
  title: 'API v1 Deprecation',
  message: 'Your application is using deprecated API v1. Migrate to v2 by June 2026.',
  action_url: 'https://api.example.com/docs/migration',
  dismissible: false,
  expires_at: '2026-06-01T00:00:00Z'
};
```

### 2. Documentation Practices

**API Reference Updates**:
```markdown
# GET /api/v1/users

⚠️ **DEPRECATED**: This endpoint is deprecated as of December 6, 2025
and will be removed on June 1, 2026.

**Migration**: Use [GET /api/v2/users](link) instead.

**Breaking Changes**:
- Response format changed from `name` to `firstName`/`lastName`
- Date fields now use ISO 8601 format
- Added required `Accept: application/json` header

[See Migration Guide →](link)
```

**Visual Indicators**:
```markdown
# API Endpoints

## User Management

- ✅ GET /api/v2/users - List users (current)
- ⚠️ GET /api/v1/users - List users (deprecated, sunset Jun 2026)
- ❌ GET /api/legacy/users - Legacy endpoint (removed)
```

**Migration Guide Structure**:
```markdown
# API v1 to v2 Migration Guide

## Overview
- Timeline and dates
- Summary of breaking changes
- Benefits of upgrading

## Breaking Changes Detail
For each breaking change:
- What changed
- Why it changed
- v1 example (before)
- v2 example (after)
- Code diff

## Step-by-Step Migration
1. Update authentication
2. Update endpoint URLs
3. Update request formats
4. Update response parsing
5. Test in staging
6. Deploy to production

## Testing Checklist
- [ ] All v1 endpoints replaced with v2
- [ ] Authentication working
- [ ] Response parsing updated
- [ ] Error handling covers v2 error format
- [ ] Tested in staging environment

## Common Issues
Q: Why is my auth failing?
A: v2 requires OAuth2, not API keys...

## Support
- Documentation: link
- Email: support@example.com
- Office hours: Tuesdays 2-4pm PST
```

### 3. Response-Embedded Warnings

Include deprecation information directly in API responses:

**TypeScript Implementation**:
```typescript
interface DeprecationMetadata {
  deprecated: boolean;
  sunset_date: string;
  removal_date: string;
  migration_guide: string;
  successor_version?: string;
  successor_url?: string;
  contact_email: string;
}

interface APIResponse<T> {
  data: T;
  meta?: {
    deprecation?: DeprecationMetadata;
    pagination?: object;
  };
}

// Middleware to add deprecation metadata
function addDeprecationWarning(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const isV1 = req.path.startsWith('/api/v1');

  if (isV1) {
    const originalJson = res.json.bind(res);
    res.json = function(body: any) {
      const wrappedBody: APIResponse<any> = {
        data: body,
        meta: {
          deprecation: {
            deprecated: true,
            sunset_date: '2026-04-01T00:00:00Z',
            removal_date: '2026-06-01T00:00:00Z',
            migration_guide: 'https://api.example.com/docs/v1-to-v2',
            successor_version: 'v2',
            successor_url: req.path.replace('/v1/', '/v2/'),
            contact_email: 'api-support@example.com'
          }
        }
      };
      return originalJson(wrappedBody);
    };
  }

  next();
}

app.use(addDeprecationWarning);
```

**Python (FastAPI) Implementation**:
```python
from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class DeprecationMetadata(BaseModel):
    deprecated: bool
    sunset_date: datetime
    removal_date: datetime
    migration_guide: str
    successor_version: Optional[str] = None
    successor_url: Optional[str] = None
    contact_email: str

class APIResponseMeta(BaseModel):
    deprecation: Optional[DeprecationMetadata] = None

class APIResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[APIResponseMeta] = None

# Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class DeprecationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith('/api/v1'):
            # Add deprecation headers
            response.headers['Deprecation'] = 'true'
            response.headers['Sunset'] = 'Wed, 01 Apr 2026 00:00:00 GMT'
            response.headers['Link'] = (
                '</api/v2>; rel="successor-version", '
                '<https://api.example.com/docs/v1-to-v2>; rel="deprecation"'
            )

        return response

app.add_middleware(DeprecationMiddleware)
```

## Sunset Timelines

### Recommended Timeline

**Standard Timeline (6-12 months)**:
```
Month 0:  Announce deprecation
Month 1:  Add deprecation warnings to responses
Month 2:  Email all active users
Month 3:  Migration guide published
Month 4:  Office hours for migration support
Month 5:  Final reminder emails
Month 6:  Sunset mode (read-only)
Month 9:  Final warning
Month 12: Complete removal
```

**Aggressive Timeline (3-6 months)** for security or critical issues:
```
Week 0:   Announce deprecation
Week 2:   Add deprecation warnings
Week 4:   Migration guide published
Week 8:   Sunset mode (read-only)
Week 12:  Complete removal
```

**Enterprise Timeline (12-24 months)** for large customer base:
```
Quarter 1: Announce, early access to v2
Quarter 2: Deprecation warnings, migration guides
Quarter 3: Migration tooling, support programs
Quarter 4: Sunset warnings increase
Quarter 5: Sunset mode (read-only)
Quarter 6: Extension for enterprise customers
Quarter 8: Complete removal
```

### Minimum Notice Periods by API Type

| API Type | Minimum Notice | Recommended Notice |
|----------|----------------|-------------------|
| Internal APIs | 1 month | 3 months |
| Partner APIs | 3 months | 6 months |
| Public APIs | 6 months | 12 months |
| Critical Infrastructure APIs | 12 months | 24 months |

### Timeline Configuration

**TypeScript**:
```typescript
interface DeprecationTimeline {
  announcement_date: Date;
  deprecation_warning_date: Date;
  migration_guide_date: Date;
  sunset_date: Date;
  removal_date: Date;
  grace_period_end_date?: Date; // For enterprise customers
}

const timelines: Record<string, DeprecationTimeline> = {
  v1: {
    announcement_date: new Date('2025-12-06'),
    deprecation_warning_date: new Date('2026-01-06'),
    migration_guide_date: new Date('2025-12-15'),
    sunset_date: new Date('2026-04-01'),
    removal_date: new Date('2026-06-01'),
    grace_period_end_date: new Date('2026-09-01') // +3 months for enterprise
  }
};

function getTimelineStatus(version: string): string {
  const timeline = timelines[version];
  const now = new Date();

  if (now < timeline.announcement_date) {
    return 'Active';
  } else if (now < timeline.deprecation_warning_date) {
    return 'Deprecation Announced';
  } else if (now < timeline.sunset_date) {
    return 'Deprecated';
  } else if (now < timeline.removal_date) {
    return 'Sunset (Read-Only)';
  } else if (timeline.grace_period_end_date && now < timeline.grace_period_end_date) {
    return 'Removed (Enterprise Grace Period)';
  } else {
    return 'Removed';
  }
}
```

### Enterprise Grace Periods

For enterprise customers who need additional time:

**Configuration**:
```typescript
interface EnterpriseException {
  customer_id: string;
  customer_name: string;
  extended_sunset_date: Date;
  justification: string;
  approved_by: string;
  migration_plan_url: string;
}

const enterpriseExceptions: EnterpriseException[] = [
  {
    customer_id: 'enterprise-123',
    customer_name: 'ACME Corp',
    extended_sunset_date: new Date('2026-09-01'),
    justification: 'Complex integration with legacy systems',
    approved_by: 'api-team@example.com',
    migration_plan_url: 'https://docs.example.com/migrations/acme-corp'
  }
];

function hasEnterpriseException(customerId: string, version: string): boolean {
  const exception = enterpriseExceptions.find(e =>
    e.customer_id === customerId
  );

  if (!exception) return false;

  const now = new Date();
  return now < exception.extended_sunset_date;
}

// Middleware
function enterpriseExceptionMiddleware(req: Request, res: Response, next: NextFunction) {
  const customerId = req.user?.customerId;
  const version = extractVersion(req);

  if (hasEnterpriseException(customerId, version)) {
    // Allow access beyond normal sunset date
    console.log(`Enterprise exception granted for ${customerId}`);
    return next();
  }

  // Apply normal version state checks
  versionStateMiddleware(req, res, next);
}
```

## Monitoring and Tracking

### 1. Usage Tracking

**Logging Deprecated API Usage**:
```typescript
import { Logger } from './logger';

interface DeprecatedAPILog {
  timestamp: Date;
  version: string;
  endpoint: string;
  method: string;
  user_id?: string;
  customer_id?: string;
  ip_address: string;
  user_agent: string;
}

function logDeprecatedUsage(req: Request) {
  const log: DeprecatedAPILog = {
    timestamp: new Date(),
    version: extractVersion(req),
    endpoint: req.path,
    method: req.method,
    user_id: req.user?.id,
    customer_id: req.user?.customerId,
    ip_address: req.ip,
    user_agent: req.headers['user-agent'] || 'unknown'
  };

  Logger.warn('Deprecated API usage', log);

  // Send to analytics
  analytics.track('deprecated_api_usage', log);
}

// Middleware
function deprecatedUsageLoggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const version = extractVersion(req);
  const config = getVersionState(version);

  if (config.state === APIVersionState.DEPRECATED ||
      config.state === APIVersionState.SUNSET) {
    logDeprecatedUsage(req);
  }

  next();
}
```

**Python (FastAPI)**:
```python
import logging
from datetime import datetime
from starlette.requests import Request

logger = logging.getLogger(__name__)

async def log_deprecated_usage(request: Request, version: str):
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'version': version,
        'endpoint': request.url.path,
        'method': request.method,
        'user_id': getattr(request.state, 'user_id', None),
        'customer_id': getattr(request.state, 'customer_id', None),
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent', 'unknown')
    }

    logger.warning('Deprecated API usage', extra=log_data)

    # Send to analytics
    await analytics.track('deprecated_api_usage', log_data)
```

### 2. Analytics and Dashboards

**Metrics to Track**:
- Total deprecated API calls per day/week/month
- Unique users/customers still using deprecated API
- Breakdown by endpoint
- Geographic distribution
- Client type (mobile, web, server)
- Trend over time (increasing or decreasing usage)

**SQL Query for Usage Report**:
```sql
-- Find customers still using v1 API
SELECT
  customer_id,
  customer_name,
  COUNT(*) as request_count,
  COUNT(DISTINCT endpoint) as unique_endpoints,
  MAX(timestamp) as last_used,
  MIN(timestamp) as first_used
FROM deprecated_api_logs
WHERE version = 'v1'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY customer_id, customer_name
ORDER BY request_count DESC;

-- Endpoint usage breakdown
SELECT
  endpoint,
  COUNT(*) as request_count,
  COUNT(DISTINCT customer_id) as unique_customers
FROM deprecated_api_logs
WHERE version = 'v1'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY endpoint
ORDER BY request_count DESC;

-- Daily usage trend
SELECT
  DATE(timestamp) as date,
  COUNT(*) as request_count,
  COUNT(DISTINCT customer_id) as unique_customers
FROM deprecated_api_logs
WHERE version = 'v1'
  AND timestamp > NOW() - INTERVAL '90 days'
GROUP BY DATE(timestamp)
ORDER BY date;
```

### 3. Identifying Stuck Consumers

**Finding Users Who Haven't Migrated**:
```typescript
interface StuckConsumer {
  customer_id: string;
  customer_name: string;
  email: string;
  v1_requests_last_30_days: number;
  last_v1_usage: Date;
  has_used_v2: boolean;
  days_until_sunset: number;
}

async function findStuckConsumers(): Promise<StuckConsumer[]> {
  const sql = `
    WITH v1_usage AS (
      SELECT
        customer_id,
        COUNT(*) as v1_count,
        MAX(timestamp) as last_v1_usage
      FROM deprecated_api_logs
      WHERE version = 'v1'
        AND timestamp > NOW() - INTERVAL '30 days'
      GROUP BY customer_id
    ),
    v2_usage AS (
      SELECT DISTINCT customer_id
      FROM api_logs
      WHERE version = 'v2'
        AND timestamp > NOW() - INTERVAL '30 days'
    )
    SELECT
      c.customer_id,
      c.customer_name,
      c.email,
      v1.v1_count as v1_requests_last_30_days,
      v1.last_v1_usage,
      CASE WHEN v2.customer_id IS NOT NULL THEN true ELSE false END as has_used_v2,
      EXTRACT(DAY FROM (DATE '2026-06-01' - CURRENT_DATE)) as days_until_sunset
    FROM customers c
    JOIN v1_usage v1 ON c.customer_id = v1.customer_id
    LEFT JOIN v2_usage v2 ON c.customer_id = v2.customer_id
    WHERE v1.v1_count > 100  -- Active users
    ORDER BY v1.v1_count DESC;
  `;

  return db.query(sql);
}
```

### 4. Outreach Strategies

**Automated Email Campaign**:
```typescript
interface EmailTemplate {
  subject: string;
  body: string;
}

const emailTemplates: Record<string, EmailTemplate> = {
  initial_notice: {
    subject: 'Action Required: Migrate from API v1 to v2',
    body: `
      Hi {{customer_name}},

      We noticed you're still using API v1, which will be removed on June 1, 2026.

      Your usage: {{v1_requests}} requests in the last 30 days
      Time remaining: {{days_until_sunset}} days

      Migration resources:
      - Migration guide: {{migration_guide_url}}
      - Support: {{support_email}}

      Let us know if you need help!
    `
  },

  final_warning: {
    subject: 'URGENT: API v1 Removal in 30 Days',
    body: `
      Hi {{customer_name}},

      This is a final reminder that API v1 will be removed in 30 days.

      Your application is still making {{v1_requests}} requests to v1.

      IMMEDIATE ACTION REQUIRED to avoid service disruption.

      Priority support available: {{support_email}}
    `
  },

  migration_success: {
    subject: 'Congratulations! API v2 Migration Complete',
    body: `
      Hi {{customer_name}},

      Great news! We haven't detected any v1 API usage from your account
      in the last 7 days.

      Your migration to v2 is complete. Thank you for upgrading!

      Questions about v2? Contact {{support_email}}
    `
  }
};

async function sendDeprecationEmails() {
  const stuckConsumers = await findStuckConsumers();

  for (const consumer of stuckConsumers) {
    let template: EmailTemplate;

    if (consumer.days_until_sunset <= 30) {
      template = emailTemplates.final_warning;
    } else if (!consumer.has_used_v2) {
      template = emailTemplates.initial_notice;
    } else {
      continue; // Skip if already using v2
    }

    await emailService.send({
      to: consumer.email,
      subject: template.subject,
      body: renderTemplate(template.body, consumer)
    });

    console.log(`Sent ${template.subject} to ${consumer.customer_name}`);
  }
}

// Run daily
cron.schedule('0 9 * * *', sendDeprecationEmails);
```

**Personalized Outreach for High-Value Customers**:
```typescript
async function personalizedOutreach() {
  const highValueCustomers = await db.query(`
    SELECT c.*, v1.v1_count
    FROM customers c
    JOIN (
      SELECT customer_id, COUNT(*) as v1_count
      FROM deprecated_api_logs
      WHERE version = 'v1'
        AND timestamp > NOW() - INTERVAL '30 days'
      GROUP BY customer_id
    ) v1 ON c.customer_id = v1.customer_id
    WHERE c.plan = 'enterprise'
      AND v1.v1_count > 10000
  `);

  for (const customer of highValueCustomers) {
    // Assign dedicated migration specialist
    await assignMigrationSpecialist(customer);

    // Schedule call
    await scheduleOutreachCall(customer);

    // Create custom migration plan
    await createMigrationPlan(customer);

    console.log(`Personalized outreach initiated for ${customer.customer_name}`);
  }
}
```

## Enterprise Considerations

### 1. SLA Commitments

For customers with SLA agreements:

```typescript
interface SLACommitment {
  customer_id: string;
  minimum_notice_days: number;
  requires_approval_for_breaking_changes: boolean;
  dedicated_support: boolean;
  custom_timeline_allowed: boolean;
}

const slaCommitments: Map<string, SLACommitment> = new Map([
  ['enterprise-123', {
    customer_id: 'enterprise-123',
    minimum_notice_days: 365, // 1 year
    requires_approval_for_breaking_changes: true,
    dedicated_support: true,
    custom_timeline_allowed: true
  }]
]);

function validateDeprecationTimeline(
  customerId: string,
  deprecationDate: Date,
  removalDate: Date
): boolean {
  const sla = slaCommitments.get(customerId);
  if (!sla) return true; // No SLA, standard timeline applies

  const daysDiff = (removalDate.getTime() - deprecationDate.getTime()) / (1000 * 60 * 60 * 24);

  if (daysDiff < sla.minimum_notice_days) {
    console.error(
      `SLA violation: ${customerId} requires ${sla.minimum_notice_days} days notice, ` +
      `only ${daysDiff} days provided`
    );
    return false;
  }

  return true;
}
```

### 2. Dedicated Migration Support

**Migration Support Program**:
```typescript
interface MigrationSupportPackage {
  customer_id: string;
  dedicated_engineer: string;
  office_hours_slots: number;
  custom_tooling: boolean;
  priority_support: boolean;
  migration_deadline_extension: number; // days
}

async function enrollInMigrationSupport(customerId: string): Promise<MigrationSupportPackage> {
  const customer = await getCustomer(customerId);

  const supportPackage: MigrationSupportPackage = {
    customer_id: customerId,
    dedicated_engineer: await assignDedicatedEngineer(customer),
    office_hours_slots: customer.plan === 'enterprise' ? 10 : 3,
    custom_tooling: customer.plan === 'enterprise',
    priority_support: true,
    migration_deadline_extension: customer.plan === 'enterprise' ? 90 : 30
  };

  await db.insert('migration_support_packages', supportPackage);

  return supportPackage;
}
```

## Quick Reference

### Deprecation Checklist

- [ ] **Announce Deprecation**
  - [ ] Email all active users
  - [ ] Update developer portal with banner
  - [ ] Post to changelog and blog
  - [ ] Notify support team

- [ ] **Create Migration Resources**
  - [ ] Write comprehensive migration guide
  - [ ] Provide code examples for v1 → v2
  - [ ] Create migration scripts/tools
  - [ ] Set up migration support email/channel

- [ ] **Monitor Usage**
  - [ ] Log all deprecated API usage
  - [ ] Create analytics dashboard
  - [ ] Identify stuck consumers
  - [ ] Track migration progress

- [ ] **Communicate Timeline**
  - [ ] Send monthly reminder emails
  - [ ] Escalate urgency as deadline approaches
  - [ ] Provide personalized outreach for high-value customers
  - [ ] Offer migration support programs

### Timeline Templates

**Standard Timeline (6-12 months)**:
- Month 0: Announce
- Month 1: Add warnings
- Month 3: Migration guide
- Month 6: Sunset (read-only)
- Month 12: Removal

**Aggressive Timeline (3-6 months)**:
- Week 0: Announce
- Week 2: Add warnings
- Week 8: Sunset
- Week 12: Removal

**Enterprise Timeline (12-24 months)**:
- Quarter 1: Announce
- Quarter 2: Migration support
- Quarter 5: Sunset
- Quarter 8: Removal (with exceptions)

### Communication Channels

1. Email notifications (primary)
2. Developer portal banners
3. Changelog/blog posts
4. In-app notifications
5. Support channel announcements
6. SMS for urgent final warnings (enterprise)

### Migration Support

- Comprehensive migration guides
- Code examples and diffs
- Automated migration scripts
- Office hours for support
- Dedicated engineers for enterprise
- Extended timelines for SLA customers
