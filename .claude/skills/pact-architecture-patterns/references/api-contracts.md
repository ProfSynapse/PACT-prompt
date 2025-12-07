# API Contract Patterns

> **When to use**: Designing APIs, defining service interfaces
> **Phase**: PACT Architect phase - API design specifications

## Table of Contents

1. REST API Design Patterns
2. API Contract Template (OpenAPI)
3. Error Response Standards
4. Versioning Strategies
5. Authentication Patterns
6. Pagination and Filtering
7. Rate Limiting
8. Complete Example: User API

---

## REST API Design Patterns

### Resource-Oriented Design

**Core Principles**:
1. Resources are nouns, not verbs
2. Use HTTP methods for operations (GET, POST, PUT, DELETE, PATCH)
3. Hierarchical URL structure reflects relationships
4. Consistent naming conventions
5. Plural nouns for collections

**Good Examples**:
```
GET    /users              # List all users
POST   /users              # Create a new user
GET    /users/{id}         # Get specific user
PUT    /users/{id}         # Update entire user
PATCH  /users/{id}         # Partial user update
DELETE /users/{id}         # Delete user
GET    /users/{id}/orders  # Get user's orders
POST   /users/{id}/orders  # Create order for user
```

**Bad Examples** (avoid):
```
GET    /getUsers           # Don't use verbs in URLs
POST   /user/create        # HTTP method already says "create"
GET    /users/delete/123   # DELETE should be used, not GET
POST   /user-search        # Should be GET with query params
```

### URL Naming Conventions

- **Lowercase**: Use lowercase letters
- **Hyphens**: Use hyphens for multi-word resources (`/user-profiles`, not `/user_profiles`)
- **No trailing slashes**: `/users`, not `/users/`
- **Plural for collections**: `/users`, not `/user`
- **Singular for single actions**: `/login`, `/logout`

### HTTP Methods and Their Meanings

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|-----------|------|--------------|---------------|
| GET    | Read resource | Yes | Yes | No | Yes |
| POST   | Create resource | No | No | Yes | Yes |
| PUT    | Replace resource | Yes | No | Yes | Yes |
| PATCH  | Update resource | No | No | Yes | Yes |
| DELETE | Remove resource | Yes | No | No | Optional |

**Idempotent**: Multiple identical requests have same effect as single request
**Safe**: Does not modify resources

---

## API Contract Template (OpenAPI)

### Complete OpenAPI 3.0 Specification

