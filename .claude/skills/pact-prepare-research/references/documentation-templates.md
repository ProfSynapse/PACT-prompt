# Documentation Templates for Prepare Phase

**Purpose**: Complete templates for all Prepare phase deliverables to ensure consistent, comprehensive documentation.

**When to Use**: Creating documentation for handoff to Architect phase, documenting research findings, capturing requirements, or organizing preparation outputs.

---

## Template Overview

This file provides ready-to-use templates for:

1. **Technology Research Summary** - Document technology evaluation and decisions
2. **API Documentation** - Document third-party API integrations
3. **Dependency Analysis** - Map dependencies and version compatibility
4. **Security Requirements** - Capture security findings and requirements
5. **Requirements Analysis** - Document functional and non-functional requirements
6. **Technology Comparison Matrix** - Compare multiple technology options
7. **Research Summary** - Executive summary for stakeholders

---

## Template 1: Technology Research Summary

**File**: `docs/preparation/technology-research.md`

```markdown
# Technology Research: [Technology Name]

**Research Date**: [YYYY-MM-DD]
**Researcher**: [Name]
**Status**: [Recommended / Not Recommended / Conditional]
**Decision**: [Brief decision statement]

---

## Executive Summary

[2-3 paragraphs summarizing the technology, why it was researched, key findings, and recommendation. This should be readable by non-technical stakeholders.]

**TL;DR**: [One sentence summary]

---

## Technology Overview

### Basic Information

| Property | Value |
|----------|-------|
| **Name** | [Official technology name] |
| **Version Researched** | [Exact version number] |
| **Official Website** | [URL] |
| **Repository** | [GitHub or GitLab URL] |
| **License** | [License type - MIT, Apache 2.0, etc.] |
| **First Release** | [Year] |
| **Current Status** | [Active / Maintenance / Deprecated] |
| **Primary Maintainer** | [Company or organization] |

### Purpose and Use Cases

**What It Does**:
[Clear explanation of what this technology does and what problems it solves]

**Primary Use Cases**:
- [Use case 1]
- [Use case 2]
- [Use case 3]

**Not Suitable For**:
- [Anti-pattern 1]
- [Anti-pattern 2]

---

## Requirements Coverage

### Functional Requirements

| Requirement | Priority | Supported | How | Notes |
|-------------|----------|-----------|-----|-------|
| [Requirement 1] | Must-have | ✅ Yes | [Native feature / Plugin / Workaround] | [Context] |
| [Requirement 2] | Should-have | ⚠️ Partial | [Description of support] | [Limitations] |
| [Requirement 3] | Nice-to-have | ❌ No | N/A | [Alternative approach] |

### Non-Functional Requirements

| Requirement | Priority | Met | Evidence | Notes |
|-------------|----------|-----|----------|-------|
| Performance: [metric] | Must-have | ✅ Yes | [Benchmark link] | [Details] |
| Security: [requirement] | Must-have | ✅ Yes | [Feature or practice] | [Details] |
| Scalability: [requirement] | Should-have | ⚠️ Partial | [Limitation] | [Mitigation] |

**Coverage Summary**: [X of Y must-haves met, Y of Z should-haves met]

---

## Technical Details

### Installation

**Prerequisites**:
- [Prerequisite 1 - e.g., Node.js ≥16]
- [Prerequisite 2 - e.g., Python ≥3.8]

**Installation Steps**:
```bash
# Installation commands
npm install [package-name]
# or
pip install [package-name]
```

**Configuration**:
```[language]
// Configuration example
{
  "option1": "value1",
  "option2": "value2"
}
```

**Verification**:
```bash
# How to verify installation worked
[command to check installation]
```

### Integration with Existing Stack

**Tech Stack Compatibility**:
| Our Technology | Version | Compatible? | Notes |
|----------------|---------|-------------|-------|
| [Tech 1] | [Version] | ✅ Yes | [Details] |
| [Tech 2] | [Version] | ⚠️ With adapter | [What's needed] |
| [Tech 3] | [Version] | ❌ No | [Blocker] |

**Integration Approach**:
[Describe how this integrates with existing architecture]

**Integration Complexity**: [Low / Medium / High]

### Core APIs and Usage

**Key APIs**:
```[language]
// Example 1: [Most common use case]
[code example]

