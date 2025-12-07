# Architectural Anti-Patterns

> **When to use**: During architecture review, preventing common mistakes
> **Phase**: PACT Architect phase - architecture review and validation

## Table of Contents

1. Structural Anti-Patterns
2. Integration Anti-Patterns
3. Data Management Anti-Patterns
4. Performance Anti-Patterns
5. Development Process Anti-Patterns
6. Review Checklist

---

## Overview

Anti-patterns are commonly-occurring solutions to problems that generate negative consequences. Recognizing these patterns helps architects avoid costly mistakes and design more maintainable systems.

This reference documents the most common architectural anti-patterns, their symptoms, consequences, and how to avoid or refactor them.

---

## Structural Anti-Patterns

### Big Ball of Mud

**Description**: A system with no clear architecture, where everything is tangled together

**Symptoms**:
- No clear component boundaries
- Everything depends on everything else
- Difficult to understand where functionality lives
- Changes have unpredictable ripple effects
- New developers struggle to understand the system
- "Spaghetti code" at the architectural level

**Example**:
```python
# Anti-pattern: God class doing everything
class Application:
    def handle_request(self, request):
        # Parse request
        data = json.loads(request.body)

        # Validate user
        user = self.db.query(f"SELECT * FROM users WHERE id = {data['user_id']}")
        if not user or user['password'] != hash(data['password']):
            return error_response("Invalid credentials")

        # Query database
        products = self.db.query("SELECT * FROM products WHERE available = true")

        # Process business logic
        cart_total = sum(p['price'] for p in products if p['id'] in data['cart'])

        # Format response
        response = format_json(cart_total, products)

        # Log everything
        self.logger.info(f"User {user['id']} processed cart")

        # Send notifications
        self.email.send(user['email'], "Cart processed")

        # Update cache
        self.cache.set(f"cart:{user['id']}", cart_total)

        return response
```

**Consequences**:
- Impossible to test in isolation
- Can't reuse components
- Hard to onboard new developers
- Deployments are high-risk
- Performance optimization is difficult

**Solution**: Apply Single Responsibility Principle

```python
# Better: Separate concerns with clear boundaries
class RequestHandler:
    def __init__(self, auth_service, cart_service, response_formatter):
        self.auth_service = auth_service
        self.cart_service = cart_service
        self.formatter = response_formatter

    def handle(self, request):
        user = self.auth_service.authenticate(request)
        cart = self.cart_service.process_cart(user, request.data)
        return self.formatter.format(cart)

class AuthenticationService:
    def __init__(self, user_repository):
        self.users = user_repository

    def authenticate(self, request):
        # Focused on authentication only
        pass

class CartService:
    def __init__(self, product_repo, notification_service):
        self.products = product_repo
        self.notifications = notification_service

    def process_cart(self, user, cart_data):
        # Focused on cart processing only
        pass
```

**Prevention**:
- Define clear component boundaries from the start
- Regular architecture reviews
- Enforce separation of concerns
- Use dependency injection
- Write architectural decision records (ADRs)

---

### God Object

**Description**: One class or module that knows or does too much

**Symptoms**:
- Single file with thousands of lines
- One class with 50+ methods
- Multiple unrelated responsibilities
- Hard to test without complex setup
- High coupling with many other components
- Frequent merge conflicts on this file

**Example**:
```python
# Anti-pattern: God object
class UserManager:
    def create_user(self): pass
    def delete_user(self): pass
    def authenticate_user(self): pass
    def send_email(self): pass
    def validate_password(self): pass
    def log_activity(self): pass
    def calculate_statistics(self): pass
    def generate_report(self): pass
    def export_to_csv(self): pass
    def import_from_api(self): pass
    # ... 40 more methods ...
```

**Consequences**:
- Changes affect many parts of the system
- Difficult to understand and maintain
- Testing requires complex mocks
- Multiple developers blocking each other
- High risk of regression bugs

**Solution**: Extract cohesive subsystems

