# API Versioning Strategies

Comprehensive guide to API versioning approaches, migration strategies, and deprecation policies.

## Table of Contents

1. [Versioning Overview](#versioning-overview)
2. [URL Versioning](#url-versioning)
3. [Header Versioning](#header-versioning)
4. [Query Parameter Versioning](#query-parameter-versioning)
5. [Content Negotiation Versioning](#content-negotiation-versioning)
6. [Semantic Versioning](#semantic-versioning)
7. [Breaking vs Non-Breaking Changes](#breaking-vs-non-breaking-changes)
8. [Migration Strategies](#migration-strategies)
9. [Deprecation Policies](#deprecation-policies)
10. [Version Comparison](#version-comparison)

## Versioning Overview

### Why Version APIs?

APIs evolve over time due to:
- New features and functionality
- Bug fixes requiring contract changes
- Performance improvements
- Security updates
- Business requirement changes

Without versioning:
- Breaking changes disrupt all clients immediately
- Clients can't control when they upgrade
- No time to adapt to changes
- Risk of service disruption

### Versioning Goals

1. **Backward Compatibility**: Old clients continue working while new clients use new features
2. **Controlled Migration**: Clients upgrade on their schedule
3. **Clear Communication**: Changes are documented and communicated
4. **Graceful Deprecation**: Old versions have clear end-of-life timeline

## URL Versioning

### Format

Include version in the URL path:
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### Implementation Example

```javascript
// Express.js router setup
const v1Router = require('./routes/v1');
const v2Router = require('./routes/v2');

app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// v1/users.js
router.get('/users', async (req, res) => {
  const users = await User.find();
  res.json(users.map(u => ({
    id: u.id,
    name: u.fullName,
    email: u.email
  })));
});

// v2/users.js
router.get('/users', async (req, res) => {
  const users = await User.find();
  res.json(users.map(u => ({
    id: u.id,
    firstName: u.firstName,  // v2: Split name into firstName/lastName
    lastName: u.lastName,
    email: u.email,
    createdAt: u.createdAt   // v2: Added timestamp
  })));
});
```

### Pros
- **Highly Visible**: Version is immediately obvious in URL
- **Easy to Test**: Can test different versions with simple URL changes
- **Browser-Friendly**: Works easily with browser developer tools
- **Cacheable**: Different URLs mean separate cache entries
- **Simple Routing**: Easy to route to different codebases

### Cons
- **URL Pollution**: Creates multiple endpoints for same resource
- **Client Hardcoding**: Clients must hardcode version in all requests
- **Migration Friction**: Changing versions requires updating all URLs
- **Resource Duplication**: Same resource at multiple URLs

### Best For
- Public APIs with many external consumers
- APIs where versioning should be very explicit
- RESTful APIs with stable, long-lived versions
- Teams comfortable maintaining multiple codebases

### Variations

**Major Version in Path, Minor in Header**:
```
URL: /api/v2/users
Header: X-API-Minor-Version: 3
Result: Using v2.3
```

**Date-Based Versions**:
```
/api/2025-01-15/users  # Version from January 15, 2025
/api/2025-06-01/users  # Version from June 1, 2025
```
Used by: Stripe, GitHub

## Header Versioning

### Format

Version specified in custom header:
```
GET /api/users
X-API-Version: 2
```

Or using standard Accept header:
```
GET /api/users
Accept: application/vnd.example.v2+json
```

### Implementation Example

```javascript
// Middleware to extract version from header
const versionMiddleware = (req, res, next) => {
  const version = req.headers['x-api-version'] || '1';
  req.apiVersion = parseInt(version);
  next();
};

app.use(versionMiddleware);

// Single endpoint with version-aware logic
router.get('/users', async (req, res) => {
  const users = await User.find();

  if (req.apiVersion === 1) {
    res.json(users.map(u => ({
      id: u.id,
      name: u.fullName,
      email: u.email
    })));
  } else if (req.apiVersion === 2) {
    res.json(users.map(u => ({
      id: u.id,
      firstName: u.firstName,
      lastName: u.lastName,
      email: u.email,
      createdAt: u.createdAt
    })));
  } else {
    res.status(400).json({ error: 'Unsupported API version' });
  }
});
```

### Pros
- **Clean URLs**: Same URL for all versions
- **Flexible**: Easy to add metadata beyond just version
- **RESTful**: Follows REST principles (same resource = same URL)
- **Backward Compatible**: Can default to latest or oldest version

### Cons
- **Less Visible**: Version not obvious from URL
- **Harder to Test**: Need to set headers in tools
- **Cache Complexity**: Must use Vary header for proper caching
- **Client Complexity**: Every request needs header

### Best For
- Internal APIs with controlled client base
- APIs following strict REST principles
- Scenarios where URL cleanliness is important
- Mobile apps that can easily set headers

### Caching Consideration

```javascript
// Must include Vary header so caches know to differentiate by version
router.get('/users', async (req, res) => {
  res.set('Vary', 'X-API-Version');
  // ... handle versioned response
});
```

## Query Parameter Versioning

### Format

Version as query parameter:
```
GET /api/users?version=2
GET /api/users?api-version=2.1
```

### Implementation Example

```javascript
router.get('/users', async (req, res) => {
  const version = parseFloat(req.query.version || '1.0');
  const users = await User.find();

  if (version >= 2.0) {
    // v2 response format
    res.json({
      data: users.map(u => ({
        id: u.id,
        firstName: u.firstName,
        lastName: u.lastName
      })),
      meta: { version: '2.0' }
    });
  } else {
    // v1 response format
    res.json(users.map(u => ({
      id: u.id,
      name: u.fullName
    })));
  }
});
```

### Pros
- **Simple**: Easy to understand and implement
- **Flexible**: Easy to test and change
- **Optional**: Can default if not provided
- **Analytics-Friendly**: Version visible in logs

### Cons
- **Not RESTful**: Query params should be for filtering, not versioning
- **URL Pollution**: Version mixed with functional parameters
- **Cache Keys**: Complicates cache key generation
- **Inconsistent**: Clients might forget to include version

### Best For
- Prototyping and experimentation
- Internal tools with flexible requirements
- Scenarios where backward compatibility is default
- **Generally not recommended for production APIs**

## Content Negotiation Versioning

### Format

Use Accept/Content-Type headers with vendor media types:
```
GET /api/users
Accept: application/vnd.example.user.v2+json
```

### Implementation Example

```javascript
const parseAcceptHeader = (accept) => {
  const match = accept.match(/application\/vnd\.example\.user\.v(\d+)\+json/);
  return match ? parseInt(match[1]) : 1;
};

router.get('/users', async (req, res) => {
  const version = parseAcceptHeader(req.headers.accept || '');
  const users = await User.find();

  const contentType = `application/vnd.example.user.v${version}+json`;
  res.set('Content-Type', contentType);

  if (version === 2) {
    res.json(/* v2 format */);
  } else {
    res.json(/* v1 format */);
  }
});
```

### Pros
- **HTTP Standard**: Uses standard HTTP content negotiation
- **Fine-Grained**: Can version individual resources differently
- **RESTful**: Aligns with REST architectural style
- **Flexible**: Can negotiate multiple dimensions (version, format, language)

### Cons
- **Complex**: Most complex approach to implement
- **Harder to Use**: Clients must craft proper Accept headers
- **Debugging**: Harder to debug and test
- **Limited Adoption**: Less common, so less familiar

### Best For
- Hypermedia-driven APIs (HATEOAS)
- APIs with sophisticated content negotiation needs
- Teams committed to pure REST principles
- Public APIs with diverse client needs

## Semantic Versioning

Apply semantic versioning principles to APIs:

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Examples

```
1.0.0 → 1.0.1  # Bug fix: Fixed date formatting
1.0.1 → 1.1.0  # New feature: Added search endpoint
1.1.0 → 2.0.0  # Breaking change: Removed deprecated fields
```

### Implementation Strategies

**URL with Major Version Only**:
```
/api/v1/users  # Could be v1.0.0, v1.5.0, v1.9.0
/api/v2/users  # Could be v2.0.0, v2.3.0
```

**Header with Full Version**:
```
X-API-Version: 1.5.2
```

**Response Header with Exact Version**:
```
Request: GET /api/v1/users
Response Header: X-API-Actual-Version: 1.5.2
```

## Breaking vs Non-Breaking Changes

### Breaking Changes (Require Version Bump)

1. **Removing Endpoints**:
   ```
   DELETE /api/v1/legacy-endpoint  # Breaking
   ```

2. **Removing Fields**:
   ```json
   // v1
   { "id": 123, "name": "John", "nickname": "Johnny" }

   // v2 - Removed nickname
   { "id": 123, "name": "John" }
   ```

3. **Changing Field Types**:
   ```json
   // v1
   { "id": "123" }  // String ID

   // v2
   { "id": 123 }  // Integer ID
   ```

4. **Renaming Fields**:
   ```json
   // v1
   { "user_id": 123 }

   // v2
   { "id": 123 }
   ```

5. **Changing Validation Rules** (more restrictive):
   ```
   v1: email is optional
   v2: email is required
   ```

6. **Changing Status Codes**:
   ```
   v1: Returns 200 OK for resource creation
   v2: Returns 201 Created for resource creation
   ```

7. **Changing Authentication**:
   ```
   v1: Basic auth
   v2: OAuth2 only
   ```

### Non-Breaking Changes (No Version Bump Required)

1. **Adding New Endpoints**:
   ```
   POST /api/v1/new-feature  # Non-breaking
   ```

2. **Adding Optional Fields**:
   ```json
   // v1
   { "id": 123, "name": "John" }

   // v1.1 - Added optional bio
   { "id": 123, "name": "John", "bio": "Engineer" }
   ```

3. **Adding Query Parameters**:
   ```
   // v1
   GET /api/v1/users

   // v1.1
   GET /api/v1/users?sort=name  # New optional parameter
   ```

4. **Relaxing Validation** (less restrictive):
   ```
   v1: Name must be 2-50 characters
   v1.1: Name must be 1-100 characters
   ```

5. **Adding New Values to Enums**:
   ```json
   // v1: status = "active" | "inactive"
   // v1.1: status = "active" | "inactive" | "pending"
   ```
   *Only if clients handle unknown values gracefully*

6. **Bug Fixes**:
   ```
   v1.0.1: Fixed incorrect date formatting
   ```

## Migration Strategies

### 1. Parallel Running

Run multiple versions simultaneously:

```javascript
// Shared data access layer
const userService = require('./services/userService');

// v1 transformer
const toV1User = (user) => ({
  id: user.id,
  name: user.fullName,
  email: user.email
});

// v2 transformer
const toV2User = (user) => ({
  id: user.id,
  firstName: user.firstName,
  lastName: user.lastName,
  email: user.email,
  createdAt: user.createdAt
});

// v1 route
app.get('/api/v1/users/:id', async (req, res) => {
  const user = await userService.getById(req.params.id);
  res.json(toV1User(user));
});

// v2 route
app.get('/api/v2/users/:id', async (req, res) => {
  const user = await userService.getById(req.params.id);
  res.json(toV2User(user));
});
```

### 2. Adapter Pattern

Use adapters to translate between versions:

```javascript
class UserV1Adapter {
  static fromDomain(user) {
    return {
      id: user.id,
      name: user.fullName,
      email: user.email
    };
  }

  static toDomain(v1User) {
    const [firstName, ...lastNameParts] = v1User.name.split(' ');
    return {
      firstName,
      lastName: lastNameParts.join(' '),
      email: v1User.email
    };
  }
}

class UserV2Adapter {
  static fromDomain(user) {
    return {
      id: user.id,
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email,
      createdAt: user.createdAt
    };
  }

  static toDomain(v2User) {
    return {
      firstName: v2User.firstName,
      lastName: v2User.lastName,
      email: v2User.email
    };
  }
}
```

### 3. Feature Flags

Use feature flags to gradually roll out changes:

```javascript
const featureFlags = require('./featureFlags');

router.get('/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);

  if (featureFlags.isEnabled('user-v2-response', req.user)) {
    res.json(toV2User(user));
  } else {
    res.json(toV1User(user));
  }
});
```

### 4. Proxy Pattern

Route requests through a version-aware proxy:

```javascript
const v1Handler = require('./v1/handler');
const v2Handler = require('./v2/handler');

const versionProxy = (req, res) => {
  const version = extractVersion(req);

  switch (version) {
    case 1:
      return v1Handler(req, res);
    case 2:
      return v2Handler(req, res);
    default:
      return res.status(400).json({ error: 'Unsupported version' });
  }
};

app.use('/api/users', versionProxy);
```

## Deprecation Policies

### Deprecation Timeline

Example policy:
1. **Announce**: 6 months before deprecation
2. **Warn**: Add deprecation warnings to responses
3. **Monitor**: Track usage of deprecated version
4. **Support**: Provide migration guide and tools
5. **Sunset**: Disable deprecated version

### Deprecation Headers

```javascript
router.get('/api/v1/users', (req, res) => {
  // Warn clients about deprecation
  res.set('Deprecation', 'true');
  res.set('Sunset', 'Sat, 01 Jun 2025 00:00:00 GMT');
  res.set('Link', '</api/v2/users>; rel="successor-version"');

  // ... handle request
});
```

### Deprecation Response

Include deprecation info in response:

```json
{
  "data": [...],
  "meta": {
    "deprecated": true,
    "sunset_date": "2025-06-01T00:00:00Z",
    "migration_guide": "https://api.example.com/docs/v1-to-v2-migration",
    "successor_version": "v2"
  }
}
```

### Communication Strategy

1. **Email Notifications**: Email all registered API consumers
2. **Developer Portal**: Update documentation with timeline
3. **Change Log**: Maintain public changelog
4. **Deprecation Notice**: Add banner to API docs
5. **Analytics**: Monitor usage and contact heavy users directly

### Graceful Shutdown

```javascript
const SUNSET_DATE = new Date('2025-06-01');

router.use('/api/v1', (req, res, next) => {
  if (new Date() > SUNSET_DATE) {
    return res.status(410).json({
      error: 'This API version has been sunset',
      sunset_date: SUNSET_DATE,
      migration_guide: 'https://api.example.com/docs/migration'
    });
  }
  next();
});
```

## Version Comparison

| Strategy | Visibility | Cache-Friendly | RESTful | Complexity | Best For |
|----------|-----------|----------------|---------|------------|----------|
| **URL Versioning** | High | Yes | No | Low | Public APIs, external clients |
| **Header Versioning** | Low | With Vary | Yes | Medium | Internal APIs, REST purists |
| **Query Parameter** | Medium | Complex | No | Low | Prototyping, not recommended |
| **Content Negotiation** | Low | With Vary | Yes | High | Hypermedia APIs, pure REST |

### Recommendation Matrix

**Choose URL Versioning if**:
- Building public API for external consumers
- Want maximum clarity and discoverability
- Comfortable maintaining separate codebases
- Cache performance is critical

**Choose Header Versioning if**:
- Building internal API for known clients
- Following strict REST principles
- URL cleanliness is important
- Clients can easily set headers

**Choose Content Negotiation if**:
- Building hypermedia-driven API (HATEOAS)
- Need fine-grained content negotiation
- Team has strong REST expertise
- Following Roy Fielding's vision

**Avoid Query Parameter Versioning** for production APIs.

### Hybrid Approach

Combine strategies for different needs:
```
URL: /api/v2/users  # Major version in URL
Header: X-API-Minor-Version: 3  # Minor version in header
Result: Using v2.3
```

This provides:
- Visibility of major version (in URL)
- Flexibility of minor version (in header)
- Clean migration path for major versions
- Backward compatibility for minor versions