// Example 2: [Second common use case]
[code example]
```

**Patterns We'll Use**:
- [Pattern 1]: [Description]
- [Pattern 2]: [Description]

---

## Performance Characteristics

### Benchmarks

**Official Benchmarks**: [Link to benchmarks or "None available"]

**Performance Metrics**:
| Metric | Value | Acceptable? | Notes |
|--------|-------|-------------|-------|
| Latency (p50) | [X ms] | ✅ Yes | [Context] |
| Latency (p99) | [X ms] | ✅ Yes | [Context] |
| Throughput | [X req/s] | ⚠️ Marginal | [May need optimization] |
| Memory usage | [X MB] | ✅ Yes | [Context] |
| Bundle size (if frontend) | [X KB] | ✅ Yes | [Gzipped] |

**Performance Characteristics**:
- [Characteristic 1 - e.g., "Constant time lookups"]
- [Characteristic 2 - e.g., "Lazy loading supported"]

**Optimization Options**:
- [Optimization 1]: [Description and impact]
- [Optimization 2]: [Description and impact]

### Scalability

**Scaling Characteristics**:
- **Vertical Scaling**: [How it scales with more resources]
- **Horizontal Scaling**: [How it scales with more instances]
- **Known Limits**: [Any documented limits]

**Resource Requirements**:
- **CPU**: [Typical CPU usage]
- **Memory**: [Typical memory usage]
- **Storage**: [Storage requirements if applicable]
- **Network**: [Network requirements if applicable]

---

## Security

### Known Vulnerabilities

**CVE History**:
| CVE ID | Severity | Affected Versions | Patched In | Mitigation |
|--------|----------|-------------------|------------|------------|
| [CVE-YYYY-XXXXX] | [Critical/High/Medium/Low] | [Versions] | [Version] | [What we need to do] |
| None found | N/A | N/A | N/A | ✅ No known CVEs |

**Security Advisories**: [Link to security advisory page or "None"]

### Security Features

**Built-in Security**:
- [Security feature 1 - e.g., "Input sanitization"]
- [Security feature 2 - e.g., "XSS protection"]
- [Security feature 3 - e.g., "CSRF tokens"]

**Authentication Support**:
- [Auth method 1 - e.g., "OAuth 2.0"]
- [Auth method 2 - e.g., "JWT"]

**Encryption**:
- **In Transit**: [TLS version support]
- **At Rest**: [Encryption options if applicable]

### Security Best Practices

**Official Recommendations**:
1. [Best practice 1]
2. [Best practice 2]
3. [Best practice 3]

**Security Considerations for Our Use Case**:
- [Consideration 1]
- [Consideration 2]

**Compliance**:
- **GDPR**: [Compliant / Needs configuration / Not applicable]
- **HIPAA**: [Compliant / Needs configuration / Not applicable]
- **SOC 2**: [Status]

---

## Dependencies

### Runtime Dependencies

| Package | Version Required | Why Needed | License | Concerns |
|---------|------------------|------------|---------|----------|
| [Package 1] | [^X.Y.Z] | [Purpose] | [License] | [Any concerns or "None"] |
| [Package 2] | [~X.Y.Z] | [Purpose] | [License] | [Any concerns or "None"] |

**Total Dependency Count**: [Direct: X, Transitive: Y]

### Peer Dependencies

| Package | Version Required | We Have | Compatible? |
|---------|------------------|---------|-------------|
| [Package 1] | [Version range] | [Our version] | ✅ Yes |
| [Package 2] | [Version range] | [Our version] | ❌ No - [Issue] |

### Compatibility Matrix

**Version Compatibility**:
```markdown
[Technology Name] [Version]
├── Node.js: ≥[X.Y] (We have: [Our version]) ✅
├── TypeScript: ≥[X.Y] (We have: [Our version]) ✅
├── React: [Version range] (We have: [Our version]) ⚠️
└── [Other dependency]: [Requirement] (We have: [Our version]) ✅
```

**Breaking Changes to Watch**:
- [Upcoming breaking change 1]
- [Upcoming breaking change 2]

---

## Community and Ecosystem

### Community Health

| Metric | Value | Assessment |
|--------|-------|------------|
| GitHub Stars | [Count] | [Large / Medium / Small] |
| Contributors | [Count] | [Active / Moderate / Limited] |
| Weekly Downloads | [Count] | [Very High / High / Medium / Low] |
| Open Issues | [Count] | [Manageable / Concerning] |
| Issue Response Time | [Average days] | [Good / Acceptable / Poor] |
| Last Commit | [Date] | [Active / Stale] |
| Last Release | [Date] | [Active / Stale] |

**Maintenance Status**: [Active / Maintenance Mode / Deprecated]

### Ecosystem

**Available Integrations**:
- [Integration 1]: [Description]
- [Integration 2]: [Description]

**Available Plugins/Extensions**:
- [Plugin 1]: [Purpose]
- [Plugin 2]: [Purpose]

**Tooling Support**:
- **IDE Support**: [VS Code / WebStorm / etc.]
- **Linting**: [ESLint / Pylint / etc.]
- **Formatting**: [Prettier / Black / etc.]
- **Testing**: [Jest / pytest / etc.]
- **Build Tools**: [Webpack / Vite / etc.]

**Learning Resources**:
- Official tutorial: [Link]
- Official examples: [Link]
- Community courses: [Link if notable]
- Books: [If any are definitive]

---

## Limitations and Gotchas

### Known Limitations

1. **[Limitation 1]**
   - Impact: [High / Medium / Low]
   - Affects us: [Yes / No]
   - Workaround: [If available]

2. **[Limitation 2]**
   - Impact: [High / Medium / Low]
   - Affects us: [Yes / No]
   - Workaround: [If available]

### Common Gotchas

- **[Gotcha 1]**: [Description and how to avoid]
- **[Gotcha 2]**: [Description and how to avoid]

### What It Doesn't Do Well

- [Weakness 1]
- [Weakness 2]

---

## Migration and Upgrade Path

### Upgrade Path

**Current Stable**: v[X.Y.Z]
**Next Major**: v[X+1].0.0 (Expected: [Date or "Unknown"])

**Migration Difficulty**:
- **Minor versions**: [Easy / Moderate / Difficult]
- **Major versions**: [Easy / Moderate / Difficult]

**Breaking Changes History**:
| From Version | To Version | Breaking Changes | Migration Guide |
|--------------|------------|------------------|-----------------|
| v[X] | v[Y] | [Summary] | [Link to guide] |

**Deprecation Warnings** (in current version):
- [Deprecated feature 1]: Removed in v[X] - Use [alternative]
- [Deprecated feature 2]: Removed in v[X] - Use [alternative]

---

## Trade-Off Analysis

### Strengths

1. **[Strength 1]**
   - Why it matters: [Explanation]
   - Evidence: [Benchmark, feature, or source]

2. **[Strength 2]**
   - Why it matters: [Explanation]
   - Evidence: [Benchmark, feature, or source]

### Weaknesses

1. **[Weakness 1]**
   - Why it matters: [Explanation]
   - Evidence: [Limitation or source]
   - Mitigation: [How we can address this]

2. **[Weakness 2]**
   - Why it matters: [Explanation]
   - Evidence: [Limitation or source]
   - Mitigation: [How we can address this]

### Trade-Offs

**Choosing This Means**:
- ✅ We gain: [Benefit 1]
- ✅ We gain: [Benefit 2]
- ❌ We give up: [Alternative benefit]
- ❌ We accept: [Limitation or complexity]

---

## Recommendation

### Decision

**Status**: [✅ Recommended / ❌ Not Recommended / ⚠️ Conditional]

**Confidence Level**: [High / Medium / Low]

### Rationale

[Clear, evidence-based explanation of the recommendation. Reference specific requirements, benchmarks, or tests that support this decision.]

**Key Decision Factors**:
1. [Factor 1 that led to this decision]
2. [Factor 2 that led to this decision]
3. [Factor 3 that led to this decision]

### Conditions (if conditional recommendation)

This technology is recommended IF:
- [ ] [Condition 1]
- [ ] [Condition 2]

This technology is NOT recommended IF:
- [ ] [Condition that would invalidate recommendation]

### Alternatives Considered

| Alternative | Why Not Chosen | When to Reconsider |
|-------------|----------------|-------------------|
| [Alternative 1] | [Reason] | [Condition] |
| [Alternative 2] | [Reason] | [Condition] |

---

## Next Steps for Architect Phase

**Architectural Considerations**:
1. [Consideration 1 - e.g., "Design service layer to abstract this technology"]
2. [Consideration 2 - e.g., "Plan for caching to mitigate latency"]

**Design Decisions Needed**:
- [ ] [Decision 1 - e.g., "Choose between REST and GraphQL API"]
- [ ] [Decision 2 - e.g., "Determine authentication strategy"]

**Integration Points**:
- [Integration point 1]: [Description]
- [Integration point 2]: [Description]

**Risks to Address in Architecture**:
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

---

## Research Sources

### Primary Sources

1. **Official Documentation**
   - URL: [Link]
   - Date Accessed: [YYYY-MM-DD]
   - Version: [Version]

2. **Official Repository**
   - URL: [Link]
   - Date Accessed: [YYYY-MM-DD]

### Secondary Sources

1. **[Source Name]**
   - URL: [Link]
   - Author: [Name]
   - Date: [YYYY-MM-DD]
   - Used for: [What information was extracted]

### Testing and Validation

- Sandbox/POC repository: [Link if applicable]
- Test results: [Link or summary]
- Date tested: [YYYY-MM-DD]
- Environment: [Details]

---

## Appendix

### Test Results

[Include any test outputs, benchmark results, or POC findings]

### Code Examples

[Include working code examples that were tested during research]

### Additional Notes

[Any other relevant information that doesn't fit in above sections]
```