```python
# Better: Single Responsibility classes
class UserRepository:
    def create(self, user): pass
    def delete(self, user_id): pass
    def find(self, user_id): pass

class AuthenticationService:
    def authenticate(self, credentials): pass
    def validate_password(self, password): pass

class UserNotificationService:
    def send_welcome_email(self, user): pass
    def send_password_reset(self, user): pass

class UserAnalytics:
    def calculate_statistics(self): pass
    def generate_report(self): pass

class UserDataExporter:
    def export_to_csv(self, users): pass
    def import_from_api(self, api_url): pass
```

**Prevention**:
- Limit class size to <500 lines
- Limit methods per class to <20
- Apply Single Responsibility Principle
- Regular refactoring
- Code review with size gates

---

### Tight Coupling

**Description**: Components directly depend on concrete implementations rather than abstractions

**Symptoms**:
- Components directly instantiate their dependencies
- Changes in one component require changes in many others
- Difficult to test components in isolation
- Hard to swap implementations
- Circular dependencies between modules

**Example**:
```python
# Anti-pattern: Tight coupling
class UserService:
    def __init__(self):
        self.db = PostgreSQLDatabase()  # Tight coupling to PostgreSQL
        self.cache = RedisCache()        # Tight coupling to Redis
        self.email = SendGridEmail()     # Tight coupling to SendGrid

    def create_user(self, user_data):
        # Now we're stuck with these specific implementations
        user = self.db.insert("users", user_data)
        self.cache.set(f"user:{user.id}", user)
        self.email.send_welcome(user.email)
        return user
```

**Consequences**:
- Can't test without actual database, cache, email service
- Can't switch to different database or email provider easily
- Dependencies are hidden (not visible in signature)
- Hard to mock for testing

**Solution**: Dependency Injection with interfaces

```python
# Better: Loose coupling via abstractions
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def insert(self, table, data): pass

class Cache(ABC):
    @abstractmethod
    def set(self, key, value): pass

class EmailService(ABC):
    @abstractmethod
    def send_welcome(self, email): pass

class UserService:
    def __init__(self, database: Database, cache: Cache, email: EmailService):
        self.db = database
        self.cache = cache
        self.email = email

    def create_user(self, user_data):
        # Dependencies are explicit and swappable
        user = self.db.insert("users", user_data)
        self.cache.set(f"user:{user.id}", user)
        self.email.send_welcome(user.email)
        return user

# Easy to test with mocks
def test_create_user():
    mock_db = MockDatabase()
    mock_cache = MockCache()
    mock_email = MockEmail()

    service = UserService(mock_db, mock_cache, mock_email)
    user = service.create_user({"name": "Test"})

    assert mock_db.insert_called
    assert mock_cache.set_called
```

**Prevention**:
- Use dependency injection
- Program to interfaces, not implementations
- Use IoC containers
- Make dependencies explicit in constructors
- Follow SOLID principles

---

## Integration Anti-Patterns

### Distributed Monolith

**Description**: Microservices that must all deploy together, defeating the purpose of microservices

**Symptoms**:
- Services share a database
- Synchronous coupling between all services
- Changes require coordinated deployments
- No independent deployment capability
- Distributed system complexity with monolith constraints

**Example**:
```
Service A ──────> Shared DB <────── Service B
    │                                   │
    │         Sync HTTP call            │
    └──────────────────────────────────>│
                                        │
                                        ▼
Service C <───────────────────── Service D
        (All services tightly coupled)
```

**Consequences**:
- All the complexity of distributed systems
- None of the benefits of microservices
- Deployment coordination nightmare
- Can't scale services independently
- More expensive to operate than a monolith

**Solution**: Proper service boundaries

```
Service A          Service B
    │                  │
    ▼                  ▼
Database A         Database B
    │                  │
    └──> Event Bus <───┘
         (Async communication)

Each service:
- Owns its data
- Deploys independently
- Communicates asynchronously
- Has clear boundaries
```

**Prevention**:
- Database per service pattern
- Async communication via events
- Design for independent deployment
- Clear service boundaries
- Question if microservices are needed

---

### Chatty APIs

**Description**: Multiple API calls required for simple operations

**Symptoms**:
- N+1 query patterns at API level
- Multiple round trips for related data
- High latency for simple operations
- Poor mobile performance
- Bandwidth waste

