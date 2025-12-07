# API Deprecation Migration

Comprehensive guide to migration paths, compatibility layers, automated tooling, and client migration support for API deprecation.

## Table of Contents

1. [Migration Guides](#migration-guides)
2. [Compatibility Layers](#compatibility-layers)
3. [Migration Tooling](#migration-tooling)
4. [Backward Compatibility Strategies](#backward-compatibility-strategies)
5. [Complete Migration Example](#complete-migration-example)
6. [Quick Reference](#quick-reference)

## Migration Guides

### Structure of Effective Migration Guide

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

## Compatibility Layers

### Client-Side Compatibility Wrapper

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

### Server-Side Compatibility Proxy

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

  private async exchangeAPIKeyForToken(apiKey: string): Promise<string> {
    // Look up customer by API key
    const customer = await db.customers.findByApiKey(apiKey);

    // Generate temporary OAuth2 token for compatibility
    const token = await oauth2.generateToken({
      customer_id: customer.id,
      scope: 'api:legacy',
      expires_in: 3600
    });

    return token.access_token;
  }

  private transformV1BodyToV2(v1Body: any): any {
    // Transform request fields from v1 to v2 format
    if (v1Body.name) {
      const [firstName, ...lastNameParts] = v1Body.name.split(' ');
      return {
        ...v1Body,
        firstName,
        lastName: lastNameParts.join(' '),
        name: undefined // Remove old field
      };
    }
    return v1Body;
  }
}

// Usage
app.use('/v1', async (req, res) => {
  const proxy = new CompatibilityProxy();
  await proxy.handleV1Request(req, res);
});
```

## Migration Tooling

### Automated Migration Script

**TypeScript Migration Script**:
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

### Migration Detection Script

**Identify v1 API Usage**:
```typescript
// detect-v1-usage.ts
import * as glob from 'glob';
import { promises as fs } from 'fs';

interface V1Usage {
  file: string;
  line: number;
  code: string;
  type: 'url' | 'auth' | 'field' | 'import';
}

async function detectV1Usage(): Promise<V1Usage[]> {
  const files = glob.sync('src/**/*.{ts,js}');
  const usages: V1Usage[] = [];

  for (const file of files) {
    const content = await fs.readFile(file, 'utf-8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      // Detect v1 URL references
      if (/\/api\/v1\//.test(line)) {
        usages.push({
          file,
          line: index + 1,
          code: line.trim(),
          type: 'url'
        });
      }

      // Detect API key authentication
      if (/Authorization.*ApiKey/i.test(line)) {
        usages.push({
          file,
          line: index + 1,
          code: line.trim(),
          type: 'auth'
        });
      }

      // Detect v1 field references
      if (/user\.name/.test(line)) {
        usages.push({
          file,
          line: index + 1,
          code: line.trim(),
          type: 'field'
        });
      }
    });
  }

  return usages;
}

async function main() {
  const usages = await detectV1Usage();

  console.log(`Found ${usages.length} instances of v1 API usage:\n`);

  // Group by type
  const byType = usages.reduce((acc, usage) => {
    if (!acc[usage.type]) acc[usage.type] = [];
    acc[usage.type].push(usage);
    return acc;
  }, {} as Record<string, V1Usage[]>);

  for (const [type, items] of Object.entries(byType)) {
    console.log(`\n${type.toUpperCase()} (${items.length} instances):`);
    items.forEach(item => {
      console.log(`  ${item.file}:${item.line}`);
      console.log(`    ${item.code}`);
    });
  }

  console.log('\n\nRun migrate-to-v2.ts to automatically fix these issues.');
}

main();
```

### Migration Progress Tracker

```typescript
// migration-tracker.ts
interface MigrationProgress {
  total_files: number;
  migrated_files: number;
  remaining_files: number;
  total_usages: number;
  remaining_usages: number;
  percentage_complete: number;
  estimated_hours_remaining: number;
}

async function trackMigrationProgress(): Promise<MigrationProgress> {
  const allFiles = glob.sync('src/**/*.{ts,js}');
  const v1Usages = await detectV1Usage();

  const filesWithUsages = new Set(v1Usages.map(u => u.file));
  const remainingFiles = filesWithUsages.size;
  const migratedFiles = allFiles.length - remainingFiles;

  const percentageComplete = (migratedFiles / allFiles.length) * 100;
  const avgTimePerFile = 0.5; // hours
  const estimatedHoursRemaining = remainingFiles * avgTimePerFile;

  return {
    total_files: allFiles.length,
    migrated_files: migratedFiles,
    remaining_files: remainingFiles,
    total_usages: v1Usages.length,
    remaining_usages: v1Usages.length,
    percentage_complete: percentageComplete,
    estimated_hours_remaining: estimatedHoursRemaining
  };
}

async function main() {
  const progress = await trackMigrationProgress();

  console.log('\nMigration Progress Report');
  console.log('=========================\n');
  console.log(`Files: ${progress.migrated_files}/${progress.total_files} migrated`);
  console.log(`Progress: ${progress.percentage_complete.toFixed(1)}%`);
  console.log(`Remaining v1 usages: ${progress.remaining_usages}`);
  console.log(`Estimated time: ${progress.estimated_hours_remaining.toFixed(1)} hours\n`);

  // Visual progress bar
  const barLength = 50;
  const filledLength = Math.round((progress.percentage_complete / 100) * barLength);
  const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
  console.log(`[${bar}] ${progress.percentage_complete.toFixed(1)}%\n`);
}

main();
```

## Backward Compatibility Strategies

### Version Negotiation

**Content Negotiation for API Versioning**:
```typescript
app.use((req, res, next) => {
  const acceptHeader = req.headers['accept'];
  const customVersionHeader = req.headers['x-api-version'];

  // Determine version from Accept header
  if (acceptHeader?.includes('application/vnd.example.v2+json')) {
    req.apiVersion = 'v2';
  } else if (acceptHeader?.includes('application/vnd.example.v1+json')) {
    req.apiVersion = 'v1';
  } else if (customVersionHeader) {
    req.apiVersion = customVersionHeader;
  } else {
    // Default to latest version
    req.apiVersion = 'v2';
  }

  next();
});

// Route handler
app.get('/api/users', async (req, res) => {
  if (req.apiVersion === 'v2') {
    return getUsersV2(req, res);
  } else {
    return getUsersV1(req, res);
  }
});
```

### Dual-Write Pattern

**Write to Both Old and New Systems During Migration**:
```typescript
async function createUser(userData: UserInput) {
  // Write to v2 (primary)
  const userV2 = await createUserV2(userData);

  // Also write to v1 for backward compatibility
  try {
    await createUserV1(transformToV1(userData));
  } catch (error) {
    Logger.warn('Failed to write to v1 system', error);
    // Don't fail the request if v1 write fails
  }

  return userV2;
}
```

### Field Expansion Pattern

**Support Both Old and New Field Names**:
```typescript
interface UserResponse {
  id: number;
  // New fields (v2)
  firstName: string;
  lastName: string;
  // Deprecated fields (v1) - computed for backward compatibility
  name?: string;
}

function buildUserResponse(user: User, apiVersion: string): UserResponse {
  const response: UserResponse = {
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName
  };

  // Include deprecated field for v1 clients
  if (apiVersion === 'v1') {
    response.name = `${user.firstName} ${user.lastName}`;
  }

  return response;
}
```

## Complete Migration Example

Here's a complete end-to-end migration workflow:

**Phase 1: Analysis (Week 1)**
```bash
# Detect all v1 usage
npm run detect-v1-usage > migration-report.txt

# Review report and plan migration
cat migration-report.txt

# Track initial progress
npm run migration-progress
```

**Phase 2: Automated Migration (Week 2)**
```bash
# Create feature branch
git checkout -b migrate-to-api-v2

# Run automated migration
npm run migrate-to-v2

# Review changes
git diff

# Commit changes
git add .
git commit -m "chore: migrate from API v1 to v2"
```

**Phase 3: Manual Fixes (Week 3)**
```typescript
// Fix complex cases that automation couldn't handle

// Before (v1)
const users = await api.getUsers({
  search: 'john',
  offset: 20,
  limit: 10
});

// After (v2) - cursor-based pagination
const users = await api.getUsers({
  search: 'john',
  cursor: lastUserCursor,
  limit: 10
});
```

**Phase 4: Testing (Week 4)**
```bash
# Run test suite against v2
npm test

# Run integration tests in staging
npm run test:integration -- --env=staging

# Load testing
npm run test:load
```

**Phase 5: Staged Rollout (Week 5-6)**
```typescript
// Use feature flag for gradual rollout
const useV2 = featureFlags.isEnabledForUser('api_v2', customerId);

if (useV2) {
  return apiV2.getUsers();
} else {
  return apiV1.getUsers();
}
```

**Phase 6: Monitor and Iterate (Ongoing)**
```bash
# Monitor v2 error rates
npm run monitor:errors -- --version=v2

# Track migration progress
npm run migration-progress

# Generate migration report
npm run migration-report
```

## Quick Reference

### Migration Steps

1. **Analyze**: Detect all v1 API usage
2. **Automate**: Run migration scripts
3. **Fix**: Handle complex cases manually
4. **Test**: Verify in staging environment
5. **Deploy**: Gradual rollout with monitoring
6. **Verify**: Confirm migration success

### Migration Checklist

- [ ] Run detection script to find v1 usage
- [ ] Review and plan migration approach
- [ ] Run automated migration tool
- [ ] Manual fixes for complex cases
- [ ] Update OAuth2 configuration
- [ ] Test in staging environment
- [ ] Deploy with feature flags
- [ ] Monitor error rates
- [ ] Verify no v1 traffic after cutover

### Compatibility Strategies

1. **Client-side wrapper**: Wrap v2 API to expose v1 interface
2. **Server-side proxy**: Translate v1 requests to v2
3. **Version negotiation**: Support both versions via headers
4. **Dual-write**: Write to both v1 and v2 during transition
5. **Field expansion**: Include deprecated fields for backward compatibility

### Tools

- **detect-v1-usage.ts**: Find all v1 API references
- **migrate-to-v2.ts**: Automated code migration
- **migration-tracker.ts**: Track migration progress
- **compatibility-proxy.ts**: Server-side compatibility layer