---

## Template 2: API Documentation

**File**: `docs/preparation/api-documentation-[api-name].md`

```markdown
# API Documentation: [API Name]

**Research Date**: [YYYY-MM-DD]
**Researcher**: [Name]
**API Version**: [Version]
**Base URL**: [Production base URL]
**Documentation URL**: [Official docs link]
**Status Page**: [Status page link or "None"]

---

## Executive Summary

[2-3 paragraphs explaining what this API provides, why we need it, key capabilities, and integration approach]

**Key Endpoints Used**:
- [Endpoint 1]: [Purpose]
- [Endpoint 2]: [Purpose]

**Integration Complexity**: [Low / Medium / High]

---

## Authentication

### Authentication Method

**Type**: [API Key / OAuth 2.0 / JWT / Basic Auth / Custom]

**Flow**: [Description of authentication flow]

### Setup Instructions

**Step 1: Obtain Credentials**
```markdown
1. [How to get API credentials]
2. [What information is needed]
3. [Where credentials are displayed]
```

**Step 2: Configure Application**
```bash
# Environment variables
API_KEY=[your-api-key]
API_SECRET=[your-api-secret]
API_BASE_URL=[base-url]
```

**Step 3: Test Authentication**
```[language]
// Example authentication code
const client = new APIClient({
  apiKey: process.env.API_KEY,
  apiSecret: process.env.API_SECRET
});

