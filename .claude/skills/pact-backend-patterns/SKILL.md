---
name: pact-backend-patterns
description: |
  CODE PHASE (Backend): Server-side implementation patterns and best practices.

  Provides service layer patterns, API implementation guidance, error handling strategies,
  data validation approaches, middleware patterns, and backend security practices.

  Use when: implementing APIs, creating services, handling errors, validating data,
  building middleware, implementing authentication/authorization.
allowed-tools:
  - Read
  - Bash
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Code"
  version: "1.0.0"
  primary-agent: "pact-backend-coder"
---

# PACT Backend Patterns Skill

## Overview

This skill provides backend implementation patterns and best practices for the CODE phase of the PACT framework. It focuses on server-side development including service layers, API design, error handling, data validation, middleware, and security.

## When to Use This Skill

Use this skill when:
- Implementing RESTful or GraphQL APIs
- Creating service layers and business logic
- Designing error handling strategies
- Implementing data validation and sanitization
- Building middleware and interceptors
- Implementing authentication and authorization
- Optimizing database queries and data access
- Creating background jobs and async processing

## Quick Reference: Service Layer Patterns

### Available MCP Tools

- **sequential-thinking**: Complex backend logic design and error handling strategies

See "MCP Tools for Backend Implementation" section below for detailed usage guidance.

---

### Repository Pattern
```
Repository: Data access abstraction layer
├── Interface defines contract (findById, findAll, create, update, delete)
├── Implementation handles DB-specific logic
└── Service layer depends on repository interface, not implementation

Benefits: Testability, swappable data sources, separation of concerns
```

### Service Pattern
```
Service: Business logic layer
├── Orchestrates repositories and other services
├── Implements business rules and validation
├── Handles transactions and error recovery
└── Returns domain models or DTOs

Benefits: Reusable business logic, testable without DB, clear boundaries
```

### Controller Pattern
```
Controller: HTTP request/response layer
├── Validates request format (using middleware)
├── Calls service layer with extracted data
├── Maps service responses to HTTP responses
└── Handles HTTP-specific concerns (status codes, headers)

Benefits: Thin controllers, framework-agnostic services, clear responsibilities
```

## Quick Reference: Error Handling

### Error Categories

**Validation Errors** (400)
- Invalid input format
- Missing required fields
- Business rule violations
- Use: Immediate client feedback

**Authorization Errors** (401/403)
- Invalid credentials (401)
- Insufficient permissions (403)
- Use: Security enforcement

**Not Found Errors** (404)
- Resource doesn't exist
- Use: Clear user feedback

**Conflict Errors** (409)
- Duplicate resources
- Concurrent modification
- Use: Business constraint enforcement

**Server Errors** (500)
- Unhandled exceptions
- Infrastructure failures
- Use: Graceful degradation, logging

### Error Handling Strategy

```
1. Define custom error classes (ValidationError, AuthError, etc.)
2. Throw semantic errors in services
3. Catch and transform in middleware/controllers
4. Log with context (request ID, user ID, timestamp)
5. Return consistent error format to client
```

## Quick Reference: Data Validation

### Input Validation Layers

**Schema Validation** (First line of defense)
- Validate request structure
- Check data types
- Enforce required fields
- Use: JSON Schema, Joi, Zod, class-validator

**Business Validation** (Second line of defense)
- Check business rules
- Verify relationships
- Validate state transitions
- Use: Service layer logic

**Database Constraints** (Last line of defense)
- Unique constraints
- Foreign key constraints
- Check constraints
- Use: Database schema definitions

## API Implementation Checklist

### Before Writing Code
- [ ] Review architectural specification in `docs/architecture/`
- [ ] Understand domain models and relationships
- [ ] Identify integration points with other services
- [ ] Review authentication/authorization requirements
- [ ] Check performance and scalability requirements

### During Implementation
- [ ] Use dependency injection for testability
- [ ] Implement comprehensive error handling
- [ ] Add structured logging with correlation IDs
- [ ] Validate all inputs at API boundary
- [ ] Use transactions for multi-step operations
- [ ] Implement rate limiting for public endpoints
- [ ] Add request/response logging for debugging
- [ ] Use DTOs to decouple API from domain models

### After Implementation
- [ ] Add inline documentation for complex logic
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Write unit tests for service layer
- [ ] Write integration tests for API endpoints
- [ ] Test error scenarios and edge cases
- [ ] Verify security controls (authentication, authorization, input validation)
- [ ] Test performance under load
- [ ] Document assumptions and trade-offs

## When to Use Sequential Thinking

Use the `mcp__sequential-thinking__sequentialthinking` tool when:

1. **Complex Business Logic Design**
   - Multiple interacting business rules
   - State machine implementations
   - Transaction boundary decisions
   - Example: "Design order fulfillment workflow with inventory, payment, shipping"

2. **Error Handling Strategy**
   - Cascade error handling across layers
   - Error recovery mechanisms
   - Partial failure scenarios
   - Example: "Handle payment failure during checkout with rollback strategy"

