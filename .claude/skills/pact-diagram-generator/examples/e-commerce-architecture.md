# E-Commerce Platform Architecture

## Scenario

A modern e-commerce platform that allows customers to browse products, manage shopping carts, and complete purchases. The system integrates with third-party payment processors, inventory management, and shipping providers.

**Business Context**:
- Customers: Browse catalog, add to cart, checkout, track orders
- Merchants: Manage products, view orders, update inventory
- Admin: Platform administration, analytics, customer support

**Non-Functional Requirements**:
- Scalability: Handle Black Friday traffic spikes
- Availability: 99.9% uptime SLA
- Security: PCI DSS compliance for payment data
- Performance: Page load < 2 seconds, checkout < 5 seconds

## Architecture Overview

**Architecture Style**: Microservices with event-driven communication

**Technology Stack**:
- Frontend: React (web), React Native (mobile)
- Backend: Node.js microservices
- Databases: PostgreSQL (transactional), MongoDB (catalog), Redis (cache/session)
- Messaging: RabbitMQ (async events)
- Infrastructure: AWS (ECS, RDS, ElastiCache)

**Key Design Decisions**:
- **Microservices**: Independent scaling and deployment
- **Database per service**: Autonomy and bounded contexts
- **Event-driven**: Decouple order processing from inventory/shipping
- **API Gateway**: Single entry point, rate limiting, authentication

---

## Diagrams

### 1. System Context Diagram (C4 Level 1)

This diagram shows the E-Commerce Platform in the context of its users and external dependencies.

```mermaid
C4Context
  title System Context for E-Commerce Platform

  Person(customer, "Customer", "Browses products, makes purchases")
  Person(merchant, "Merchant", "Manages product inventory")
  Person(admin, "Admin", "Platform administration")

  System(ecommerce, "E-Commerce Platform", "Online retail platform")

  System_Ext(stripe, "Stripe", "Payment processing gateway")
  System_Ext(shippo, "Shippo", "Shipping rate calculation and label generation")
  System_Ext(sendgrid, "SendGrid", "Transactional email service")
  System_Ext(analytics, "Google Analytics", "User behavior tracking")

  Rel(customer, ecommerce, "Uses", "HTTPS")
  Rel(merchant, ecommerce, "Manages inventory via", "HTTPS")
  Rel(admin, ecommerce, "Administers platform via", "HTTPS")

  Rel(ecommerce, stripe, "Processes payments via", "HTTPS/REST")
  Rel(ecommerce, shippo, "Calculates shipping via", "HTTPS/REST")
  Rel(ecommerce, sendgrid, "Sends emails via", "HTTPS/REST")
  Rel(ecommerce, analytics, "Tracks events to", "JavaScript SDK")
```

**Key Elements**:
- **Customer**: Primary user persona, browses and purchases
- **Merchant**: Seller persona, manages products and inventory
- **Admin**: Platform operator, manages system configuration
- **External integrations**: Payment (Stripe), shipping (Shippo), email (SendGrid), analytics (Google Analytics)

**Tips for Adaptation**:
- Replace external systems with your chosen providers (e.g., PayPal instead of Stripe)
- Add additional personas (Supplier, Warehouse Manager, Customer Support)
- Include compliance systems (fraud detection, tax calculation)

---

### 2. Container Diagram (C4 Level 2)

This diagram zooms into the E-Commerce Platform, showing the deployable containers and their interactions.