// Test connection
const result = await client.authenticate();
console.log('Authenticated:', result.success);
```

### Authentication Details

**Headers Required**:
```http
Authorization: Bearer [token]
Content-Type: application/json
X-API-Key: [api-key]
```

**Token Lifetime**: [Duration]
**Refresh Mechanism**: [How to refresh tokens]

### Security Considerations

- **Credential Storage**: [Where to store - env vars, secrets manager, etc.]
- **Rotation Policy**: [How often to rotate credentials]
- **Scope/Permissions**: [What permissions are needed]
- **IP Restrictions**: [Any IP allowlisting required]

---

## Endpoints

### Endpoint: [Endpoint Name]

**Purpose**: [What this endpoint does and when to use it]

**HTTP Method**: `[GET / POST / PUT / DELETE / PATCH]`

**URL Pattern**: `[Base URL]/[path]/[resource]`

**Full Example**: `https://api.example.com/v1/users/123`

#### Request

**Headers**:
```http
Authorization: Bearer [token]
Content-Type: application/json
X-Custom-Header: [value]
```

**Path Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| [param1] | string | Yes | [Description] | `"abc123"` |

**Query Parameters**:
| Parameter | Type | Required | Default | Description | Example |
|-----------|------|----------|---------|-------------|---------|
| [param1] | string | No | [default] | [Description] | `"value"` |
| limit | integer | No | 10 | Results per page | `20` |
| offset | integer | No | 0 | Pagination offset | `40` |

**Request Body** (if applicable):
```json
{
  "field1": "string",
  "field2": 123,
  "nested": {
    "subfield": "value"
  },
  "array": ["item1", "item2"]
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| field1 | string | Yes | Max 255 chars | [Description] |
| field2 | integer | Yes | Min: 1, Max: 100 | [Description] |
| nested.subfield | string | No | Enum: ["a","b","c"] | [Description] |

#### Response

**Success Response (200 OK)**:
```json
{
  "id": "abc123",
  "field1": "value",
  "field2": 123,
  "created_at": "2025-12-04T12:00:00Z",
  "updated_at": "2025-12-04T12:00:00Z"
}
```

**Response Schema**:
| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| id | string | Yes | Unique identifier |
| field1 | string | Yes | [Description] |
| created_at | ISO 8601 datetime | Yes | Creation timestamp |

**Other Success Codes**:
- **201 Created**: [When returned]
- **204 No Content**: [When returned]

#### Error Responses

**400 Bad Request**:
```json
{
  "error": "InvalidRequest",
  "message": "field1 is required",
  "details": {
    "field": "field1",
    "issue": "missing"
  }
}
```
**When**: [Conditions that cause this error]

**401 Unauthorized**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```
**When**: [Conditions that cause this error]

**404 Not Found**:
```json
{
  "error": "NotFound",
  "message": "Resource with id abc123 not found"
}
```
**When**: [Conditions that cause this error]

**429 Too Many Requests**:
```json
{
  "error": "RateLimitExceeded",
  "message": "Rate limit exceeded. Retry after 60 seconds",
  "retry_after": 60
}
```
**When**: [Rate limit details]

**500 Internal Server Error**:
```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "request_id": "req_123"
}
```
**When**: [Server-side errors - how to report]

#### Rate Limits

**Limits**:
- **Rate**: [X requests per Y seconds/minutes]
- **Quota**: [Daily or monthly limit]
- **Burst**: [Burst allowance if applicable]

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701691200
```

**Handling Rate Limits**:
```[language]
// Example retry logic with exponential backoff
async function callAPIWithRetry(request) {
  let retryAfter = 1;
  while (true) {
    try {
      return await makeRequest(request);
    } catch (error) {
      if (error.status === 429) {
        await sleep(retryAfter * 1000);
        retryAfter *= 2; // Exponential backoff
      } else {
        throw error;
      }
    }
  }
}
```

#### Pagination

**Pagination Type**: [Offset-based / Cursor-based / Page-based]

**Example Request**:
```http
GET /v1/resources?limit=20&offset=40
```

**Example Response**:
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "limit": 20,
    "offset": 40,
    "next_offset": 60,
    "has_more": true
  }
}
```

**Pagination Logic**:
```[language]
// Example pagination implementation
async function getAllPages() {
  let allResults = [];
  let offset = 0;
  const limit = 100;

  while (true) {
    const response = await api.get(`/resources?limit=${limit}&offset=${offset}`);
    allResults = allResults.concat(response.data);

    if (!response.pagination.has_more) break;
    offset = response.pagination.next_offset;
  }

  return allResults;
}
```

#### Filtering and Sorting

**Filter Parameters**:
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| filter[field] | string | [How filtering works] | `filter[status]=active` |
| q | string | Full-text search | `q=search+term` |

**Sort Parameters**:
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| sort | string | Sort field(s) | `sort=created_at` |
| order | string | Sort order | `order=desc` |

#### Example Usage

**cURL Example**:
```bash
curl -X POST https://api.example.com/v1/resources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field1": "value",
    "field2": 123
  }'
```