3. **Security Implementation**
   - Authentication/authorization flow
   - Permission checking logic
   - Data access control
   - Example: "Design multi-tenant data isolation strategy"

4. **Performance Optimization**
   - Query optimization decisions
   - Caching strategy design
   - Async processing patterns
   - Example: "Optimize user feed generation with 10k+ items"

5. **Integration Design**
   - External API integration patterns
   - Retry and circuit breaker logic
   - Data synchronization strategies
   - Example: "Integrate payment gateway with retry and idempotency"

## Decision Tree: Which Reference to Use

```
START: What are you implementing?

├─ API Endpoints / Controllers?
│  └─> service-patterns.md (Controller Pattern section)
│
├─ Business Logic / Services?
│  └─> service-patterns.md (Service Pattern section)
│
├─ Database Access?
│  └─> service-patterns.md (Repository Pattern section)
│
├─ Error Handling?
│  ├─ Defining error types? → error-handling.md (Error Types section)
│  ├─ Logging strategy? → error-handling.md (Logging section)
│  └─ Recovery patterns? → error-handling.md (Recovery Strategies section)
│
├─ Input Validation?
│  ├─ Request validation? → data-validation.md (Schema Validation section)
│  ├─ Business rules? → data-validation.md (Business Validation section)
│  └─ Sanitization? → data-validation.md (Sanitization section)
│
├─ Authentication / Authorization?
│  ├─ Service patterns → service-patterns.md (Middleware section)
│  └─ Error handling → error-handling.md (Authorization Errors section)
│
└─ Performance / Scalability?
   ├─ Caching → service-patterns.md (Caching Patterns section)
   └─ Async processing → service-patterns.md (Async Patterns section)
```

## Common Backend Patterns

### Middleware Pattern

**Purpose**: Cross-cutting concerns applied to requests/responses

**Use cases**:
- Authentication verification
- Request logging
- Rate limiting
- Request validation
- Error transformation

**Example structure**:
```
Middleware chain: Request → Auth → Logging → Validation → Controller → Response
```

### DTO Pattern

**Purpose**: Decouple API contracts from domain models

**Benefits**:
- API versioning flexibility
- Hide internal structure
- Controlled data exposure
- Input validation boundary

**When to use**:
- Public APIs
- Service boundaries
- Complex domain models
- Version management

### Transaction Pattern

**Purpose**: Ensure data consistency across multiple operations

**Key principles**:
- Start transaction at service layer
- Commit on success
- Rollback on error
- Keep transactions short
- Avoid nested transactions

**When to use**:
- Multiple database operations
- Data consistency requirements
- Financial operations
- Inventory management

## Security Best Practices

### Input Security
- Validate all inputs against schemas
- Sanitize user-provided data
- Use parameterized queries (prevent SQL injection)
- Validate file uploads (type, size, content)
- Implement rate limiting

### Authentication & Authorization
- Use established libraries (Passport, JWT, OAuth)
- Store passwords with strong hashing (bcrypt, argon2)
- Implement token expiration and refresh
- Use HTTPS for all authentication endpoints
- Check permissions at service layer, not just controller

### Data Protection
- Encrypt sensitive data at rest
- Use TLS for data in transit
- Implement proper CORS policies
- Avoid logging sensitive information
- Implement data retention policies

### API Security
- Rate limiting per endpoint/user
- Request size limits
- Timeout configurations
- CSRF protection for state-changing operations
- Input validation at API boundary

## Performance Patterns

### Caching Strategy

**Levels of caching**:
1. Application cache (in-memory)
2. Distributed cache (Redis, Memcached)
3. Database query cache
4. HTTP cache (CDN, reverse proxy)

**Cache invalidation patterns**:
- Time-based expiration (TTL)
- Event-based invalidation
- Cache-aside pattern
- Write-through cache

### Database Optimization

**Query optimization**:
- Use indexes for frequent queries
- Avoid N+1 query problems
- Use connection pooling
- Implement query result pagination
- Use database-specific optimizations

**Data access patterns**:
- Lazy loading for optional data
- Eager loading for required relationships
- Batch operations for bulk updates
- Read replicas for read-heavy workloads

### Async Processing

**When to use**:
- Long-running operations
- Email/notification sending
- Report generation
- Data imports/exports
- Third-party API calls

**Patterns**:
- Job queues (Bull, BullMQ, Sidekiq)
- Pub/sub messaging
- Event-driven architecture
- Background workers

## Testing Strategy

### Unit Tests
- Test service layer in isolation
- Mock repository dependencies
- Test business logic edge cases
- Test error conditions
- Aim for 80%+ coverage of critical paths

### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Test authentication/authorization
- Test error responses
- Test data validation

### Performance Tests
- Load testing for expected traffic
- Stress testing for peak loads
- Endurance testing for memory leaks
- Spike testing for traffic bursts

## File Organization