```yaml
openapi: 3.0.0
info:
  title: E-Commerce API
  version: 1.0.0
  description: |
    RESTful API for e-commerce platform providing user management,
    product catalog, and order processing.
  contact:
    name: API Support
    email: api@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List all users
      description: Returns a paginated list of users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: sort
          in: query
          description: Sort field and direction
          required: false
          schema:
            type: string
            enum: [created_at:asc, created_at:desc, name:asc, name:desc]
            default: created_at:desc
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/InternalError'

    post:
      summary: Create a new user
      description: Creates a new user account
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'
        '500':
          $ref: '#/components/responses/InternalError'

  /users/{userId}:
    parameters:
      - name: userId
        in: path
        required: true
        description: Unique user identifier
        schema:
          type: string
          format: uuid

    get:
      summary: Get user by ID
      description: Returns detailed information about a specific user
      operationId: getUser
      tags:
        - Users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'

    put:
      summary: Update user
      description: Updates all fields of a user
      operationId: updateUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'
      responses:
        '200':
          description: User updated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'

    delete:
      summary: Delete user
      description: Permanently deletes a user account
      operationId: deleteUser
      tags:
        - Users
      responses:
        '204':
          description: User deleted successfully
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
        - created_at
      properties:
        id:
          type: string
          format: uuid
          description: Unique user identifier
          example: "123e4567-e89b-12d3-a456-426614174000"
        email:
          type: string
          format: email
          description: User's email address
          example: "user@example.com"
        name:
          type: string
          minLength: 1
          maxLength: 100
          description: User's full name
          example: "John Doe"
        avatar_url:
          type: string
          format: uri
          nullable: true
          description: URL to user's avatar image
          example: "https://cdn.example.com/avatars/123.jpg"
        created_at:
          type: string
          format: date-time
          description: Account creation timestamp
          example: "2025-12-04T10:30:00Z"
        updated_at:
          type: string
          format: date-time
          description: Last update timestamp
          example: "2025-12-04T15:45:00Z"

    UserCreate:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
          example: "newuser@example.com"
        name:
          type: string
          minLength: 1
          maxLength: 100
          example: "Jane Smith"
        password:
          type: string
          format: password
          minLength: 8
          example: "SecurePass123!"
        avatar_url:
          type: string
          format: uri
          nullable: true

    UserUpdate:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        avatar_url:
          type: string
          format: uri
          nullable: true

    PaginationMeta:
      type: object
      properties:
        total:
          type: integer
          description: Total number of items
          example: 150
        page:
          type: integer
          description: Current page number
          example: 1
        per_page:
          type: integer
          description: Items per page
          example: 20
        pages:
          type: integer
          description: Total number of pages
          example: 8
        has_more:
          type: boolean
          description: Whether more pages exist
          example: true

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Machine-readable error code
          example: "VALIDATION_ERROR"
        message:
          type: string
          description: Human-readable error message
          example: "Email address is invalid"
        details:
          type: object
          description: Additional error context
          additionalProperties: true
          example:
            field: "email"
            reason: "Invalid format"
        request_id:
          type: string
          description: Unique request identifier for tracking
          example: "req_abc123xyz"
        timestamp:
          type: string
          format: date-time
          description: Error occurrence time
          example: "2025-12-04T10:30:00Z"

  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                $ref: '#/components/schemas/Error'
          example:
            error:
              code: "VALIDATION_ERROR"
              message: "Request validation failed"
              details:
                field: "email"
                reason: "Invalid email format"
              request_id: "req_abc123"
              timestamp: "2025-12-04T10:30:00Z"

    Unauthorized:
      description: Authentication required or failed
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                $ref: '#/components/schemas/Error'
          example:
            error:
              code: "UNAUTHORIZED"
              message: "Invalid or missing authentication token"
              request_id: "req_abc124"
              timestamp: "2025-12-04T10:31:00Z"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                $ref: '#/components/schemas/Error'
          example:
            error:
              code: "NOT_FOUND"
              message: "User not found"
              details:
                resource: "user"
                id: "123e4567-e89b-12d3-a456-426614174000"
              request_id: "req_abc125"
              timestamp: "2025-12-04T10:32:00Z"

    Conflict:
      description: Resource conflict (e.g., duplicate)
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                $ref: '#/components/schemas/Error'
          example:
            error:
              code: "CONFLICT"
              message: "User with this email already exists"
              details:
                field: "email"
                value: "user@example.com"
              request_id: "req_abc126"
              timestamp: "2025-12-04T10:33:00Z"

    InternalError:
      description: Internal server error
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                $ref: '#/components/schemas/Error'
          example:
            error:
              code: "INTERNAL_ERROR"
              message: "An unexpected error occurred"
              request_id: "req_abc127"
              timestamp: "2025-12-04T10:34:00Z"

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token authentication

security:
  - BearerAuth: []
```

---

## Error Response Standards

### Standard Error Format