**SDK Example** (if official SDK available):
```[language]
const client = new APIClient({ apiKey: process.env.API_KEY });

const result = await client.resources.create({
  field1: 'value',
  field2: 123
});

console.log('Created resource:', result.id);
```

**JavaScript/TypeScript Example**:
```typescript
const response = await fetch('https://api.example.com/v1/resources', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    field1: 'value',
    field2: 123
  })
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(`API Error: ${error.message}`);
}

const data = await response.json();
console.log('Created:', data.id);
```

---

[Repeat **Endpoint** section for each critical endpoint]

---

## Webhooks

### Webhook Overview

**Support**: [Yes / No]
**Purpose**: [What events can be subscribed to]

### Webhook Configuration

**Setup**:
1. [How to configure webhook in dashboard/API]
2. [What URL format is needed]
3. [How to verify webhook signature]

**Webhook URL Requirements**:
- Must be HTTPS
- Must respond within [X seconds]
- Must return 200 status for successful receipt

### Webhook Payload

**Headers**:
```http
X-Webhook-Signature: [signature]
X-Event-Type: [event.type]
Content-Type: application/json
```

**Payload Format**:
```json
{
  "event": "resource.created",
  "timestamp": "2025-12-04T12:00:00Z",
  "data": {
    "id": "abc123",
    "field1": "value"
  }
}
```

**Signature Verification**:
```[language]
// Example signature verification
function verifyWebhook(payload, signature, secret) {
  const computed = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(computed)
  );
}
```

### Event Types

| Event Type | Description | When Fired |
|------------|-------------|------------|
| resource.created | Resource created | [Trigger condition] |
| resource.updated | Resource updated | [Trigger condition] |
| resource.deleted | Resource deleted | [Trigger condition] |

### Webhook Best Practices

- [ ] Verify webhook signature
- [ ] Respond quickly (200 OK), process asynchronously
- [ ] Implement idempotency (handle duplicate deliveries)
- [ ] Log webhook receipts for debugging
- [ ] Handle webhook retries gracefully

---

## SDK / Client Libraries

### Official SDKs

| Language | Package | Version | Documentation |
|----------|---------|---------|---------------|
| JavaScript | [@vendor/sdk-js](link) | v[X.Y.Z] | [Docs link] |
| Python | [vendor-sdk-python](link) | v[X.Y.Z] | [Docs link] |
| Ruby | [vendor-sdk-ruby](link) | v[X.Y.Z] | [Docs link] |

### Recommended SDK

**Choice**: [JavaScript SDK]
**Reason**: [Why this SDK for our project]

**Installation**:
```bash
npm install @vendor/sdk-js
```

**Basic Usage**:
```[language]
const { APIClient } = require('@vendor/sdk-js');

const client = new APIClient({
  apiKey: process.env.API_KEY,
  environment: 'production'
});

// Example operation
const result = await client.resources.list({ limit: 10 });
```

---

## Error Handling Strategy

### Error Response Format

**Standard Error Structure**:
```json
{
  "error": "ErrorCode",
  "message": "Human-readable message",
  "details": {},
  "request_id": "req_abc123"
}
```

### Error Codes

| Error Code | HTTP Status | Meaning | Action |
|------------|-------------|---------|--------|
| InvalidRequest | 400 | Malformed request | Fix request format |
| Unauthorized | 401 | Invalid credentials | Re-authenticate |
| Forbidden | 403 | Insufficient permissions | Check permissions |
| NotFound | 404 | Resource doesn't exist | Check resource ID |
| RateLimitExceeded | 429 | Too many requests | Implement backoff |
| InternalServerError | 500 | Server error | Retry with backoff |

### Retry Strategy

**When to Retry**:
- 429 Rate Limit Exceeded
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

**Retry Logic**:
```[language]
async function retryWithBackoff(operation, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      const isRetryable = [429, 500, 502, 503, 504].includes(error.status);
      const isLastAttempt = attempt === maxRetries - 1;

      if (!isRetryable || isLastAttempt) {
        throw error;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt) * 1000;
      await sleep(delay);
    }
  }
}
```

### Error Logging

**Log Format**:
```json
{
  "timestamp": "2025-12-04T12:00:00Z",
  "level": "error",
  "message": "API request failed",
  "context": {
    "endpoint": "/v1/resources",
    "method": "POST",
    "status": 400,
    "error_code": "InvalidRequest",
    "request_id": "req_abc123",
    "response_body": {...}
  }
}
```

---

## Testing

### Sandbox Environment

