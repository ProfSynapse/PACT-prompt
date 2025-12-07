# API Deprecation Workflows

Comprehensive guide to API deprecation strategies, communication patterns, sunset timelines, and migration best practices.

## Table of Contents

1. [Deprecation Overview](#deprecation-overview)
2. [Deprecation Communication](#deprecation-communication)
3. [HTTP Sunset and Deprecation Headers](#http-sunset-and-deprecation-headers)
4. [Version Lifecycle States](#version-lifecycle-states)
5. [Migration Paths](#migration-paths)
6. [Sunset Timelines](#sunset-timelines)
7. [Monitoring Deprecated Endpoints](#monitoring-deprecated-endpoints)
8. [Enterprise Considerations](#enterprise-considerations)
9. [Complete Deprecation Example](#complete-deprecation-example)
10. [Quick Reference](#quick-reference)

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

## Deprecation Communication

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

## HTTP Sunset and Deprecation Headers

### Standard Headers

**Deprecation Header** (RFC Draft):
```
Deprecation: true
```

Indicates the resource is deprecated but still functional.

**Sunset Header** (RFC 8594):
```
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
```

Indicates when the resource will become unavailable.

**Link Header**:
```
Link: </api/v2/users>; rel="successor-version"
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

Provides links to successor version and migration documentation.

### Complete Header Example

**TypeScript**:
```typescript
import { format } from 'date-fns';

function setDeprecationHeaders(
  res: Response,
  sunsetDate: Date,
  successorUrl: string,
  migrationGuideUrl: string
) {
  // Deprecation header
  res.set('Deprecation', 'true');

  // Sunset header (HTTP date format)
  const sunsetHttpDate = format(sunsetDate, 'EEE, dd MMM yyyy HH:mm:ss') + ' GMT';
  res.set('Sunset', sunsetHttpDate);

  // Link headers
  res.set('Link', [
    `<${successorUrl}>; rel="successor-version"`,
    `<${migrationGuideUrl}>; rel="deprecation"`
  ].join(', '));

  // Custom headers for machine-readable data
  res.set('X-API-Deprecation-Date', '2025-12-06T00:00:00Z');
  res.set('X-API-Sunset-Date', sunsetDate.toISOString());
  res.set('X-API-Removal-Date', sunsetDate.toISOString());
}

// Usage in route
app.get('/api/v1/users', (req, res) => {
  setDeprecationHeaders(
    res,
    new Date('2026-06-01T00:00:00Z'),
    '/api/v2/users',
    'https://api.example.com/docs/v1-to-v2'
  );

  const users = await getUsersV1();
  res.json(users);
});
```

**Python (FastAPI)**:
```python
from datetime import datetime
from email.utils import formatdate
from fastapi import Response

def set_deprecation_headers(
    response: Response,
    sunset_date: datetime,
    successor_url: str,
    migration_guide_url: str
):
    # Deprecation header
    response.headers['Deprecation'] = 'true'

    # Sunset header (HTTP date format)
    sunset_timestamp = sunset_date.timestamp()
    response.headers['Sunset'] = formatdate(sunset_timestamp, usegmt=True)

    # Link headers
    response.headers['Link'] = (
        f'<{successor_url}>; rel="successor-version", '
        f'<{migration_guide_url}>; rel="deprecation"'
    )

    # Custom headers
    response.headers['X-API-Deprecation-Date'] = '2025-12-06T00:00:00Z'
    response.headers['X-API-Sunset-Date'] = sunset_date.isoformat()
    response.headers['X-API-Removal-Date'] = sunset_date.isoformat()

# Usage
@app.get('/api/v1/users')
def get_users_v1(response: Response):
    set_deprecation_headers(
        response,
        datetime(2026, 6, 1),
        '/api/v2/users',
        'https://api.example.com/docs/v1-to-v2'
    )

    users = get_users_from_db()
    return users
```

### Client Detection of Deprecation

**TypeScript Client**:
```typescript
async function apiRequest(url: string): Promise<any> {
  const response = await fetch(url);

  // Check for deprecation
  if (response.headers.get('Deprecation') === 'true') {
    const sunsetDate = response.headers.get('Sunset');
    const successorLink = response.headers.get('Link')?.match(
      /<([^>]+)>; rel="successor-version"/
    )?.[1];

    console.warn(
      `⚠️ API endpoint ${url} is deprecated.`,
      `Sunset date: ${sunsetDate}`,
      `Migrate to: ${successorLink}`
    );

    // Optional: Track deprecation usage
    trackDeprecationUsage(url, sunsetDate);
  }

  return response.json();
}
```

**Python Client**:
```python
import requests
import logging

def api_request(url: str) -> dict:
    response = requests.get(url)

    # Check for deprecation
    if response.headers.get('Deprecation') == 'true':
        sunset_date = response.headers.get('Sunset')
        link_header = response.headers.get('Link', '')

        # Parse Link header for successor
        import re
        match = re.search(r'<([^>]+)>; rel="successor-version"', link_header)
        successor_url = match.group(1) if match else None

        logging.warning(
            f"⚠️ API endpoint {url} is deprecated. "
            f"Sunset date: {sunset_date}. "
            f"Migrate to: {successor_url}"
        )

        # Optional: Track deprecation usage
        track_deprecation_usage(url, sunset_date)

    return response.json()
```

## Version Lifecycle States

### State Definitions

| State | Description | Behavior |
|-------|-------------|----------|
| **Active** | Current, fully supported version | Full functionality, receives all updates |
| **Deprecated** | Discouraged but fully functional | Full functionality, only security updates |
| **Sunset** | End-of-life date announced | Read-only, no updates, removal pending |
| **Removed** | No longer available | Returns 410 Gone |

### State Transitions

```
Active → Deprecated → Sunset → Removed
   |         |           |         |
   |         |           |         └─ Returns 410 Gone
   |         |           └─ Read-only, removal date set
   |         └─ Deprecation warnings, migration encouraged
   └─ Full support
```

### Implementation with State Machine

**TypeScript**:
```typescript
enum APIVersionState {
  ACTIVE = 'active',
  DEPRECATED = 'deprecated',
  SUNSET = 'sunset',
  REMOVED = 'removed'
}

interface APIVersionConfig {
  version: string;
  state: APIVersionState;
  deprecation_date?: Date;
  sunset_date?: Date;
  removal_date?: Date;
  successor_version?: string;
}

const versionConfigs: Record<string, APIVersionConfig> = {
  v1: {
    version: 'v1',
    state: APIVersionState.SUNSET,
    deprecation_date: new Date('2025-12-06'),
    sunset_date: new Date('2026-04-01'),
    removal_date: new Date('2026-06-01'),
    successor_version: 'v2'
  },
  v2: {
    version: 'v2',
    state: APIVersionState.ACTIVE
  }
};

function getVersionState(version: string): APIVersionConfig {
  const config = versionConfigs[version];
  if (!config) {
    throw new Error(`Unknown version: ${version}`);
  }

  const now = new Date();

  // Update state based on dates
  if (config.removal_date && now >= config.removal_date) {
    config.state = APIVersionState.REMOVED;
  } else if (config.sunset_date && now >= config.sunset_date) {
    config.state = APIVersionState.SUNSET;
  } else if (config.deprecation_date && now >= config.deprecation_date) {
    config.state = APIVersionState.DEPRECATED;
  }

  return config;
}

// Middleware to enforce version state
function versionStateMiddleware(req: Request, res: Response, next: NextFunction) {
  const version = extractVersion(req); // e.g., 'v1' from /api/v1/users
  const config = getVersionState(version);

  switch (config.state) {
    case APIVersionState.REMOVED:
      return res.status(410).json({
        error: 'This API version has been removed',
        version: config.version,
        removal_date: config.removal_date,
        successor_version: config.successor_version,
        migration_guide: `https://api.example.com/docs/${version}-to-${config.successor_version}`
      });

    case APIVersionState.SUNSET:
      // Read-only mode: block write operations
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
        return res.status(403).json({
          error: 'This API version is in sunset mode (read-only)',
          version: config.version,
          removal_date: config.removal_date,
          message: 'Write operations disabled. Please migrate to ' + config.successor_version
        });
      }
      // Allow GET/HEAD for reads
      setDeprecationHeaders(res, config.sunset_date!, config.successor_version!);
      break;

    case APIVersionState.DEPRECATED:
      setDeprecationHeaders(res, config.sunset_date!, config.successor_version!);
      break;

    case APIVersionState.ACTIVE:
      // No special handling
      break;
  }

  next();
}
```

**Python (FastAPI)**:
```python
from enum import Enum
from datetime import datetime
from typing import Optional
from fastapi import Request, Response, HTTPException

class APIVersionState(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    REMOVED = "removed"

class APIVersionConfig:
    def __init__(
        self,
        version: str,
        state: APIVersionState,
        deprecation_date: Optional[datetime] = None,
        sunset_date: Optional[datetime] = None,
        removal_date: Optional[datetime] = None,
        successor_version: Optional[str] = None
    ):
        self.version = version
        self.state = state
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.removal_date = removal_date
        self.successor_version = successor_version

VERSION_CONFIGS = {
    'v1': APIVersionConfig(
        version='v1',
        state=APIVersionState.SUNSET,
        deprecation_date=datetime(2025, 12, 6),
        sunset_date=datetime(2026, 4, 1),
        removal_date=datetime(2026, 6, 1),
        successor_version='v2'
    ),
    'v2': APIVersionConfig(
        version='v2',
        state=APIVersionState.ACTIVE
    )
}

def get_version_state(version: str) -> APIVersionConfig:
    config = VERSION_CONFIGS.get(version)
    if not config:
        raise ValueError(f"Unknown version: {version}")

    now = datetime.now()

    # Update state based on dates
    if config.removal_date and now >= config.removal_date:
        config.state = APIVersionState.REMOVED
    elif config.sunset_date and now >= config.sunset_date:
        config.state = APIVersionState.SUNSET
    elif config.deprecation_date and now >= config.deprecation_date:
        config.state = APIVersionState.DEPRECATED

    return config

# Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class VersionStateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        version = self.extract_version(request.url.path)
        config = get_version_state(version)

        if config.state == APIVersionState.REMOVED:
            return Response(
                content={
                    'error': 'This API version has been removed',
                    'version': config.version,
                    'removal_date': config.removal_date.isoformat(),
                    'successor_version': config.successor_version
                },
                status_code=410,
                media_type='application/json'
            )

        if config.state == APIVersionState.SUNSET:
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return Response(
                    content={
                        'error': 'This API version is in sunset mode (read-only)',
                        'version': config.version,
                        'removal_date': config.removal_date.isoformat()
                    },
                    status_code=403,
                    media_type='application/json'
                )

        response = await call_next(request)

        if config.state in [APIVersionState.DEPRECATED, APIVersionState.SUNSET]:
            set_deprecation_headers(response, config.sunset_date, config.successor_version)

        return response

    def extract_version(self, path: str) -> str:
        # Extract version from path like /api/v1/users
        import re
        match = re.search(r'/api/(v\d+)/', path)
        return match.group(1) if match else 'v1'
```

## Migration Paths

### 1. Comprehensive Migration Guides

**Structure of Effective Migration Guide**:

```markdown
# API v1 to v2 Migration Guide

## Executive Summary
- **Timeline**: 6 months to migrate (Dec 2025 - Jun 2026)
- **Effort**: Estimated 2-5 days depending on integration complexity
- **Support**: migration-support@example.com, office hours Tuesdays 2-4pm PST
- **Breaking Changes**: 12 endpoints affected, 3 new authentication requirements

## Pre-Migration Checklist
- [ ] Review all v1 endpoints your application uses
- [ ] Identify breaking changes that affect your integration
- [ ] Set up v2 sandbox/staging environment
- [ ] Allocate development time for migration
- [ ] Plan testing strategy

## Breaking Changes Summary

### Authentication
**Change**: OAuth2 required instead of API keys
- **v1**: `Authorization: ApiKey YOUR_KEY`
- **v2**: `Authorization: Bearer YOUR_OAUTH_TOKEN`
- **Migration**: See [OAuth2 Setup Guide](link)

### Response Format
**Change**: Standardized envelope format
- **v1**: Direct array/object response
- **v2**: Wrapped in `data` field with `meta`

```diff
// v1
- GET /api/v1/users
- [{ "id": 1, "name": "John" }]

// v2
+ GET /api/v2/users
+ {
+   "data": [{ "id": 1, "firstName": "John", "lastName": "Doe" }],
+   "meta": { "total": 1, "page": 1 }
+ }
```

### User Resource Changes
**Change**: Name split into firstName/lastName
```diff
// v1
{
-  "name": "John Doe"
}

// v2
{
+  "firstName": "John",
+  "lastName": "Doe"
}
```

## Step-by-Step Migration

### Step 1: Update Authentication (1-2 hours)

1. Register OAuth2 application in developer portal
2. Implement OAuth2 flow in your application
3. Update token refresh logic
4. Test authentication in staging

**Code Example**:
```typescript
// Before (v1)
const headers = {
  'Authorization': `ApiKey ${process.env.API_KEY}`
};

// After (v2)
import { OAuth2Client } from '@example/oauth2-client';

const oauth2 = new OAuth2Client({
  clientId: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET
});

const token = await oauth2.getAccessToken();
const headers = {
  'Authorization': `Bearer ${token}`
};
```

### Step 2: Update Base URL (15 minutes)

```typescript
// Before
const BASE_URL = 'https://api.example.com/v1';

// After
const BASE_URL = 'https://api.example.com/v2';
```

### Step 3: Update Response Parsing (2-4 hours)

Update all API calls to handle new response envelope:

```typescript
// Before (v1)
async function getUsers() {
  const response = await fetch(`${BASE_URL}/users`);
  const users = await response.json();
  return users; // Direct array
}

// After (v2)
async function getUsers() {
  const response = await fetch(`${BASE_URL}/users`);
  const json = await response.json();
  return json.data; // Extract from envelope
}
```

### Step 4: Update Field Mappings (3-5 hours)

Map old field names to new ones:

```typescript
// Before (v1)
interface UserV1 {
  id: number;
  name: string;
  email: string;
}

// After (v2)
interface UserV2 {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  createdAt: string;
}

// Adapter for gradual migration
function adaptUserV2ToV1(userV2: UserV2): UserV1 {
  return {
    id: userV2.id,
    name: `${userV2.firstName} ${userV2.lastName}`,
    email: userV2.email
  };
}
```

### Step 5: Test in Staging (4-8 hours)

1. Run full integration test suite against v2 staging
2. Test error handling with v2 error format
3. Verify pagination works correctly
4. Load test if high traffic application
5. Security review of OAuth2 implementation

### Step 6: Deploy to Production

1. Deploy during low-traffic window
2. Monitor error rates and API response times
3. Have rollback plan ready
4. Gradually shift traffic (canary deployment)

## Testing Checklist

- [ ] OAuth2 authentication working
- [ ] All endpoints migrated to v2
- [ ] Response parsing handles new envelope format
- [ ] Error handling covers v2 error codes
- [ ] Pagination working correctly
- [ ] Search and filtering work as expected
- [ ] Rate limiting handled appropriately
- [ ] Logging captures v2 request/response format
- [ ] Staging tests passing
- [ ] Production smoke tests passing

## Rollback Plan

If issues arise after migration:

1. Switch BASE_URL back to v1
2. Revert authentication to API key (temporarily)
3. Monitor error recovery
4. Investigate root cause
5. Fix issues and retry migration

## Common Migration Issues

### Issue: OAuth2 token expires during long-running process
**Solution**: Implement token refresh logic
```typescript
if (response.status === 401) {
  await oauth2.refreshToken();
  // Retry request
}
```

### Issue: Pagination broke after migration
**Solution**: v2 uses cursor-based pagination instead of offset
```typescript
// v1: offset-based
GET /v1/users?offset=20&limit=10

// v2: cursor-based
GET /v2/users?cursor=abc123&limit=10
```

### Issue: Date format parsing errors
**Solution**: v2 uses ISO 8601, update date parsing
```typescript
// v1: Custom format
const date = moment(user.created, 'MM/DD/YYYY');

// v2: ISO 8601
const date = new Date(user.createdAt);
```

## Support Resources

- **Documentation**: https://api.example.com/docs/v2
- **Migration Support Email**: migration-support@example.com
- **Office Hours**: Tuesdays 2-4pm PST (Zoom link in email)
- **Slack Channel**: #api-v2-migration
- **Status Page**: https://status.example.com

## FAQ

**Q: Can I run v1 and v2 in parallel during migration?**
A: Yes, you can gradually migrate endpoints while keeping others on v1.

**Q: What if I can't migrate before the deadline?**
A: Contact migration-support@example.com to discuss extension options for enterprise customers.

**Q: Will my API key continue to work?**
A: API keys work for v1 until removal. v2 requires OAuth2.
```

### 2. Compatibility Layers

Create compatibility layers to ease migration:

**TypeScript Compatibility Wrapper**:
```typescript
// v1-compatibility.ts
// Wraps v2 API to provide v1-compatible interface

class APIV1Compatibility {
  private v2Client: APIV2Client;

  constructor(oauth2Client: OAuth2Client) {
    this.v2Client = new APIV2Client(oauth2Client);
  }

  // v1-compatible method that internally uses v2
  async getUsers(): Promise<UserV1[]> {
    const response = await this.v2Client.getUsers();

    // Transform v2 response to v1 format
    return response.data.map(userV2 => ({
      id: userV2.id,
      name: `${userV2.firstName} ${userV2.lastName}`,
      email: userV2.email
    }));
  }

  async getUser(id: number): Promise<UserV1> {
    const userV2 = await this.v2Client.getUser(id);

    return {
      id: userV2.id,
      name: `${userV2.firstName} ${userV2.lastName}`,
      email: userV2.email
    };
  }

  // Gradually expose v2 features
  async getUserWithDetails(id: number): Promise<UserV2> {
    return this.v2Client.getUser(id);
  }
}

// Usage: Drop-in replacement
const api = new APIV1Compatibility(oauth2Client);
const users = await api.getUsers(); // Returns v1 format
```

### 3. Migration Tooling

**Automated Migration Script**:
```typescript
// migrate-to-v2.ts
import { promises as fs } from 'fs';
import * as glob from 'glob';

interface MigrationRule {
  pattern: RegExp;
  replacement: string;
  description: string;
}

const migrationRules: MigrationRule[] = [
  {
    pattern: /\/api\/v1\//g,
    replacement: '/api/v2/',
    description: 'Update API version in URL'
  },
  {
    pattern: /Authorization: ApiKey/g,
    replacement: 'Authorization: Bearer',
    description: 'Update auth header format'
  },
  {
    pattern: /user\.name/g,
    replacement: 'user.firstName + " " + user.lastName',
    description: 'Update name field access'
  },
  {
    pattern: /const response = await fetch\(([^)]+)\);\s*const data = await response\.json\(\);/g,
    replacement: 'const response = await fetch($1);\n  const { data } = await response.json();',
    description: 'Update response parsing for envelope'
  }
];

async function migrateFile(filePath: string): Promise<boolean> {
  let content = await fs.readFile(filePath, 'utf-8');
  let changed = false;

  for (const rule of migrationRules) {
    if (rule.pattern.test(content)) {
      console.log(`  ${rule.description} in ${filePath}`);
      content = content.replace(rule.pattern, rule.replacement);
      changed = true;
    }
  }

  if (changed) {
    await fs.writeFile(filePath, content, 'utf-8');
  }

  return changed;
}

async function main() {
  const files = glob.sync('src/**/*.{ts,js}');
  let totalChanged = 0;

  console.log(`Scanning ${files.length} files for v1 API usage...\n`);

  for (const file of files) {
    const changed = await migrateFile(file);
    if (changed) {
      totalChanged++;
      console.log(`✓ Updated ${file}`);
    }
  }

  console.log(`\nMigration complete: ${totalChanged} files updated`);
  console.log('\nNext steps:');
  console.log('1. Review changes with git diff');
  console.log('2. Update OAuth2 configuration');
  console.log('3. Run tests: npm test');
  console.log('4. Manual review of complex cases');
}

main();
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

## Monitoring Deprecated Endpoints

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

### 3. Backward Compatibility Proxies

For critical enterprise customers, maintain compatibility proxy:

```typescript
// compatibility-proxy.ts
// Translates v1 requests to v2 internally
// Allows gradual migration without hard deadline

class CompatibilityProxy {
  private v2Client: APIV2Client;

  async handleV1Request(req: Request, res: Response) {
    // Log compatibility proxy usage
    Logger.warn('Compatibility proxy used', {
      customer_id: req.user.customerId,
      endpoint: req.path
    });

    try {
      // Transform v1 request to v2
      const v2Request = this.transformV1ToV2Request(req);

      // Call v2 API internally
      const v2Response = await this.v2Client.request(v2Request);

      // Transform v2 response back to v1 format
      const v1Response = this.transformV2ToV1Response(v2Response);

      res.json(v1Response);
    } catch (error) {
      Logger.error('Compatibility proxy error', error);
      res.status(500).json({
        error: 'Compatibility proxy error',
        message: 'Please migrate to v2 API'
      });
    }
  }

  private transformV1ToV2Request(req: Request): V2Request {
    // Transform authentication
    const apiKey = req.headers.authorization?.replace('ApiKey ', '');
    const oauth2Token = this.exchangeAPIKeyForToken(apiKey);

    // Transform request body
    const v2Body = this.transformV1BodyToV2(req.body);

    return {
      method: req.method,
      path: req.path.replace('/v1/', '/v2/'),
      headers: {
        'Authorization': `Bearer ${oauth2Token}`,
        'Content-Type': 'application/json'
      },
      body: v2Body
    };
  }

  private transformV2ToV1Response(v2Response: V2Response): V1Response {
    // Extract data from envelope
    const data = v2Response.data;

    // Transform field names
    if (Array.isArray(data)) {
      return data.map(item => this.transformV2ItemToV1(item));
    } else {
      return this.transformV2ItemToV1(data);
    }
  }

  private transformV2ItemToV1(item: any): any {
    return {
      id: item.id,
      name: `${item.firstName} ${item.lastName}`,
      email: item.email
      // Omit new v2 fields
    };
  }
}
```

## Complete Deprecation Example

Here's a complete end-to-end example of deprecating an API version:

**Step 1: Announce Deprecation**
```typescript
// 2025-12-06: Initial announcement
const announcement = {
  title: 'API v1 Deprecation Announcement',
  date: '2025-12-06',
  timeline: {
    deprecation_start: '2026-01-06',
    sunset_date: '2026-04-01',
    removal_date: '2026-06-01'
  },
  migration_guide: 'https://api.example.com/docs/v1-to-v2',
  support_email: 'migration-support@example.com'
};

// Send emails to all v1 users
await notifyAllV1Users(announcement);
```

**Step 2: Add Deprecation Headers (2026-01-06)**
```typescript
app.use('/api/v1', (req, res, next) => {
  res.set('Deprecation', 'true');
  res.set('Sunset', 'Sat, 01 Jun 2026 00:00:00 GMT');
  res.set('Link', '</api/v2>; rel="successor-version"');
  next();
});
```

**Step 3: Add Response Warnings**
```typescript
app.use('/api/v1', (req, res, next) => {
  const originalJson = res.json.bind(res);
  res.json = function(body: any) {
    return originalJson({
      data: body,
      meta: {
        deprecation: {
          deprecated: true,
          sunset_date: '2026-04-01T00:00:00Z',
          removal_date: '2026-06-01T00:00:00Z',
          migration_guide: 'https://api.example.com/docs/v1-to-v2'
        }
      }
    });
  };
  next();
});
```

**Step 4: Monthly Reminder Emails**
```typescript
// Automated monthly reminders
cron.schedule('0 9 1 * *', async () => {
  const stuckUsers = await findStuckConsumers();

  for (const user of stuckUsers) {
    await sendEmail({
      to: user.email,
      subject: `Reminder: API v1 Removal in ${user.days_until_sunset} Days`,
      body: renderEmailTemplate('monthly_reminder', user)
    });
  }
});
```

**Step 5: Sunset Mode (2026-04-01)**
```typescript
app.use('/api/v1', (req, res, next) => {
  // Read-only mode: block write operations
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    return res.status(403).json({
      error: 'API v1 is in sunset mode (read-only)',
      removal_date: '2026-06-01T00:00:00Z',
      message: 'Write operations disabled. Migrate to v2.'
    });
  }
  next();
});
```

**Step 6: Final Warning (2026-05-01)**
```typescript
// 30 days before removal
const finalWarning = await findStuckConsumers();

for (const user of finalWarning) {
  await sendUrgentEmail({
    to: user.email,
    subject: 'URGENT: API v1 Removal in 30 Days',
    priority: 'high',
    body: renderEmailTemplate('final_warning', user)
  });

  // Also SMS for high-value customers
  if (user.plan === 'enterprise') {
    await sendSMS(user.phone, 'URGENT: API v1 removal in 30 days. Contact support.');
  }
}
```

**Step 7: Complete Removal (2026-06-01)**
```typescript
app.use('/api/v1', (req, res) => {
  return res.status(410).json({
    error: 'This API version has been removed',
    removal_date: '2026-06-01T00:00:00Z',
    successor_version: 'v2',
    migration_guide: 'https://api.example.com/docs/v1-to-v2',
    contact_email: 'api-support@example.com'
  });
});
```

**Step 8: Monitor Migration Success**
```typescript
// Track migration completion
const migrationStats = await db.query(`
  SELECT
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT CASE WHEN has_migrated THEN customer_id END) as migrated_customers,
    COUNT(DISTINCT CASE WHEN has_migrated THEN customer_id END)::float /
      COUNT(DISTINCT customer_id) * 100 as migration_percentage
  FROM customer_migration_status
`);

console.log(`Migration Status: ${migrationStats.migration_percentage}% complete`);
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

- [ ] **Add Deprecation Indicators**
  - [ ] Add Deprecation and Sunset HTTP headers
  - [ ] Include deprecation metadata in responses
  - [ ] Update API documentation with warnings
  - [ ] Add visual indicators in developer portal

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

- [ ] **Enforce Sunset**
  - [ ] Enter read-only mode at sunset date
  - [ ] Block write operations (POST/PUT/PATCH/DELETE)
  - [ ] Maintain GET requests during grace period

- [ ] **Complete Removal**
  - [ ] Return 410 Gone for all requests
  - [ ] Provide clear error message with migration info
  - [ ] Monitor for errors and customer complaints
  - [ ] Maintain redirect/proxy for critical customers

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

### HTTP Headers

```http
Deprecation: true
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
Link: </api/v2>; rel="successor-version"
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

### Error Codes

- **200 OK** + Deprecation headers: Deprecated but functional
- **403 Forbidden**: Sunset mode (read-only), write blocked
- **410 Gone**: Completely removed
- **429 Too Many Requests** + Deprecation info: Rate limiting deprecated version

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
- Compatibility layers/proxies
- Extended timelines for SLA customers
