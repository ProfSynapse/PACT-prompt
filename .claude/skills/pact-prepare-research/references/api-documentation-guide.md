# API Documentation Guide

**Purpose**: Systematic approach to analyzing, testing, and documenting third-party APIs during the Prepare phase.

**When to Use**: Integrating external services, evaluating API-based platforms, documenting REST/GraphQL endpoints, or assessing SDK capabilities.

---

## Quick Reference

### Essential API Research Steps

1. **Authentication Setup**: Obtain credentials, test auth flow, document security
2. **Endpoint Discovery**: Identify required endpoints, test requests/responses
3. **Error Handling**: Document error codes, test failure scenarios
4. **Rate Limits**: Identify limits, test throttling behavior, plan mitigation
5. **SDK Evaluation**: Test official SDKs, document integration patterns

### Critical Questions

- What authentication method does the API use?
- What are the rate limits and quotas?
- How does error handling work?
- Is there pagination? How is it implemented?
- What's the API versioning strategy?
- Are webhooks supported?
- What's the data retention/deletion policy?

---

## Phase 1: Authentication Exploration

### Authentication Method Identification

**Common Authentication Types**:

**API Key**:
```http
GET /api/resources HTTP/1.1
Host: api.example.com
X-API-Key: your-api-key-here
```
- **Pros**: Simple, fast to implement
- **Cons**: Less secure, no granular permissions
- **Use when**: Simple integrations, server-to-server only

**Bearer Token (OAuth 2.0)**:
```http
GET /api/resources HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
- **Pros**: Industry standard, token expiration, refresh mechanism
- **Cons**: More complex setup
- **Use when**: User-facing applications, need delegated access

**JWT (JSON Web Tokens)**:
```http
GET /api/resources HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
- **Pros**: Self-contained, stateless, includes user info
- **Cons**: Larger payload size, revocation complexity
- **Use when**: Microservices, distributed systems

**Basic Authentication**:
```http
GET /api/resources HTTP/1.1
Host: api.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```
- **Pros**: Simple, universally supported
- **Cons**: Credentials in every request (must use HTTPS)
- **Use when**: Internal APIs, development only

### Authentication Testing Workflow

**Step 1: Obtain Credentials**
```markdown
Document:
- How to create developer account
- Where to generate API keys/tokens
- Credential format and structure
- Rotation/expiration policies
- Revocation process
```

**Step 2: Test Authentication**
```bash
# Example cURL test for API key
curl -X GET https://api.example.com/v1/auth/test \
  -H "X-API-Key: your-api-key"

# Expected success response
{
  "authenticated": true,
  "user_id": "usr_123",
  "permissions": ["read", "write"]
}
```

**Step 3: Document Token Lifecycle**
```markdown
## Authentication Flow

1. Obtain token:
   - Endpoint: POST /auth/token
   - Payload: { client_id, client_secret }
   - Response: { access_token, refresh_token, expires_in }

2. Use token:
   - Header: Authorization: Bearer {access_token}
   - Valid for: 3600 seconds (1 hour)

3. Refresh token:
   - Endpoint: POST /auth/refresh
   - Payload: { refresh_token }
   - Response: { access_token, expires_in }

4. Handle expiration:
   - Error: 401 Unauthorized
   - Action: Refresh token or re-authenticate
```

### Security Considerations Checklist

```markdown
Authentication Security:
- [ ] HTTPS required for all requests
- [ ] TLS version minimum (1.2 or 1.3)
- [ ] Credential storage strategy (env vars, secrets manager)
- [ ] Rotation frequency (API keys every 90 days)
- [ ] Scope/permissions model documented
- [ ] IP allowlisting available (if needed)
- [ ] Webhook signature verification method
- [ ] Token refresh mechanism tested
- [ ] Revocation process understood
- [ ] Multi-factor authentication support
```

---

## Phase 2: Endpoint Analysis

### Endpoint Discovery Strategy

**Identify Required Endpoints**:
```markdown
Map user stories to API endpoints:

User Story: "As a user, I can view my order history"
Required Endpoints:
- GET /orders - List orders
- GET /orders/{id} - Get order details
- GET /orders/{id}/items - Get order line items

User Story: "As a user, I can update my profile"
Required Endpoints:
- GET /profile - Get current profile
- PUT /profile - Update profile
- PATCH /profile - Partial update
```

### Request Documentation Template

**For Each Endpoint**:
```markdown
### GET /api/v1/resources/{id}

**Purpose**: Retrieve a specific resource by ID

**URL Pattern**: `https://api.example.com/v1/resources/{id}`

**HTTP Method**: GET

**Authentication**: Required (Bearer token)

**Headers**:
```http
Authorization: Bearer {token}
Accept: application/json
X-API-Version: 2023-11-01
```

