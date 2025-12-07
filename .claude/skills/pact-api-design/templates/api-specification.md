# API Specification Template

## API: [API Name]

### Overview
- **Version**: v1
- **Base URL**: `/api/v1/[resource]`
- **Authentication**: [Bearer Token | API Key | OAuth2]
- **Rate Limit**: [requests/minute]

---

## Endpoints

### [Resource] Endpoints

#### List [Resources]
```
GET /api/v1/[resources]
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 20, max: 100) |
| sort | string | No | Sort field (default: created_at) |
| order | string | No | Sort order: asc, desc (default: desc) |
| [filter] | string | No | Filter by [field] |

**Response**: `200 OK`
```json
{
  "data": [
    {
      "id": "string",
      "type": "[resource]",
      "attributes": {
        // Resource attributes
      }
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  },
  "links": {
    "self": "/api/v1/[resources]?page=1",
    "next": "/api/v1/[resources]?page=2",
    "prev": null
  }
}
```

---

#### Get [Resource]
```
GET /api/v1/[resources]/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Resource identifier |

**Response**: `200 OK`
```json
{
  "data": {
    "id": "string",
    "type": "[resource]",
    "attributes": {
      // Resource attributes
    },
    "relationships": {
      // Related resources
    }
  }
}
```

**Errors**:
- `404 Not Found`: Resource not found

---

#### Create [Resource]
```
POST /api/v1/[resources]
```

**Request Body**:
```json
{
  "data": {
    "type": "[resource]",
    "attributes": {
      // Required and optional attributes
    }
  }
}
```

**Response**: `201 Created`
```json
{
  "data": {
    "id": "string",
    "type": "[resource]",
    "attributes": {
      // Created resource
    }
  }
}
```

**Errors**:
- `400 Bad Request`: Validation error
- `409 Conflict`: Resource already exists

---

#### Update [Resource]
```
PATCH /api/v1/[resources]/{id}
```

**Request Body**:
```json
{
  "data": {
    "type": "[resource]",
    "attributes": {
      // Fields to update (partial update)
    }
  }
}
```

**Response**: `200 OK`

**Errors**:
- `400 Bad Request`: Validation error
- `404 Not Found`: Resource not found

---

#### Delete [Resource]
```
DELETE /api/v1/[resources]/{id}
```

**Response**: `204 No Content`

**Errors**:
- `404 Not Found`: Resource not found
- `409 Conflict`: Cannot delete (has dependencies)

---

## Error Format

All errors follow this structure:
```json
{
  "errors": [
    {
      "status": "400",
      "code": "VALIDATION_ERROR",
      "title": "Validation Failed",
      "detail": "The 'email' field must be a valid email address",
      "source": {
        "pointer": "/data/attributes/email"
      }
    }
  ]
}
```

## Common Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | VALIDATION_ERROR | Request validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict |
| 422 | UNPROCESSABLE | Business rule violation |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---
*Generated from pact-api-design skill template*