**Example**:
```
# Anti-pattern: Chatty API
GET /users/123           # Get user
GET /users/123/profile   # Get profile
GET /users/123/orders    # Get orders
GET /orders/456          # Get order details
GET /orders/457          # Get order details
GET /orders/458          # Get order details
# 6 requests for one user's data!
```

**Consequences**:
- High latency (network round trips)
- Poor mobile experience
- Increased server load
- Complex client code

**Solution**: Aggregate endpoints or GraphQL

```
# Better: Aggregate endpoint
GET /users/123?include=profile,orders

Response:
{
  "id": 123,
  "name": "John",
  "profile": {...},
  "orders": [
    {details included},
    {details included},
    {details included}
  ]
}

# Or use GraphQL
query {
  user(id: 123) {
    name
    profile { ... }
    orders { ... }
  }
}
```

**Prevention**:
- Design APIs around use cases
- Provide aggregation options
- Consider GraphQL for complex data needs
- Measure and optimize round trips
- Use include/expand parameters

---

### API Versioning Chaos

**Description**: No consistent versioning strategy leading to breaking changes

**Symptoms**:
- Breaking changes without version bumps
- Multiple versioning schemes (URL, header, query param)
- No deprecation policy
- Clients break unexpectedly
- No migration guides

**Consequences**:
- Client applications break without warning
- Loss of trust from API consumers
- Support burden for multiple undocumented versions
- Fear of making any changes

**Solution**: Consistent versioning strategy

```
# Clear versioning in URL
/v1/users  - Original version
/v2/users  - Breaking changes

# Deprecation headers
HTTP/1.1 200 OK
Sunset: Wed, 01 Jan 2026 00:00:00 GMT
Deprecation: true
Link: <https://docs.example.com/migration/v1-to-v2>; rel="deprecation"

# Clear policy
- Breaking changes → new major version
- 6 months deprecation notice
- 12 months support for old version
- Migration guide provided
```

**Prevention**:
- Choose one versioning strategy
- Document version policy
- Never make breaking changes in existing versions
- Provide migration guides
- Use deprecation headers

---

## Data Management Anti-Patterns

### Shared Database

**Description**: Multiple services or applications writing to the same database tables

**Symptoms**:
- Multiple services with direct database access
- Schema changes affect multiple services
- Impossible to scale services independently
- Tight coupling via shared data schema
- No clear data ownership

**Example**:
```
User Service ─┐
              │
Product Service ──> Shared Database
              │
Order Service ─┘

(All services read/write same tables)
```

**Consequences**:
- Schema changes break multiple services
- Can't optimize database for specific service
- No independent scaling
- Transaction coordination complexity
- Tight coupling defeats microservices benefits

**Solution**: Database per service pattern

```
User Service ────> User DB
                   (owns user data)
                        │
                        ▼
                   Event Bus
                        │
                        ▼
Product Service ──> Product DB
                   (owns product data)
                        │
                        ▼
                   Event Bus
                        │
                        ▼
Order Service ────> Order DB
                   (owns order data)
```

**Prevention**:
- Database per service pattern
- API-based data access only
- Event-driven data synchronization
- Clear data ownership
- Consider if microservices are appropriate

---

### Premature Optimization

**Description**: Optimizing before measuring or understanding actual bottlenecks

**Symptoms**:
- Complex caching before measuring performance
- Over-engineered for hypothetical scale
- Sacrificing clarity for micro-optimizations
- Building for millions of users with zero users
- Choosing "scalable" solutions for small problems

**Example**:
```python
# Anti-pattern: Premature optimization
class UserService:
    def __init__(self):
        # Complex multi-level caching before any performance testing
        self.l1_cache = LocalMemoryCache()
        self.l2_cache = RedisCache()
        self.l3_cache = MemcachedCache()
        # Database sharding before 100 users
        self.db_shard_manager = ShardManager(16)
        # Message queue for simple operations
        self.async_queue = RabbitMQQueue()

    def get_user(self, user_id):
        # Check 3 caches before database
        # for an app with 50 users
        pass
```

**Consequences**:
- Unnecessary complexity
- Harder to maintain and debug
- Wasted development time
- Harder to onboard new developers
- May actually perform worse