All error responses should follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "fieldName",
      "reason": "Specific reason for error"
    },
    "request_id": "req_unique_identifier",
    "timestamp": "2025-12-04T10:30:00Z"
  }
}
```

### Common HTTP Status Codes

| Status | Code | Meaning | When to Use |
|--------|------|---------|-------------|
| 200 | OK | Success | Successful GET, PUT, PATCH |
| 201 | Created | Resource created | Successful POST |
| 204 | No Content | Success, no body | Successful DELETE |
| 400 | Bad Request | Invalid input | Validation failures |
| 401 | Unauthorized | Auth required | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions | User lacks access |
| 404 | Not Found | Resource doesn't exist | Invalid ID |
| 409 | Conflict | Resource conflict | Duplicate entry |
| 422 | Unprocessable Entity | Valid format, invalid semantics | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded | Too many requests |
| 500 | Internal Error | Server failure | Unexpected errors |
| 503 | Service Unavailable | Temporary unavailable | Maintenance mode |

### Error Code Naming Convention

Use UPPER_SNAKE_CASE for error codes:

```
VALIDATION_ERROR
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
CONFLICT
RATE_LIMITED
INTERNAL_ERROR
SERVICE_UNAVAILABLE
```

---

## Versioning Strategies

### URL Versioning (Recommended)

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Benefits**:
- Clear and explicit
- Easy to understand and test
- Cache-friendly
- Works with all HTTP clients

**Trade-offs**:
- URL changes between versions
- Can lead to version proliferation

**Implementation**:
```
/v1/users - Current stable version
/v2/users - New version with breaking changes
/v1/... - Maintain for 6-12 months after v2 release
```

### Header Versioning

```
GET /users HTTP/1.1
Accept: application/vnd.myapi.v1+json
```

**Benefits**:
- Clean URLs
- Content negotiation
- RESTful purist approach

**Trade-offs**:
- Less visible
- Harder to test in browser
- Requires custom headers

### Version Management Guidelines

1. **Semantic Versioning**: Use Major.Minor.Patch
   - Major: Breaking changes
   - Minor: New features, backward compatible
   - Patch: Bug fixes

2. **Deprecation Policy**:
   - Announce deprecation 6 months in advance
   - Provide migration guide
   - Support old version for 12 months minimum

3. **Backward Compatibility**:
   - Add fields, don't remove them
   - Make new fields optional
   - Keep old endpoints working
   - Document all changes

4. **Breaking Changes**:
   - Required → Optional: OK
   - Optional → Required: BREAKING
   - Rename field: BREAKING
   - Change data type: BREAKING
   - Remove endpoint: BREAKING

---

## Authentication Patterns

### JWT Bearer Token

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Payload**:
```json
{
  "sub": "user_id",
  "iat": 1638360000,
  "exp": 1638363600,
  "scope": ["read:users", "write:users"]
}
```

**Best Practices**:
- Short expiration (15-30 minutes for access tokens)
- Refresh tokens for long-lived sessions
- Include only necessary claims
- Sign with strong algorithm (RS256 recommended)

### API Key Authentication

```
X-API-Key: your_api_key_here
```

**Best Practices**:
- Use for server-to-server communication
- Not suitable for client-side applications
- Rotate keys regularly
- Support multiple keys per account
- Rate limit per API key

### OAuth 2.0 Flow

**Authorization Code Flow** (for web apps):
```
1. User → Authorization Server: Request authorization
2. Authorization Server → User: Redirect with auth code
3. Client → Authorization Server: Exchange code for token
4. Client → Resource Server: Use access token
```

---

## Pagination and Filtering

### Offset-Based Pagination

**Request**:
```
GET /users?page=2&limit=20
```

**Response**:
```json
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 2,
    "per_page": 20,
    "pages": 8,
    "has_more": true
  }
}
```

### Cursor-Based Pagination

**Request**:
```
GET /users?cursor=eyJpZCI6MTAwfQ==&limit=20
```

**Response**:
```json
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJpZCI6MTIwfQ==",
    "has_more": true
  }
}
```

**Use cursor-based for**:
- Large datasets
- Real-time data
- Consistent results even with inserts/deletes

### Filtering

```
GET /users?status=active&role=admin&created_after=2025-01-01
```

**Best Practices**:
- Support common filters
- Document all filter options
- Validate filter values
- Consider performance implications

### Sorting

```
GET /users?sort=created_at:desc,name:asc
```

---

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
```

### 429 Response

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_at": "2025-12-04T11:00:00Z"
    }
  }
}
```

### Rate Limiting Strategies

- **Per user**: Track by user ID or email
- **Per API key**: Track by API key
- **Per IP**: Track by IP address (less reliable)
- **Per endpoint**: Different limits for different endpoints

---

## Additional Resources

For complementary architectural patterns and guidance:
- Refer back to SKILL.md for other architecture references
- Use C4 diagrams to visualize API relationships and system context
- Review anti-patterns to avoid common API design mistakes