### Recommended Structure
```
src/
├── controllers/       # HTTP request/response handlers
├── services/         # Business logic layer
├── repositories/     # Data access layer
├── models/           # Domain models
├── dto/              # Data transfer objects
├── middleware/       # Cross-cutting concerns
├── validators/       # Input validation schemas
├── errors/           # Custom error classes
├── config/           # Configuration management
└── utils/            # Shared utilities
```

### File Size Guidelines
- Controllers: < 200 lines (thin controllers)
- Services: < 400 lines (split complex services)
- Repositories: < 300 lines (one per domain model)
- Keep related functionality together
- Extract reusable logic to utilities

## Documentation Standards

### Code Comments
- Add file header with location, purpose, and usage
- Document complex business logic
- Explain non-obvious decisions
- Document security considerations
- Avoid obvious comments

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Document request/response schemas
- Include example requests/responses
- Document error responses
- Note authentication requirements

### Service Documentation
- Document public methods with JSDoc/docstrings
- Include parameter descriptions
- Document return values
- Note exceptions thrown
- Provide usage examples

## Common Pitfalls to Avoid

### Architecture
- ❌ Business logic in controllers
- ❌ Direct database access from controllers
- ❌ Tight coupling between layers
- ❌ Missing abstraction layers

### Error Handling
- ❌ Swallowing exceptions
- ❌ Generic error messages
- ❌ Missing error logging
- ❌ Exposing internal errors to clients

### Security
- ❌ Trusting client input
- ❌ Missing authentication checks
- ❌ SQL injection vulnerabilities
- ❌ Logging sensitive data

### Performance
- ❌ N+1 query problems
- ❌ Missing database indexes
- ❌ Synchronous long-running operations
- ❌ No rate limiting

## MCP Tools for Backend Implementation

This section provides guidance on WHEN and WHY to use MCP tools during backend coding. See agent documentation for invocation syntax.

### Available MCP Tools

The following MCP tool enhances backend implementation decisions:
- **sequential-thinking**: Complex backend logic design and error handling strategies

---

### sequential-thinking

**Purpose**: Extended reasoning capability for complex backend implementation decisions

**When to use**:
- Designing complex business logic with multiple interacting rules (e.g., order fulfillment workflow coordinating inventory, payment, shipping with various failure modes)
- Planning error handling strategies across service layers with cascading failures (e.g., payment failure during checkout requiring rollback coordination)
- Designing multi-step transaction boundaries with competing consistency and performance requirements
- Planning security implementations for multi-tenant systems (e.g., data isolation strategies with shared vs separate schemas)
- Optimizing performance bottlenecks with multiple competing approaches (e.g., query optimization vs caching vs async processing trade-offs)
- Designing integration patterns for unreliable external services (e.g., retry strategies, circuit breakers, idempotency considerations)

**When NOT to use**:
- Straightforward CRUD operations following established service patterns
- Simple input validation with clear schema requirements
- Standard authentication flows using well-documented libraries
- Performance optimization with obvious solutions (e.g., adding missing database index)
- Refactoring existing code without changing business logic

**Value for backend coding**: Systematic reasoning prevents overlooking edge cases in complex business logic. Creates clear documentation of error handling rationale for future maintenance. Reduces bugs in critical transaction paths.

**Integration approach**: Review architectural specification → Identify complex implementation decision → Use sequential-thinking to reason through edge cases and failure modes → Implement solution with documented rationale → Create tests covering reasoned scenarios.

**See pact-backend-coder agent for invocation syntax and workflow integration.**

---

## Reference Files

This skill includes detailed reference documentation:

1. **service-patterns.md**: Repository, service, controller patterns with implementation examples
2. **error-handling.md**: Error types, logging strategies, recovery patterns
3. **data-validation.md**: Input validation, sanitization, schema design

Use the decision tree above to determine which reference to consult for your specific implementation needs.

## Integration with PACT Framework

### Inputs from Previous Phases

**From PREPARE phase** (`docs/preparation/`):
- API documentation and requirements
- External service integration specs
- Performance requirements
- Security requirements

**From ARCHITECT phase** (`docs/architecture/`):
- System architecture diagrams
- Component specifications
- API contracts and interfaces
- Data models and schemas
- Technology stack decisions

### Outputs to TEST Phase

After completing backend implementation:
- Create summary in `docs/implementation/backend-summary.md`
- Document APIs implemented
- Note security measures taken
- List integration points
- Specify test scenarios to verify
- Hand off to `pact-test-engineer` for validation

## Success Criteria

Your backend implementation is complete when:
- ✅ All architectural specifications implemented
- ✅ Comprehensive error handling in place
- ✅ All inputs validated and sanitized
- ✅ Security controls implemented
- ✅ Code follows established patterns
- ✅ Documentation complete
- ✅ Unit tests written
- ✅ Ready for integration testing

## Additional Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- REST API Best Practices: https://restfulapi.net/
- Node.js Best Practices: https://github.com/goldbergyoni/nodebestpractices
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