**Path Parameters**:
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | string | Yes | Unique resource identifier | "res_abc123" |

**Query Parameters**:
| Name | Type | Required | Default | Description | Example |
|------|------|----------|---------|-------------|---------|
| include | string | No | null | Related resources to include | "owner,tags" |
| fields | string | No | all | Specific fields to return | "id,name,created_at" |

**Success Response (200 OK)**:
```json
{
  "id": "res_abc123",
  "name": "Example Resource",
  "status": "active",
  "created_at": "2025-12-04T10:00:00Z",
  "updated_at": "2025-12-04T12:00:00Z",
  "owner": {
    "id": "usr_456",
    "name": "John Doe"
  }
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource ID doesn't exist
- **429 Too Many Requests**: Rate limit exceeded
```

### Response Schema Documentation

**Capture Complete Schema**:
```markdown
| Field | Type | Always Present | Nullable | Description |
|-------|------|----------------|----------|-------------|
| id | string | Yes | No | Unique identifier |
| name | string | Yes | No | Resource name |
| status | enum | Yes | No | Values: "active", "inactive", "pending" |
| created_at | ISO 8601 | Yes | No | Creation timestamp |
| updated_at | ISO 8601 | Yes | No | Last update timestamp |
| owner | object | Yes | Yes | Owner information (null if deleted) |
| owner.id | string | If owner present | No | Owner user ID |
| owner.name | string | If owner present | Yes | Owner display name |
| metadata | object | No | Yes | Custom key-value pairs |
```

---

## Phase 3: Rate Limit Discovery

### Rate Limit Investigation

**Identify Rate Limits**:
```markdown
Check documentation for:
1. Request rate limits (requests per second/minute/hour)
2. Quota limits (daily/monthly caps)
3. Burst allowances (temporary spikes)
4. Per-endpoint limits (different endpoints may have different limits)
5. Authenticated vs. unauthenticated limits
```

**Test Rate Limiting**:
```javascript
// Rate limit test script
async function testRateLimits() {
  const results = {
    requests: 0,
    rateLimitHit: false,
    limitHeaders: null
  };

  for (let i = 0; i < 200; i++) {
    try {
      const response = await fetch('https://api.example.com/v1/test', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      results.requests++;

      // Capture rate limit headers
      results.limitHeaders = {
        limit: response.headers.get('X-RateLimit-Limit'),
        remaining: response.headers.get('X-RateLimit-Remaining'),
        reset: response.headers.get('X-RateLimit-Reset')
      };

      if (response.status === 429) {
        results.rateLimitHit = true;
        results.retryAfter = response.headers.get('Retry-After');
        break;
      }
    } catch (error) {
      console.error(`Request ${i} failed:`, error);
      break;
    }
  }

  return results;
}
```

### Rate Limit Headers Documentation

**Standard Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701705600
Retry-After: 60
```

**Document Header Meanings**:
```markdown
| Header | Type | Description | Example |
|--------|------|-------------|---------|
| X-RateLimit-Limit | integer | Total requests allowed per period | 100 |
| X-RateLimit-Remaining | integer | Requests remaining in current period | 95 |
| X-RateLimit-Reset | unix timestamp | When rate limit resets | 1701705600 |
| Retry-After | integer | Seconds to wait before retry | 60 |
```

### Rate Limit Mitigation Strategies

**Strategy 1: Request Queuing**:
```javascript
class RateLimitedAPIClient {
  constructor(requestsPerSecond) {
    this.queue = [];
    this.interval = 1000 / requestsPerSecond;
    this.processing = false;
  }

  async request(endpoint, options) {
    return new Promise((resolve, reject) => {
      this.queue.push({ endpoint, options, resolve, reject });
      if (!this.processing) this.processQueue();
    });
  }