```mermaid
C4Container
  title Container Architecture for E-Commerce Platform

  Person(customer, "Customer")
  Person(merchant, "Merchant")

  Container_Boundary(platform, "E-Commerce Platform") {
    Container(webApp, "Web Application", "React/S3", "Customer-facing website")
    Container(mobileApp, "Mobile App", "React Native", "iOS and Android apps")
    Container(merchantPortal, "Merchant Portal", "React/S3", "Merchant admin interface")

    Container(apiGateway, "API Gateway", "Kong", "Request routing, rate limiting, auth")

    Container(userService, "User Service", "Node.js/Express", "User authentication and profiles")
    Container(productService, "Product Service", "Node.js/Express", "Product catalog management")
    Container(cartService, "Cart Service", "Node.js/Express", "Shopping cart operations")
    Container(orderService, "Order Service", "Node.js/Express", "Order processing workflow")
    Container(inventoryService, "Inventory Service", "Node.js/Express", "Stock management")

    ContainerDb(userDB, "User Database", "PostgreSQL", "User accounts and profiles")
    ContainerDb(productDB, "Product Database", "MongoDB", "Product catalog and images")
    ContainerDb(orderDB, "Order Database", "PostgreSQL", "Orders and transactions")
    ContainerDb(inventoryDB, "Inventory Database", "PostgreSQL", "Stock levels")

    ContainerDb(cache, "Cache", "Redis", "Session storage, cart data")

    ContainerQueue(messageQueue, "Message Queue", "RabbitMQ", "Async event processing")
    Container(emailWorker, "Email Worker", "Node.js", "Background email job processor")
  }

  System_Ext(stripe, "Stripe", "Payment processing")
  System_Ext(shippo, "Shippo", "Shipping provider")
  System_Ext(sendgrid, "SendGrid", "Email delivery")

  Rel(customer, webApp, "Uses", "HTTPS")
  Rel(customer, mobileApp, "Uses")
  Rel(merchant, merchantPortal, "Uses", "HTTPS")

  Rel(webApp, apiGateway, "Calls", "HTTPS/REST")
  Rel(mobileApp, apiGateway, "Calls", "HTTPS/REST")
  Rel(merchantPortal, apiGateway, "Calls", "HTTPS/REST")

  Rel(apiGateway, userService, "Routes to", "HTTP/REST")
  Rel(apiGateway, productService, "Routes to", "HTTP/REST")
  Rel(apiGateway, cartService, "Routes to", "HTTP/REST")
  Rel(apiGateway, orderService, "Routes to", "HTTP/REST")
  Rel(apiGateway, inventoryService, "Routes to", "HTTP/REST")

  Rel(userService, userDB, "Reads/Writes", "JDBC")
  Rel(productService, productDB, "Reads/Writes", "MongoDB driver")
  Rel(orderService, orderDB, "Reads/Writes", "JDBC")
  Rel(inventoryService, inventoryDB, "Reads/Writes", "JDBC")

  Rel(cartService, cache, "Stores cart data", "Redis protocol")
  Rel(userService, cache, "Caches user sessions", "Redis protocol")

  Rel(orderService, stripe, "Processes payments", "HTTPS/REST")
  Rel(orderService, shippo, "Calculates shipping", "HTTPS/REST")

  Rel(orderService, messageQueue, "Publishes order events", "AMQP")
  Rel(inventoryService, messageQueue, "Subscribes to order events", "AMQP")
  Rel(emailWorker, messageQueue, "Subscribes to email events", "AMQP")

  Rel(emailWorker, sendgrid, "Sends emails", "HTTPS/REST")
```

**Key Elements**:
- **Frontend containers**: Web (React), Mobile (React Native), Merchant Portal
- **API Gateway**: Kong for routing, rate limiting, JWT validation
- **Microservices**: User, Product, Cart, Order, Inventory (each with bounded context)
- **Databases**: PostgreSQL for transactional data, MongoDB for product catalog
- **Cache**: Redis for sessions and shopping cart (ephemeral data)
- **Message Queue**: RabbitMQ for asynchronous order processing
- **Background worker**: Email worker processes async notification jobs

**Technology Choices**:
- **Node.js/Express**: Consistent runtime across services, non-blocking I/O
- **PostgreSQL**: ACID compliance for orders, inventory, users
- **MongoDB**: Flexible schema for product catalog with varying attributes
- **Redis**: In-memory cache for session data and cart (fast reads)
- **RabbitMQ**: Reliable message delivery for order events

**Tips for Adaptation**:
- Replace Kong with AWS API Gateway, NGINX, or Traefik
- Use AWS SQS/SNS instead of RabbitMQ for managed messaging
- Add CDN (CloudFront, Cloudflare) in front of web app
- Include search service (Elasticsearch) for product search

---

### 3. Component Diagram - Order Service (C4 Level 3)

This diagram zooms into the Order Service container, showing its internal components.

```mermaid
C4Component
  title Component Architecture for Order Service

  Container_Boundary(orderService, "Order Service") {
    Component(orderController, "Order Controller", "Express Controller", "HTTP request handling for orders")
    Component(checkoutController, "Checkout Controller", "Express Controller", "Checkout workflow orchestration")

    Component(orderManager, "Order Manager", "Service", "Order lifecycle management")
    Component(paymentProcessor, "Payment Processor", "Service", "Payment transaction handling")
    Component(shippingCalculator, "Shipping Calculator", "Service", "Shipping cost calculation")
    Component(orderValidator, "Order Validator", "Service", "Order validation rules")

    ComponentDb(orderRepository, "Order Repository", "Repository", "Database access for orders")
    ComponentDb(transactionRepository, "Transaction Repository", "Repository", "Payment transaction records")
  }

  ContainerDb(orderDB, "Order Database", "PostgreSQL", "Order and transaction data")

  System_Ext(stripe, "Stripe", "Payment gateway")
  System_Ext(shippo, "Shippo", "Shipping API")

  ContainerQueue(messageQueue, "Message Queue", "RabbitMQ")

  Container(inventoryService, "Inventory Service", "Node.js")

  Rel(orderController, orderManager, "Uses")
  Rel(checkoutController, orderManager, "Uses")
  Rel(checkoutController, paymentProcessor, "Uses")
  Rel(checkoutController, shippingCalculator, "Uses")

  Rel(orderManager, orderValidator, "Validates with")
  Rel(orderManager, orderRepository, "Persists via")
  Rel(paymentProcessor, transactionRepository, "Records transactions via")

  Rel(orderRepository, orderDB, "Reads/Writes", "JDBC")
  Rel(transactionRepository, orderDB, "Reads/Writes", "JDBC")

  Rel(paymentProcessor, stripe, "Charges card via", "HTTPS/REST")
  Rel(shippingCalculator, shippo, "Calculates rates via", "HTTPS/REST")

  Rel(orderManager, messageQueue, "Publishes OrderCreated event", "AMQP")
  Rel(orderManager, inventoryService, "Checks stock via", "HTTP/REST")
```