**Solution**: Measure, then optimize

```python
# Better: Start simple
class UserService:
    def __init__(self, database):
        self.db = database

    def get_user(self, user_id):
        return self.db.find_by_id(user_id)

# Add optimizations when measurements show need:
# 1. Measure performance
# 2. Identify actual bottleneck
# 3. Add simplest optimization that works
# 4. Measure again
```

**Principle**: "Make it work, make it right, make it fast" - in that order

**Prevention**:
- Measure before optimizing
- Start simple, add complexity when needed
- Focus on actual bottlenecks
- Document performance requirements
- Profile in production-like environments

---

### No Data Migration Strategy

**Description**: No plan for evolving database schema or migrating data

**Symptoms**:
- Manual SQL scripts for schema changes
- No rollback capability
- Data migrations in production without testing
- Lost track of schema version
- Fear of making database changes

**Consequences**:
- Risky deployments
- Data corruption during migrations
- Downtime during schema changes
- Inconsistent schemas across environments

**Solution**: Version-controlled migrations

```
migrations/
├── 001_initial_schema.sql
├── 002_add_user_avatar.sql
├── 003_add_order_status_index.sql
└── 004_migrate_user_addresses.sql

# Each migration:
- Has up and down scripts
- Is version controlled
- Is tested in staging
- Is idempotent
- Has rollback plan
```

**Prevention**:
- Use migration tools (Flyway, Liquibase, Alembic)
- Version control all schema changes
- Test migrations in staging
- Plan for zero-downtime deployments
- Document migration procedures

---

## Performance Anti-Patterns

### Synchronous Everything

**Description**: All operations block until complete, no async processing

**Symptoms**:
- Long API response times
- Blocking operations in request path
- Timeout cascades
- Poor scalability
- User waits for operations that don't need to be synchronous

**Example**:
```python
# Anti-pattern: Everything synchronous
def create_user(request):
    user = save_to_database(request.data)  # 50ms
    send_welcome_email(user.email)         # 200ms - user waits
    generate_pdf_report(user)              # 500ms - user waits
    update_analytics(user)                 # 100ms - user waits
    notify_admin(user)                     # 150ms - user waits
    # Total: 1000ms response time
    return user
```

**Consequences**:
- Long response times
- Poor user experience
- Timeouts and failures
- Can't scale horizontally
- Server resources tied up

**Solution**: Async for non-critical paths

```python
# Better: Async for non-critical operations
def create_user(request):
    user = save_to_database(request.data)  # 50ms - must be sync

    # Queue background tasks
    task_queue.enqueue(send_welcome_email, user.email)
    task_queue.enqueue(generate_pdf_report, user)
    task_queue.enqueue(update_analytics, user)
    task_queue.enqueue(notify_admin, user)

    # Fast response: 50ms
    return user
```

**Prevention**:
- Identify operations that can be async
- Use background job queues
- Event-driven for updates
- Return quickly, process later
- Monitor background job health

---

### No Caching Strategy

**Description**: No caching of frequently-accessed, rarely-changing data

**Symptoms**:
- Repeated expensive computations
- Database queries for static data
- Slow response times
- High database load
- Poor scalability

**Example**:
```python
# Anti-pattern: No caching
def get_product(product_id):
    # Query database every time
    # even though products rarely change
    return database.query(f"SELECT * FROM products WHERE id = {product_id}")
```

**Consequences**:
- Unnecessary load on database
- Slow response times
- High infrastructure costs
- Poor scalability

**Solution**: Strategic caching

```python
# Better: Cache rarely-changing data
def get_product(product_id):
    # Check cache first
    cached = cache.get(f"product:{product_id}")
    if cached:
        return cached

    # Query database if not cached
    product = database.query(f"SELECT * FROM products WHERE id = {product_id}")

    # Cache with appropriate TTL
    cache.set(f"product:{product_id}", product, ttl=3600)

    return product
```

**Caching Strategy Guidelines**:
- **Cache hot data**: Frequently accessed data
- **TTL based on change frequency**: Long TTL for static, short for dynamic
- **Invalidation strategy**: How to clear cache on updates
- **Cache warming**: Pre-populate cache for known hot data
- **Don't cache everything**: Caching has costs too

