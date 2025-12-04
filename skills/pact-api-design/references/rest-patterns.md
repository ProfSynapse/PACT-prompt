# REST API Design Patterns

Comprehensive guide to RESTful API design patterns, best practices, and common pitfalls.

## Table of Contents

1. [Resource Naming Conventions](#resource-naming-conventions)
2. [HTTP Method Usage](#http-method-usage)
3. [URL Structure](#url-structure)
4. [HATEOAS](#hateoas)
5. [Content Negotiation](#content-negotiation)
6. [Common Patterns](#common-patterns)
7. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Resource Naming Conventions

### General Principles

1. **Use Plural Nouns**: Resources should be plural nouns representing collections
   - Good: `/users`, `/orders`, `/products`
   - Bad: `/user`, `/getUser`, `/createOrder`

2. **Lowercase with Hyphens**: Use lowercase letters with hyphens for multi-word resources
   - Good: `/order-items`, `/shipping-addresses`
   - Bad: `/OrderItems`, `/shipping_addresses`, `/shippingAddresses`

3. **Resource Hierarchy**: Nest resources to show relationships, but limit depth
   - Good: `/users/123/orders`
   - Acceptable: `/users/123/orders/456/items`
   - Bad: `/companies/1/departments/2/teams/3/members/4/tasks/5` (too deep)

4. **Avoid Verbs**: Resources are nouns; actions are expressed through HTTP methods
   - Good: `POST /users`, `DELETE /users/123`
   - Bad: `/createUser`, `/deleteUser`, `/getUser`

### Special Cases

**Actions/Operations**: When an action doesn't fit CRUD, use a noun representing the operation:
- `POST /users/123/password-reset` (request password reset)
- `POST /orders/456/cancellation` (cancel order)
- `POST /documents/789/publication` (publish document)

**Searches**: Treat search as a resource or use query parameters:
- `GET /search?q=query&type=users` (search as resource)
- `GET /users?search=john&status=active` (filtered collection)

**Batch Operations**: Use plural forms or batch endpoints:
- `POST /users/batch` with array of user objects
- `DELETE /users?ids=1,2,3` (bulk delete)

## HTTP Method Usage

### GET - Retrieve Resources

**Purpose**: Retrieve representation of a resource or collection
**Idempotent**: Yes (multiple identical requests have same effect as single request)
**Safe**: Yes (doesn't modify server state)
**Cacheable**: Yes

```
# Retrieve collection
GET /api/v1/users
Response: 200 OK

# Retrieve specific resource
GET /api/v1/users/123
Response: 200 OK

# Resource not found
GET /api/v1/users/999
Response: 404 Not Found
```

**Best Practices**:
- Use query parameters for filtering, sorting, pagination
- Return 404 for missing resources, not empty 200
- Support conditional requests (If-None-Match, If-Modified-Since)
- Include ETag headers for caching

### POST - Create Resources or Operations

**Purpose**: Create new resource or execute non-idempotent operation
**Idempotent**: No (repeated requests may create duplicates)
**Safe**: No
**Cacheable**: Only if Cache-Control or Expires headers set

```
# Create resource
POST /api/v1/users
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe"
}

Response: 201 Created
Location: /api/v1/users/124
{
  "id": 124,
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2025-12-04T10:30:00Z"
}

# Non-idempotent operation
POST /api/v1/orders/456/payment
Response: 202 Accepted
```

**Best Practices**:
- Return 201 Created with Location header for new resources
- Return created resource in response body
- Use 202 Accepted for async operations
- Return 409 Conflict for duplicate resources
- Validate all input and return 422 for validation errors

### PUT - Replace Entire Resource

**Purpose**: Replace entire resource with new representation
**Idempotent**: Yes (multiple identical requests produce same result)
**Safe**: No
**Cacheable**: No

```
# Replace entire user resource
PUT /api/v1/users/123
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "name": "John Doe",
  "bio": "Software Engineer",
  "location": "San Francisco"
}

Response: 200 OK
{
  "id": 123,
  "email": "john.doe@example.com",
  "name": "John Doe",
  "bio": "Software Engineer",
  "location": "San Francisco",
  "updated_at": "2025-12-04T10:35:00Z"
}
```

**Best Practices**:
- Require all fields in request (omitted fields are removed)
- Use PATCH for partial updates instead
- Return 404 if resource doesn't exist
- Consider supporting "upsert" behavior (create if not exists)
- Return updated resource in response

### PATCH - Partial Update

**Purpose**: Apply partial modifications to resource
**Idempotent**: No (depends on implementation)
**Safe**: No
**Cacheable**: No

```
# Update only email field
PATCH /api/v1/users/123
Content-Type: application/json

{
  "email": "newemail@example.com"
}

Response: 200 OK
{
  "id": 123,
  "email": "newemail@example.com",
  "name": "John Doe",
  "bio": "Software Engineer",
  "location": "San Francisco",
  "updated_at": "2025-12-04T10:40:00Z"
}

# JSON Patch format (RFC 6902)
PATCH /api/v1/users/123
Content-Type: application/json-patch+json

[
  { "op": "replace", "path": "/email", "value": "newemail@example.com" },
  { "op": "add", "path": "/phone", "value": "+1-555-0100" }
]
```

**Best Practices**:
- Accept partial representation (only changed fields)
- Support JSON Merge Patch (RFC 7396) or JSON Patch (RFC 6902)
- Return 404 if resource doesn't exist
- Return 422 for validation errors
- Return updated resource in response

### DELETE - Remove Resource

**Purpose**: Delete specified resource
**Idempotent**: Yes (deleting multiple times has same effect)
**Safe**: No
**Cacheable**: No

```
# Delete resource
DELETE /api/v1/users/123
Response: 204 No Content

# Delete already deleted resource
DELETE /api/v1/users/123
Response: 404 Not Found (or 204 if treating as idempotent)

# Soft delete
DELETE /api/v1/users/123
Response: 200 OK
{
  "id": 123,
  "status": "deleted",
  "deleted_at": "2025-12-04T10:45:00Z"
}
```

**Best Practices**:
- Return 204 No Content on successful deletion
- Return 404 if resource doesn't exist
- Consider soft deletes for auditing
- Support permanent delete separately if using soft deletes
- Return resource representation if providing status info

## URL Structure

### Path vs Query Parameters

**Path Parameters**: Identify specific resources
```
/users/123           # User ID in path
/orders/456/items/789  # Order ID and item ID in path
```

**Query Parameters**: Filter, sort, paginate, or modify representation
```
/users?status=active&role=admin  # Filter users
/products?sort=price:desc        # Sort products
/orders?page=2&per_page=20       # Paginate orders
/users/123?fields=id,name,email  # Partial response
```

### URL Design Guidelines

1. **Keep URLs Short**: Aim for 2-3 path segments maximum
   ```
   Good: /users/123/orders
   Bad: /api/v1/companies/456/departments/789/teams/012/members/345
   ```

2. **Use Query Parameters for Optional Filters**:
   ```
   /products?category=electronics&price_min=100&price_max=500
   ```

3. **Avoid File Extensions**:
   ```
   Good: /users/123 with Accept: application/json header
   Bad: /users/123.json
   ```

4. **Version in URL or Header**:
   ```
   URL: /api/v1/users
   Header: Accept: application/vnd.api+json; version=1
   ```

5. **Trailing Slashes**: Be consistent (prefer without)
   ```
   Preferred: /users/123
   Avoid: /users/123/
   ```

## HATEOAS

**Hypermedia As The Engine Of Application State**: Include links to related resources and actions.

### Basic Link Format

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/api/v1/users/123" },
    "orders": { "href": "/api/v1/users/123/orders" },
    "profile": { "href": "/api/v1/users/123/profile" }
  }
}
```

### HAL (Hypertext Application Language)

```json
{
  "id": 123,
  "name": "John Doe",
  "_links": {
    "self": { "href": "/api/v1/users/123" },
    "orders": { "href": "/api/v1/users/123/orders" }
  },
  "_embedded": {
    "orders": [
      {
        "id": 456,
        "total": 99.99,
        "_links": {
          "self": { "href": "/api/v1/orders/456" }
        }
      }
    ]
  }
}
```

### JSON:API Format

```json
{
  "data": {
    "type": "users",
    "id": "123",
    "attributes": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "relationships": {
      "orders": {
        "links": {
          "related": "/api/v1/users/123/orders"
        }
      }
    }
  },
  "links": {
    "self": "/api/v1/users/123"
  }
}
```

### When to Use HATEOAS

**Good Fit**:
- Public APIs with diverse clients
- Long-lived APIs that need flexibility
- Complex workflows with state transitions
- APIs consumed primarily by humans/exploratory tools

**Overkill**:
- Internal microservices (tight coupling is acceptable)
- Simple CRUD APIs with known clients
- Mobile apps with bandwidth constraints
- High-performance requirements (overhead not acceptable)

## Content Negotiation

### Request Content Type

Use `Content-Type` header to specify request body format:
```
POST /api/v1/users
Content-Type: application/json

{"name": "John Doe"}
```

### Response Content Type

Use `Accept` header to request response format:
```
GET /api/v1/users/123
Accept: application/json
```

Server responds with:
```
Content-Type: application/json

{"id": 123, "name": "John Doe"}
```

### Supported Media Types

- `application/json`: Standard JSON
- `application/hal+json`: HAL format
- `application/vnd.api+json`: JSON:API format
- `application/xml`: XML (if supporting legacy clients)
- `application/problem+json`: RFC 7807 problem details

## Common Patterns

### Filtering

```
GET /api/v1/products?category=electronics&price_max=500&in_stock=true
```

**Operators in Query Parameters**:
```
/products?price[gte]=100&price[lte]=500  # Range
/users?created_at[after]=2025-01-01      # Date comparison
/orders?status[in]=pending,processing    # Multiple values
```

### Sorting

```
GET /api/v1/users?sort=created_at        # Ascending
GET /api/v1/users?sort=-created_at       # Descending (minus prefix)
GET /api/v1/users?sort=last_name,first_name  # Multiple fields
```

### Field Selection (Sparse Fieldsets)

```
GET /api/v1/users?fields=id,name,email   # Only return specified fields
GET /api/v1/users/123?exclude=password,ssn  # Exclude sensitive fields
```

### Resource Expansion (Embedding)

```
GET /api/v1/orders/456?expand=customer,items
```

Response includes nested resources:
```json
{
  "id": 456,
  "customer": {
    "id": 123,
    "name": "John Doe"
  },
  "items": [
    {"id": 1, "product": "Widget", "quantity": 2}
  ]
}
```

### Bulk Operations

**Batch Create**:
```
POST /api/v1/users/batch
Content-Type: application/json

[
  {"name": "User 1", "email": "user1@example.com"},
  {"name": "User 2", "email": "user2@example.com"}
]
```

**Bulk Update**:
```
PATCH /api/v1/users
Content-Type: application/json

[
  {"id": 123, "status": "active"},
  {"id": 124, "status": "inactive"}
]
```

**Bulk Delete**:
```
DELETE /api/v1/users?ids=123,124,125
```

## Anti-Patterns to Avoid

### 1. Using GET for Mutations
```
Bad: GET /api/v1/users/123/delete
Good: DELETE /api/v1/users/123
```

### 2. Ignoring HTTP Status Codes
```
Bad: Always return 200, put error in body
Good: Use appropriate status codes (404, 422, 500)
```

### 3. Not Using HTTP Methods Correctly
```
Bad: POST /api/v1/users/123/update
Good: PATCH /api/v1/users/123
```

### 4. Exposing Internal Implementation
```
Bad: /api/v1/database-table-name
Good: /api/v1/user-profiles
```

### 5. Non-Hierarchical Nesting
```
Bad: /users/123/companies/456 (user doesn't own company)
Good: /companies/456 with ?user_id=123 filter
```

### 6. Tunneling Everything Through POST
```
Bad: POST /api with action=getUser, action=deleteUser
Good: Use appropriate HTTP methods
```

### 7. Version Chaos
```
Bad: /api/v1/users, /api/v2.1/users, /api/latest/users
Good: Consistent versioning strategy with clear deprecation
```

### 8. Exposing Database IDs Directly
Consider using UUIDs or opaque identifiers instead of sequential integers for:
- Security (prevent enumeration attacks)
- Scalability (distributed ID generation)
- Privacy (don't expose growth metrics)

### 9. Inconsistent Error Formats
```
Bad:
  /users returns {"error": "Not found"}
  /orders returns {"message": "Not found", "code": 404}

Good: Consistent error structure across all endpoints
```

### 10. Missing Pagination on Large Collections
```
Bad: GET /api/v1/users returns all 1,000,000 users
Good: Always paginate large collections with sensible defaults
```