  async processQueue() {
    this.processing = true;
    while (this.queue.length > 0) {
      const { endpoint, options, resolve, reject } = this.queue.shift();
      try {
        const result = await fetch(endpoint, options);
        resolve(result);
      } catch (error) {
        reject(error);
      }
      await this.sleep(this.interval);
    }
    this.processing = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

**Strategy 2: Exponential Backoff**:
```javascript
async function retryWithBackoff(operation, maxRetries = 5) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (error.status === 429) {
        const retryAfter = error.headers.get('Retry-After') ||
                          Math.pow(2, attempt);
        await sleep(retryAfter * 1000);
      } else {
        throw error;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Phase 4: Error Response Cataloging

### Error Format Analysis

**Document Standard Error Structure**:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource with ID 'res_123' not found",
    "details": {
      "resource_id": "res_123",
      "resource_type": "order"
    },
    "request_id": "req_abc456def",
    "documentation_url": "https://docs.api.example.com/errors#not-found"
  }
}
```

**Error Field Documentation**:
```markdown
| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| error.code | string | Yes | Machine-readable error code |
| error.message | string | Yes | Human-readable description |
| error.details | object | No | Additional error context |
| error.request_id | string | Yes | Request ID for support |
| error.documentation_url | string | No | Link to error docs |
```

### Error Code Catalog

**Create Error Matrix**:
```markdown
| HTTP Status | Error Code | Meaning | Action |
|-------------|------------|---------|--------|
| 400 | INVALID_REQUEST | Malformed request body or params | Fix request format |
| 400 | VALIDATION_ERROR | Request validation failed | Check field constraints |
| 401 | UNAUTHORIZED | Missing or invalid authentication | Re-authenticate |
| 401 | TOKEN_EXPIRED | Access token has expired | Refresh token |
| 403 | FORBIDDEN | Insufficient permissions | Check user permissions |
| 404 | RESOURCE_NOT_FOUND | Resource doesn't exist | Verify resource ID |
| 409 | CONFLICT | Resource conflict (e.g., duplicate) | Handle conflict state |
| 422 | UNPROCESSABLE_ENTITY | Semantic errors in request | Fix business logic |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests | Implement backoff |
| 500 | INTERNAL_SERVER_ERROR | Server-side error | Retry, contact support |
| 503 | SERVICE_UNAVAILABLE | API temporarily down | Circuit breaker, retry |
```

### Error Testing Scenarios

**Test Each Error Type**:
```javascript
// Error scenario tests
const errorTests = [
  {
    name: 'Invalid Authentication',
    test: () => fetch('/api/resource', {
      headers: { 'Authorization': 'Bearer invalid-token' }
    }),
    expectedStatus: 401,
    expectedCode: 'UNAUTHORIZED'
  },
  {
    name: 'Validation Error',
    test: () => fetch('/api/resources', {
      method: 'POST',
      body: JSON.stringify({ name: '' }) // Invalid empty name
    }),
    expectedStatus: 400,
    expectedCode: 'VALIDATION_ERROR'
  },
  {
    name: 'Resource Not Found',
    test: () => fetch('/api/resources/nonexistent-id'),
    expectedStatus: 404,
    expectedCode: 'RESOURCE_NOT_FOUND'
  }
];

// Run all error tests
for (const errorTest of errorTests) {
  const response = await errorTest.test();
  console.log(`${errorTest.name}: ${response.status} - ${response.statusText}`);
}
```

---

## Phase 5: SDK Evaluation

### Official SDK Assessment

**SDK Evaluation Criteria**:
```markdown
- [ ] Language/runtime version support
- [ ] Installation method (npm, pip, gem, etc.)
- [ ] Documentation quality
- [ ] Code examples availability
- [ ] Type definitions (TypeScript, Python type hints)
- [ ] Error handling patterns
- [ ] Retry logic built-in
- [ ] Rate limiting handling
- [ ] Pagination support
- [ ] Webhook utilities
- [ ] Test utilities/mocks
- [ ] Active maintenance (recent updates)
- [ ] Community adoption (downloads, stars)
```

### SDK Feature Testing

**Test SDK Capabilities**:
```javascript
// SDK feature test
const { APIClient } = require('@vendor/sdk');

const client = new APIClient({
  apiKey: process.env.API_KEY,
  environment: 'sandbox'
});

// Test 1: Basic CRUD operations
const resource = await client.resources.create({ name: 'Test' });
const retrieved = await client.resources.get(resource.id);
await client.resources.update(resource.id, { name: 'Updated' });
await client.resources.delete(resource.id);

// Test 2: Error handling
try {
  await client.resources.get('nonexistent-id');
} catch (error) {
  console.log('Error type:', error.constructor.name);
  console.log('Error code:', error.code);
  console.log('Request ID:', error.requestId);
}

// Test 3: Pagination
const allResources = [];
for await (const resource of client.resources.list({ limit: 100 })) {
  allResources.push(resource);
}

// Test 4: Retry behavior
const result = await client.resources.get(id, {
  retry: { attempts: 3, backoff: 'exponential' }
});
```

### SDK vs Raw HTTP Comparison

**Decision Matrix**:
```markdown
| Feature | SDK | Raw HTTP | Notes |
|---------|-----|----------|-------|
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐ | SDK faster to implement |
| **Type Safety** | ⭐⭐⭐⭐⭐ | ⭐⭐ | SDK has TypeScript defs |
| **Error Handling** | ⭐⭐⭐⭐ | ⭐⭐⭐ | SDK has structured errors |
| **Retry Logic** | ⭐⭐⭐⭐⭐ | ⭐ | SDK has built-in retry |
| **Bundle Size** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Raw HTTP smaller |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Raw HTTP more control |
| **Debugging** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Raw HTTP easier to debug |
| **Maintenance** | ⭐⭐⭐⭐ | ⭐⭐ | SDK maintained by vendor |

**Recommendation**: Use SDK if:
- Official SDK is well-maintained
- Development speed is priority
- Built-in features (retry, pagination) valuable

Use Raw HTTP if:
- Need minimal bundle size
- SDK has bugs or missing features
- Need full control over requests
```

---

## Pagination Patterns

### Common Pagination Types

**Offset-Based Pagination**:
```http
GET /api/resources?limit=20&offset=40
```
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "limit": 20,
    "offset": 40,
    "has_more": true
  }
}
```

**Cursor-Based Pagination**:
```http
GET /api/resources?limit=20&cursor=eyJpZCI6MTIzfQ
```
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_more": true
  }
}
```