**Prevention**:
- Identify cacheable data
- Use appropriate TTLs
- Implement cache invalidation
- Monitor cache hit rates
- Balance cache size vs. benefit

---

## Development Process Anti-Patterns

### No Architecture Documentation

**Description**: Architecture exists only in developers' heads

**Symptoms**:
- No diagrams or written documentation
- New developers struggle to understand system
- Tribal knowledge required
- Inconsistent implementation across teams
- Architectural decisions lost to time

**Consequences**:
- Onboarding takes months
- Repeated mistakes
- Inconsistent patterns
- Lost architectural vision
- Can't justify decisions

**Solution**: Maintain architecture documentation

```
docs/architecture/
├── README.md                    # Overview and index
├── system-context.md            # External dependencies
├── container-diagram.md         # High-level structure
├── component-diagrams/          # Detailed component docs
├── api-contracts/               # API specifications
├── data-model.md                # Database schema
└── decisions/                   # Architecture Decision Records
    ├── 001-use-postgresql.md
    ├── 002-microservices-approach.md
    └── 003-event-driven-integration.md
```

**Prevention**:
- Document as you design
- Use C4 model or similar
- Maintain ADRs (Architecture Decision Records)
- Review and update documentation
- Make documentation accessible

---

### Analysis Paralysis

**Description**: Over-analyzing and never starting implementation

**Symptoms**:
- Months of design, no code
- Trying to make "perfect" architecture
- Every possible scenario considered
- Endless debate over minor details
- Fear of making wrong choice

**Consequences**:
- Opportunity cost of delayed delivery
- Market changes while planning
- Team frustration
- Requirements change before implementation
- Competitor ships first

**Solution**: Iterative architecture

```
1. Start with minimum viable architecture
2. Implement core functionality
3. Learn from real usage
4. Refine architecture based on learnings
5. Repeat
```

**Prevention**:
- Time-box architecture phase
- Start with "good enough" design
- Plan for iteration and evolution
- Accept that you can't predict everything
- Deliver incrementally

---

## Review Checklist

Use this checklist during architecture review to catch anti-patterns:

**Structural**:
- [ ] Components have single, clear responsibilities
- [ ] No God objects (classes >500 lines or >20 methods)
- [ ] Dependencies injected, not hardcoded
- [ ] Clear, documented interfaces between components

**Integration**:
- [ ] Services can deploy independently (if microservices)
- [ ] APIs designed around use cases, not chatty
- [ ] Consistent API versioning strategy
- [ ] Async communication where appropriate

**Data**:
- [ ] Clear data ownership per service
- [ ] No shared database between services
- [ ] Migration strategy in place
- [ ] Caching strategy for hot data

**Performance**:
- [ ] Non-critical operations are async
- [ ] Identified and measured bottlenecks
- [ ] Appropriate caching strategy
- [ ] No premature optimization

**Process**:
- [ ] Architecture documented (diagrams + text)
- [ ] Decision log maintained (ADRs)
- [ ] Clear deployment strategy
- [ ] Testing approach defined

**General**:
- [ ] Security built in, not bolted on
- [ ] Testability considered
- [ ] Monitoring and observability planned
- [ ] Scalability path identified

---

## When Anti-Patterns Are Acceptable

Sometimes anti-patterns are the right choice given constraints:

**Tight Coupling**: Acceptable for:
- Prototypes and MVPs
- Small, single-developer projects
- Components that truly must change together

**Shared Database**: Acceptable for:
- Legacy systems migration
- Small teams with co-located services
- Temporary during transition period

**Synchronous Operations**: Acceptable for:
- Critical operations requiring immediate confirmation
- Operations that must be atomic
- Simple, fast operations

**No Caching**: Acceptable for:
- Frequently changing data
- Small datasets
- Strong consistency requirements

**Key Principle**: Understand the trade-offs and make conscious decisions, not default choices.

---

## Additional Resources

For complementary architectural patterns and guidance:
- Refer back to SKILL.md for positive architectural patterns and other references
- Use C4 diagrams to visualize proper component boundaries and system structure
- Apply API contract best practices when designing service interfaces