**Base URL**: [Sandbox URL]
**Credentials**: [How to obtain test credentials]
**Test Data**: [What test data is available]
**Limitations**: [What doesn't work in sandbox]

### Test Scenarios

**Test 1: Successful Request**
```[language]
// Test creating a resource
const result = await api.resources.create({ field1: 'test' });
assert(result.id);
assert(result.field1 === 'test');
```

**Test 2: Invalid Request (400)**
```[language]
// Test validation error
try {
  await api.resources.create({ field1: '' }); // Invalid
  assert.fail('Should have thrown error');
} catch (error) {
  assert(error.status === 400);
  assert(error.code === 'InvalidRequest');
}
```

**Test 3: Rate Limiting (429)**
```[language]
// Test rate limit handling
let rateLimitHit = false;
for (let i = 0; i < 200; i++) {
  try {
    await api.resources.list();
  } catch (error) {
    if (error.status === 429) {
      rateLimitHit = true;
      break;
    }
  }
}
assert(rateLimitHit);
```

---

## Performance and Limits

### Response Times

| Endpoint | Average | P95 | P99 |
|----------|---------|-----|-----|
| GET /resources | [X ms] | [X ms] | [X ms] |
| POST /resources | [X ms] | [X ms] | [X ms] |

**Source**: [Official SLA / Our testing / Status page]

### Rate Limits Summary

| Endpoint | Limit | Period | Burst |
|----------|-------|--------|-------|
| All endpoints | [X requests] | [per minute/hour] | [X] |
| Specific endpoint | [X requests] | [per minute/hour] | [X] |

### Quotas

- **Daily Quota**: [X requests per day]
- **Monthly Quota**: [X requests per month]
- **Overage Handling**: [What happens if exceeded]

---

## Security

### Security Best Practices

1. **Credential Management**
   - Store API keys in environment variables
   - Never commit credentials to version control
   - Rotate keys every [X months]

2. **HTTPS Only**
   - All requests must use HTTPS
   - TLS 1.2+ required

3. **Request Signing** (if applicable)
   - [How to sign requests]
   - [What algorithm to use]

4. **IP Allowlisting** (if available)
   - [How to configure]
   - [Our production IPs]

### Compliance

- **Data Residency**: [Where data is stored]
- **Privacy**: [GDPR compliance status]
- **Certifications**: [SOC 2, ISO 27001, etc.]

### Vulnerability Reporting

**Security Contact**: [security@vendor.com]
**Disclosure Policy**: [Link to responsible disclosure]

---

## Monitoring and Observability

### Status Monitoring

**Status Page**: [URL]
**Incident History**: [Recent incidents]
**Uptime SLA**: [Guaranteed uptime]

### Metrics to Track

```markdown
Application should monitor:
- [ ] API response times (by endpoint)
- [ ] Error rates (by status code)
- [ ] Rate limit usage
- [ ] Daily/monthly quota usage
- [ ] Webhook delivery success rate
```

### Logging Strategy

**What to Log**:
- All API requests (endpoint, method, status, duration)
- All errors (with request_id for vendor support)
- Rate limit headers
- Webhook receipts

**Sample Log Entry**:
```json
{
  "timestamp": "2025-12-04T12:00:00Z",
  "service": "api-client",
  "level": "info",
  "message": "API request completed",
  "endpoint": "/v1/resources",
  "method": "POST",
  "status": 201,
  "duration_ms": 145,
  "request_id": "req_abc123",
  "rate_limit_remaining": 95
}
```

---

## Cost Analysis

### Pricing Model

**Pricing Type**: [Free tier / Pay-per-use / Subscription]

**Pricing Tiers**:
| Tier | Requests/Month | Cost | Notes |
|------|----------------|------|-------|
| Free | [X] | $0 | [Limitations] |
| Standard | [X] | $[Y]/month | [Features] |
| Premium | [X] | $[Y]/month | [Features] |

**Overage Costs**: $[X] per [Y] requests over quota

### Estimated Costs for Our Use Case

**Expected Usage**: [X requests per month]
**Recommended Tier**: [Tier name]
**Estimated Monthly Cost**: $[X]

**Cost Optimization**:
- [Strategy 1 - e.g., "Cache frequently accessed data"]
- [Strategy 2 - e.g., "Batch requests where possible"]

---

## Integration Recommendations

### Integration Architecture

**Approach**: [Direct integration / Facade pattern / Queue-based]

**Rationale**: [Why this approach]

**Components Needed**:
1. [Component 1 - e.g., "API client wrapper"]
2. [Component 2 - e.g., "Retry middleware"]
3. [Component 3 - e.g., "Webhook handler"]

### Error Handling Strategy

1. **Retry transient errors** (429, 500, 502, 503, 504)
2. **Log all errors** with request_id for support
3. **Fail fast on** validation errors (400, 401, 403, 404)
4. **Alert on** repeated failures or quota exceeded

### Caching Strategy

**What to Cache**:
- [Data type 1]: Cache for [duration]
- [Data type 2]: Cache for [duration]

**Cache Invalidation**:
- [Trigger 1]: Clear cache
- [Trigger 2]: Clear cache

---

## Next Steps for Architect Phase

### Architectural Decisions Needed

- [ ] [Decision 1 - e.g., "Design API client facade interface"]
- [ ] [Decision 2 - e.g., "Determine retry and circuit breaker strategy"]
- [ ] [Decision 3 - e.g., "Plan webhook processing queue architecture"]

### Integration Points

| Our Component | API Endpoint(s) | Data Flow |
|---------------|-----------------|-----------|
| [Component 1] | [Endpoint(s)] | [Direction and description] |
| [Component 2] | [Endpoint(s)] | [Direction and description] |

### Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | [High/Med/Low] | [High/Med/Low] | [Strategy] |
| Rate limit exceeded | High | Medium | Implement request queue with rate limiting |
| API downtime | High | Low | Implement circuit breaker, cache fallback |

---

## Research Sources

1. **Official API Documentation**
   - URL: [Link]
   - Version: [Version]
   - Date Accessed: [YYYY-MM-DD]

2. **API Status Page**
   - URL: [Link]
   - Date Accessed: [YYYY-MM-DD]

3. **Official SDK Documentation**
   - URL: [Link]
   - Date Accessed: [YYYY-MM-DD]

4. **Testing Results**
   - Sandbox testing completed: [Date]
   - Test repository: [Link]

---

## Appendix

### Complete API Reference

[Link to full API reference or embed additional endpoints]

### Example Integration Code

[Link to POC repository or embed complete working example]

### Troubleshooting Guide

**Common Issues**:
1. **Authentication failures**
   - Check: [Checklist]

2. **Rate limit errors**
   - Check: [Checklist]
```

---

## Template 3: Technology Comparison Matrix

**File**: `docs/preparation/technology-comparison.md`

```markdown
# Technology Comparison: [Category]

**Research Date**: [YYYY-MM-DD]
**Researcher**: [Name]
**Decision**: [Which technology was chosen]

---

## Executive Summary

[2-3 paragraphs explaining what technologies were compared, why, the evaluation process, and the recommendation]

**Recommendation**: [Technology Name] based on [key factor(s)]

---

## Technologies Compared

| Technology | Version | Official Site | License |
|------------|---------|---------------|---------|
| [Option A] | [Version] | [URL] | [License] |
| [Option B] | [Version] | [URL] | [License] |
| [Option C] | [Version] | [URL] | [License] |

---

## Evaluation Criteria

| Criterion | Weight | Description | Why It Matters |
|-----------|--------|-------------|----------------|
| [Criterion 1] | High (3x) | [Description] | [Importance to project] |
| [Criterion 2] | High (3x) | [Description] | [Importance to project] |
| [Criterion 3] | Medium (2x) | [Description] | [Importance to project] |
| [Criterion 4] | Low (1x) | [Description] | [Importance to project] |

**Weight Legend**:
- High (3x): Critical to project success
- Medium (2x): Important but not blocking
- Low (1x): Nice to have

---

## Comparison Matrix

| Criterion | Weight | [Option A] | [Option B] | [Option C] | Notes |
|-----------|--------|------------|------------|------------|-------|
| **Functional Requirements** |||||
| [Requirement 1] | High | ✅ Yes | ⚠️ Partial | ❌ No | [Context] |
| [Requirement 2] | High | ✅ Yes | ✅ Yes | ✅ Yes | [Context] |
| [Requirement 3] | Medium | ⚠️ Plugin | ✅ Yes | ❌ No | [Context] |
| **Performance** |||||
| Response Time | High | ⭐⭐⭐⭐ (4) | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐ (3) | [Benchmark source] |
| Throughput | High | ⭐⭐⭐ (3) | ⭐⭐⭐⭐ (4) | ⭐⭐⭐⭐⭐ (5) | [Benchmark source] |
| Bundle Size (if FE) | Medium | ⭐⭐⭐ (3) | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐⭐ (4) | [Size comparison] |
| **Security** |||||
| Built-in Security | High | ⭐⭐⭐⭐ (4) | ⭐⭐⭐ (3) | ⭐⭐⭐⭐⭐ (5) | [Features] |
| CVE History | High | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐⭐ (4) | ⭐⭐⭐ (3) | [Few/none] |
| **Developer Experience** |||||
| Learning Curve | Medium | Moderate (2) | Steep (1) | Easy (3) | [Team assessment] |
| Documentation | High | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐⭐ (4) | ⭐⭐⭐ (3) | [Quality rating] |
| DX Tooling | Medium | ⭐⭐⭐⭐ (4) | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐ (3) | [IDE support, etc.] |
| **Ecosystem** |||||
| Community Size | Medium | Large (4) | Medium (3) | Small (2) | [GitHub stars, downloads] |
| Plugin Ecosystem | Medium | ⭐⭐⭐⭐ (4) | ⭐⭐⭐⭐⭐ (5) | ⭐⭐ (2) | [Available plugins] |
| **Operational** |||||
| Maintenance Status | High | Active (5) | Active (5) | Stale (2) | [Last commit date] |
| Breaking Changes | Medium | Few (4) | Frequent (2) | None (5) | [Stability] |
| License | High | MIT (5) | Apache (5) | GPL (1) | [Compatibility] |
| **Total Score** || **[X]** | **[Y]** | **[Z]** | Weighted total |

**Scoring Legend**:
- ✅ Fully supported (3)
- ⚠️ Partial support (2)
- ❌ Not supported (0)
- ⭐ Rating scale (1-5 stars)

---

## Weighted Score Calculation

### [Option A] Total Score

```
Functional Requirements:
  Requirement 1: 3 × 3 = 9
  Requirement 2: 3 × 3 = 9
  Requirement 3: 2 × 2 = 4
Performance:
  Response Time: 4 × 3 = 12
  Throughput: 3 × 3 = 9
  Bundle Size: 3 × 2 = 6
Security:
  Built-in Security: 4 × 3 = 12
  CVE History: 5 × 3 = 15
Developer Experience:
  Learning Curve: 2 × 2 = 4
  Documentation: 5 × 3 = 15
  DX Tooling: 4 × 2 = 8
Ecosystem:
  Community Size: 4 × 2 = 8
  Plugin Ecosystem: 4 × 2 = 8
Operational:
  Maintenance Status: 5 × 3 = 15
  Breaking Changes: 4 × 2 = 8
  License: 5 × 3 = 15

Total: 157
```

### [Option B] Total Score

[Similar calculation]

Total: [Score]

### [Option C] Total Score

[Similar calculation]

Total: [Score]

---

## Detailed Analysis

### [Option A]: [Technology Name]

#### Strengths
- **[Strength 1]**: [Description with evidence]
- **[Strength 2]**: [Description with evidence]
- **[Strength 3]**: [Description with evidence]

#### Weaknesses
- **[Weakness 1]**: [Description with evidence]
- **[Weakness 2]**: [Description with evidence]

#### Trade-Offs
**Choosing this means**:
- ✅ We gain: [Benefit]
- ✅ We gain: [Benefit]
- ❌ We give up: [Alternative benefit]
- ❌ We accept: [Limitation]

#### Best For
- [Scenario where this excels]
- [Another ideal use case]

#### Avoid If
- [Scenario where this is not suitable]
- [Another poor fit]

---

[Repeat **Detailed Analysis** section for Option B and Option C]

---

## Side-by-Side Feature Comparison

| Feature | [Option A] | [Option B] | [Option C] |
|---------|------------|------------|------------|
| [Feature 1] | ✅ Built-in | ⚠️ Plugin | ❌ None |
| [Feature 2] | ⚠️ Beta | ✅ Stable | ✅ Stable |
| [Feature 3] | ✅ Yes | ✅ Yes | ✅ Yes |
| [Feature 4] | ❌ No | ✅ Yes | ⚠️ Workaround |

---

## Migration and Upgrade Paths

| Technology | Minor Version Upgrades | Major Version Upgrades | Notes |
|------------|----------------------|----------------------|-------|
| [Option A] | [Easy/Moderate/Hard] | [Easy/Moderate/Hard] | [Details] |
| [Option B] | [Easy/Moderate/Hard] | [Easy/Moderate/Hard] | [Details] |
| [Option C] | [Easy/Moderate/Hard] | [Easy/Moderate/Hard] | [Details] |

---

## Recommendation

### Final Decision

**Recommended Technology**: [Technology Name]

**Confidence Level**: [High / Medium / Low]

### Rationale

[Detailed explanation of why this technology was chosen, referencing specific criteria, scores, and requirements]

**Key Decision Factors**:
1. [Factor 1 with evidence]
2. [Factor 2 with evidence]
3. [Factor 3 with evidence]

### Runner-Up

**Second Choice**: [Technology Name]

**When to Reconsider**: [Conditions under which runner-up might be better]

### Alternatives Ruled Out

**[Technology Name]**: Ruled out because [specific reason]

---

## Risk Assessment

| Risk | Technology | Severity | Likelihood | Mitigation |
|------|-----------|----------|------------|------------|
| [Risk 1] | [Chosen tech] | [H/M/L] | [H/M/L] | [Strategy] |
| [Risk 2] | [Chosen tech] | [H/M/L] | [H/M/L] | [Strategy] |

---

## Next Steps for Architect Phase

1. [Action item 1 based on chosen technology]
2. [Action item 2]
3. [Architectural decision needed]

---

## Research Sources

### [Option A] Sources
1. [Source 1]
2. [Source 2]

### [Option B] Sources
1. [Source 1]
2. [Source 2]

### [Option C] Sources
1. [Source 1]
2. [Source 2]

### Comparison Resources
1. [Benchmark or comparison source]
2. [Community comparison or discussion]

---

## Appendix

### Test Results

[Include any POC or benchmark results that informed the decision]

### Team Feedback

[Include any input from team members on learning curve, preferences, etc.]
```

---

## Using These Templates

### Template Selection Guide

| Need to Document | Use Template |
|------------------|--------------|
| Single technology evaluation | Technology Research Summary |
| Third-party API integration | API Documentation |
| Comparing 2+ options | Technology Comparison Matrix |
| All dependencies | [Create custom based on needs] |
| Security findings | [Adapt Technology Research template] |
| Requirements | [Use Requirements Analysis structure] |

### Customization Guidelines

**Always Include**:
- Research date and researcher name
- Version information for all technologies
- Links to sources
- Evidence for claims (tests, benchmarks, quotes)

**Adapt As Needed**:
- Remove sections that don't apply
- Add project-specific criteria
- Adjust detail level based on decision importance

**Quality Standards**:
- Be specific and concrete
- Cite sources
- Show your work (how you reached conclusions)
- Document assumptions
- Include working code examples where applicable

---

This completes the documentation templates for the Prepare phase. Use these templates to ensure consistent, comprehensive research documentation that enables informed architectural decisions.