**Page-Based Pagination**:
```http
GET /api/resources?page=3&per_page=20
```
```json
{
  "data": [...],
  "pagination": {
    "page": 3,
    "per_page": 20,
    "total_pages": 50,
    "total_count": 1000
  }
}
```

### Pagination Implementation

**Generic Pagination Iterator**:
```javascript
async function* paginateAPI(endpoint, pageSize = 100) {
  let hasMore = true;
  let cursor = null;

  while (hasMore) {
    const params = new URLSearchParams({ limit: pageSize });
    if (cursor) params.set('cursor', cursor);

    const response = await fetch(`${endpoint}?${params}`);
    const data = await response.json();

    for (const item of data.data) {
      yield item;
    }

    hasMore = data.pagination.has_more;
    cursor = data.pagination.next_cursor;
  }
}

// Usage
for await (const resource of paginateAPI('/api/resources')) {
  console.log(resource);
}
```

---

## Documentation Deliverable Template

```markdown
# API Documentation: [Service Name]

**API Version**: [Version]
**Documentation URL**: [Official docs link]
**Base URL**: [Production URL]
**Sandbox URL**: [Test environment URL]

## Authentication

**Method**: [Type]
**Setup**: [Steps to obtain credentials]
**Token Lifetime**: [Duration]
**Refresh Mechanism**: [How to refresh]

## Endpoints Summary

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| /resources | GET | List resources | 100/min |
| /resources/{id} | GET | Get resource | 1000/min |
| /resources | POST | Create resource | 50/min |

## Rate Limits

- **Global**: 1000 requests/hour
- **Per Endpoint**: See table above
- **Burst**: 10 requests/second
- **Headers**: X-RateLimit-*

## Error Handling

**Error Format**: [Structure]
**Error Codes**: [See catalog]
**Retry Strategy**: [Exponential backoff recommended]

## SDK Recommendation

**Use**: [@vendor/sdk-js](link) v[X.Y.Z]
**Reason**: [Well-maintained, type-safe, built-in retry]

## Security

- **HTTPS Required**: Yes
- **TLS Minimum**: 1.2
- **Credential Storage**: Environment variables
- **IP Allowlisting**: Available

## Next Steps for Architect

- [ ] Design API client wrapper interface
- [ ] Implement retry and circuit breaker strategy
- [ ] Plan webhook processing architecture
- [ ] Define error logging strategy
```

---

## Checklist: API Research Completeness

Before finishing API documentation:

**Authentication**:
- [ ] Authentication method documented
- [ ] Credentials obtained and tested
- [ ] Token refresh mechanism understood
- [ ] Security requirements captured

**Endpoints**:
- [ ] All required endpoints identified
- [ ] Request/response formats documented
- [ ] Path and query parameters cataloged
- [ ] Success and error responses tested

**Rate Limits**:
- [ ] Rate limits documented
- [ ] Quota limits identified
- [ ] Rate limit headers understood
- [ ] Mitigation strategy planned

**Error Handling**:
- [ ] Error response format documented
- [ ] All error codes cataloged
- [ ] Error scenarios tested
- [ ] Retry strategy defined

**SDK**:
- [ ] Official SDK evaluated
- [ ] SDK vs raw HTTP decision made
- [ ] Integration examples created
- [ ] Dependencies documented

**Security**:
- [ ] HTTPS/TLS requirements noted
- [ ] Credential storage strategy defined
- [ ] Webhook signature verification documented
- [ ] Compliance requirements identified

---

## Summary

Thorough API research during the Prepare phase prevents integration surprises during implementation. By systematically exploring authentication, endpoints, rate limits, error handling, and SDK capabilities, you create comprehensive documentation that enables the Architect to design robust integration patterns.

**Key Principles**:
- **Test Don't Assume**: Always test API behavior, don't rely only on docs
- **Document Errors**: Error cases are as important as success cases
- **Plan for Limits**: Rate limits and quotas affect architecture
- **Security First**: Authentication and credential management are critical
- **SDK Evaluation**: Weigh SDK convenience against control and bundle size

**Remember**: APIs change. Document version-specific behavior and monitor for deprecation notices.