**Key Components**:
- **Controllers**: HTTP request handlers for order and checkout endpoints
- **Order Manager**: Core business logic for order lifecycle
- **Payment Processor**: Handles Stripe integration and payment state
- **Shipping Calculator**: Integrates with Shippo for shipping cost estimation
- **Order Validator**: Business rules (minimum order, address validation)
- **Repositories**: Data access layer with database abstraction

**Component Responsibilities**:
- **Order Controller**: `GET /orders`, `GET /orders/:id`, `PUT /orders/:id/cancel`
- **Checkout Controller**: `POST /checkout` (orchestrates validation, payment, order creation)
- **Order Manager**: Create order, update status, cancel order, emit events
- **Payment Processor**: Create charge, refund, handle payment webhooks
- **Shipping Calculator**: Calculate shipping cost based on weight, destination
- **Repositories**: CRUD operations, query by user, query by status

**Tips for Adaptation**:
- Add `OrderEventPublisher` component if complex event publishing logic
- Include `FraudDetector` component for fraud prevention
- Add `DiscountCalculator` for coupon/promo code support
- Separate `PaymentGatewayAdapter` interface with multiple implementations

---

### 4. Service Dependency Graph

This graph shows dependencies between microservices to identify coupling and potential circular dependencies.

```mermaid
graph TD
  subgraph "API Layer"
    apiGateway["API Gateway<br/>Kong"]
  end

  subgraph "Service Layer"
    userSvc["User Service<br/>Auth & profiles"]
    productSvc["Product Service<br/>Catalog management"]
    cartSvc["Cart Service<br/>Shopping cart"]
    orderSvc["Order Service<br/>Order processing"]
    inventorySvc["Inventory Service<br/>Stock management"]
  end

  subgraph "Data Layer"
    userDB[("User Database<br/>PostgreSQL")]
    productDB[("Product Database<br/>MongoDB")]
    orderDB[("Order Database<br/>PostgreSQL")]
    inventoryDB[("Inventory Database<br/>PostgreSQL")]
    cache[("Redis Cache<br/>Sessions & cart")]
  end

  subgraph "Async Communication"
    queue["Message Queue<br/>RabbitMQ"]
    emailWorker["Email Worker<br/>Notifications"]
  end

  subgraph "External Systems"
    stripe{{"Stripe<br/>Payments"}}
    shippo{{"Shippo<br/>Shipping"}}
    sendgrid{{"SendGrid<br/>Email"}}
  end

  %% API Gateway routes
  apiGateway --> userSvc
  apiGateway --> productSvc
  apiGateway --> cartSvc
  apiGateway --> orderSvc
  apiGateway --> inventorySvc

  %% Service dependencies (synchronous)
  orderSvc --> userSvc
  orderSvc --> productSvc
  orderSvc --> inventorySvc
  cartSvc --> productSvc

  %% Data access
  userSvc --> userDB
  productSvc --> productDB
  orderSvc --> orderDB
  inventorySvc --> inventoryDB

  %% Cache usage
  userSvc --> cache
  cartSvc --> cache

  %% Async messaging
  orderSvc -.->|"publishes events"| queue
  inventorySvc -.->|"subscribes"| queue
  emailWorker -.->|"subscribes"| queue

  %% External integrations
  orderSvc --> stripe
  orderSvc --> shippo
  emailWorker --> sendgrid

  %% Styling
  classDef service fill:#e1f5ff,stroke:#1976d2
  classDef data fill:#e8f5e9,stroke:#388e3c
  classDef async fill:#fff3e0,stroke:#f57c00
  classDef external fill:#fce4ec,stroke:#c2185b
  classDef gateway fill:#f3e5f5,stroke:#7b1fa2

  class userSvc,productSvc,cartSvc,orderSvc,inventorySvc service
  class userDB,productDB,orderDB,inventoryDB,cache data
  class queue,emailWorker async
  class stripe,shippo,sendgrid external
  class apiGateway gateway
```

**Dependency Analysis**:

**Order Service Dependencies (High Coupling)**:
- Synchronous: User Service, Product Service, Inventory Service, Stripe, Shippo
- Asynchronous: Message Queue
- **Impact**: Order Service is central orchestrator with most dependencies
- **Trade-off**: Acceptable for checkout workflow that needs real-time coordination

**Inventory Service**:
- Synchronous: Inventory Database only
- Asynchronous: Message Queue (subscribes to OrderCreated events)
- **Pattern**: Event-driven updates reduce coupling

**Cart Service**:
- Dependencies: Product Service (to validate products), Redis Cache
- **Pattern**: Stateless service, uses cache for cart storage

**No Circular Dependencies**: ✅ Clean dependency graph
- All dependencies flow in one direction (top to bottom)
- Async messaging prevents tight coupling
- Services don't depend on Order Service (one-way dependency)

**Recommendations**:
1. **Consider**: Circuit breaker for Order Service → External systems (Stripe, Shippo)
2. **Consider**: API composition layer to reduce frontend calls to multiple services
3. **Monitor**: Order Service latency (depends on 5 downstream systems)

**Tips for Adaptation**:
- Add more services (Review Service, Recommendation Service, Search Service)
- Show circular dependencies with dashed arrows: `A -.->|"circular"| B`
- Highlight high-coupling services with custom styling
- Include caching layers between services

---

## Key Architectural Patterns

### 1. Database Per Service

Each microservice owns its database schema, ensuring loose coupling and independent scaling.

**Benefits**:
- Service autonomy (deploy independently)
- Technology diversity (PostgreSQL for orders, MongoDB for products)
- Fault isolation (User DB failure doesn't affect Order Service)

**Trade-offs**:
- No distributed transactions (use Saga pattern for multi-service workflows)
- Data duplication (User email stored in Order records for denormalization)

### 2. API Gateway Pattern

Single entry point for all client requests, handles cross-cutting concerns.

**Responsibilities**:
- Request routing to appropriate service
- Authentication (JWT validation)
- Rate limiting (prevent abuse)
- Request/response transformation
- API versioning

**Benefits**:
- Simplified client logic (one endpoint instead of 5)
- Centralized security enforcement
- Protocol translation (REST to gRPC)

### 3. Event-Driven Architecture

Services communicate asynchronously via message queue for eventual consistency.

**Events**:
- `OrderCreated`: Published by Order Service, consumed by Inventory Service, Email Worker
- `InventoryReserved`: Published by Inventory Service
- `PaymentProcessed`: Published by Order Service

**Benefits**:
- Decoupling (Inventory Service doesn't know about Order Service implementation)
- Resilience (Message queue buffers during Inventory Service downtime)
- Scalability (Add more Email Worker instances for Black Friday)

**Trade-offs**:
- Eventual consistency (inventory not updated instantly)
- Debugging complexity (distributed tracing required)

### 4. CQRS (Command Query Responsibility Segregation)

Product Service uses separate read and write models.

**Write Model**: MongoDB (flexible schema for product attributes)
**Read Model**: Elasticsearch (optimized for search queries)

**Benefits**:
- Optimized queries (search across 1M+ products)
- Independent scaling (read-heavy workload needs more read replicas)

---

## Deployment Architecture

**Production Environment** (AWS):
- **API Gateway**: ECS Fargate (auto-scaling containers)
- **Microservices**: ECS Fargate (2 tasks per service minimum, scale to 10)
- **Databases**: RDS PostgreSQL Multi-AZ, DocumentDB (MongoDB-compatible)
- **Cache**: ElastiCache Redis cluster
- **Message Queue**: Amazon MQ (managed RabbitMQ)
- **Static Assets**: S3 + CloudFront CDN

**Regions**: Multi-region deployment (us-east-1 primary, us-west-2 failover)

**High Availability**:
- Load balancer across availability zones
- Database replication (RDS Multi-AZ)
- Autoscaling based on CPU and request count

---

## Related Diagrams

For complete architecture documentation, create these additional diagrams:

1. **Sequence Diagrams**:
   - Checkout flow (see `authentication-flow.md` for sequence pattern)
   - Payment processing sequence
   - Inventory reservation flow

2. **Additional Component Diagrams**:
   - Product Service components (search indexing, image processing)
   - User Service components (authentication, profile management)

3. **Deployment Diagram**:
   - AWS infrastructure (VPC, subnets, security groups)
   - CI/CD pipeline (build, test, deploy stages)

---

## Summary

This e-commerce architecture demonstrates:
- ✅ Microservices with clear bounded contexts
- ✅ Event-driven communication for decoupling
- ✅ Database per service for autonomy
- ✅ API Gateway for centralized cross-cutting concerns
- ✅ Scalable infrastructure with cloud-native services

**Use this as a template for**:
- E-commerce platforms
- Multi-service SaaS applications
- Event-driven architectures
- Payment processing integrations
