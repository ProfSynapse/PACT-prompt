# REST API Design Example

## Scenario: Task Management API

This example demonstrates REST API best practices for a task management system.

---

## Resource Design

### Resources Identified
- **Tasks** (`/tasks`) - Core resource
- **Projects** (`/projects`) - Parent resource
- **Users** (`/users`) - Related resource
- **Comments** (`/tasks/{id}/comments`) - Nested resource

### Relationships
```
Project (1) ─────── (*) Task
Task    (1) ─────── (*) Comment
User    (1) ─────── (*) Task (assignee)
```

---

## Endpoint Design

### Tasks Resource

```yaml
# List tasks with filtering and pagination
GET /api/v1/tasks
  Query Parameters:
    - status: enum[open, in_progress, completed]
    - assignee_id: uuid
    - project_id: uuid
    - due_before: date (ISO 8601)
    - due_after: date (ISO 8601)
    - page: integer (default: 1)
    - limit: integer (default: 20, max: 100)
    - sort: enum[created_at, due_date, priority]
    - order: enum[asc, desc]

  Response: 200 OK
    {
      "data": [Task],
      "meta": { "page": 1, "limit": 20, "total": 150 },
      "links": { "self": "...", "next": "...", "prev": null }
    }

# Get single task
GET /api/v1/tasks/{id}
  Response: 200 OK
    {
      "data": Task,
      "included": [User, Project]  // Sparse fieldsets
    }

# Create task
POST /api/v1/tasks
  Request Body:
    {
      "data": {
        "type": "task",
        "attributes": {
          "title": "string (required)",
          "description": "string",
          "due_date": "date",
          "priority": "enum[low, medium, high]"
        },
        "relationships": {
          "project": { "data": { "type": "project", "id": "uuid" } },
          "assignee": { "data": { "type": "user", "id": "uuid" } }
        }
      }
    }
  Response: 201 Created
    Location: /api/v1/tasks/{new_id}
    {
      "data": Task
    }

# Update task (partial)
PATCH /api/v1/tasks/{id}
  Request Body:
    {
      "data": {
        "type": "task",
        "attributes": {
          "status": "in_progress"
        }
      }
    }
  Response: 200 OK

# Delete task
DELETE /api/v1/tasks/{id}
  Response: 204 No Content

# Bulk operations (custom action)
POST /api/v1/tasks/bulk-update
  Request Body:
    {
      "task_ids": ["uuid1", "uuid2"],
      "updates": {
        "status": "completed"
      }
    }
  Response: 200 OK
    {
      "updated": 2,
      "failed": []
    }
```

---

## Request/Response Examples

### Create Task - Success

**Request:**
```http
POST /api/v1/tasks HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbG...
Content-Type: application/json

{
  "data": {
    "type": "task",
    "attributes": {
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication to the API",
      "due_date": "2024-02-15",
      "priority": "high"
    },
    "relationships": {
      "project": {
        "data": { "type": "project", "id": "550e8400-e29b-41d4-a716-446655440000" }
      }
    }
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Location: /api/v1/tasks/7c9e6679-7425-40de-944b-e07fc1f90ae7
Content-Type: application/json

{
  "data": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "type": "task",
    "attributes": {
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication to the API",
      "status": "open",
      "due_date": "2024-02-15",
      "priority": "high",
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    },
    "relationships": {
      "project": {
        "data": { "type": "project", "id": "550e8400-e29b-41d4-a716-446655440000" }
      },
      "assignee": {
        "data": null
      }
    },
    "links": {
      "self": "/api/v1/tasks/7c9e6679-7425-40de-944b-e07fc1f90ae7"
    }
  }
}
```

### Create Task - Validation Error

**Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "errors": [
    {
      "status": "400",
      "code": "VALIDATION_ERROR",
      "title": "Invalid Attribute",
      "detail": "Title is required and must be between 1 and 255 characters",
      "source": {
        "pointer": "/data/attributes/title"
      }
    },
    {
      "status": "400",
      "code": "VALIDATION_ERROR",
      "title": "Invalid Attribute",
      "detail": "Priority must be one of: low, medium, high",
      "source": {
        "pointer": "/data/attributes/priority"
      }
    }
  ]
}
```

---

## Pagination Pattern

```json
{
  "data": [...],
  "meta": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/tasks?page=2&limit=20",
    "first": "/api/v1/tasks?page=1&limit=20",
    "prev": "/api/v1/tasks?page=1&limit=20",
    "next": "/api/v1/tasks?page=3&limit=20",
    "last": "/api/v1/tasks?page=8&limit=20"
  }
}
```

---

## HTTP Status Codes Used

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |

---
*Generated from pact-api-design skill example*
