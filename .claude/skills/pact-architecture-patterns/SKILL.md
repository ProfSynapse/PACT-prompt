---
name: pact-architecture-patterns
description: |
  ARCHITECT PHASE: Architectural design patterns, component templates, and system design guidance.

  Provides proven architectural patterns including microservices, layered architecture,
  event-driven systems, C4 diagram templates, API contract formats, and design anti-patterns.

  Use when: designing system architecture, creating component diagrams, defining interfaces,
  planning component boundaries, choosing architectural patterns, organizing system modules,
  or when user mentions: architecture, components, system design, diagrams, C4, microservices,
  API contracts, service boundaries, architectural patterns.

  Use for: component design, interface definition, system boundaries, dependency management,
  architecture documentation, design patterns, integration patterns.

  DO NOT use for: code implementation details, specific framework syntax, database schema design,
  frontend-specific patterns, testing strategies, or security implementation (use dedicated skills).
allowed-tools:
  - Read
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Architect"
  version: "1.0.0"
  updated: "2025-12-04"
  primary-agent: "pact-architect"
---

# Architecture Patterns Reference

## Overview

This skill provides proven architectural patterns, design templates, and best practices
for the PACT Architect phase. Use these patterns when designing system architecture,
defining component boundaries, and creating implementation-ready specifications.

## Quick Reference: Common Patterns

### 1. Layered Architecture
**When to use**: Traditional applications with clear separation of concerns
**Structure**: Presentation → Business Logic → Data Access → Database
**Benefits**: Clear separation, testability, familiar pattern
**Trade-offs**: Can become rigid, vertical slicing challenges

### 2. Microservices Architecture
**When to use**: Large-scale systems requiring independent deployment
**Structure**: Independent services with well-defined APIs
**Benefits**: Scalability, technology diversity, fault isolation
**Trade-offs**: Operational complexity, distributed system challenges

### 3. Event-Driven Architecture
**When to use**: Systems requiring loose coupling and async processing
**Structure**: Event producers → Message broker → Event consumers
**Benefits**: Decoupling, scalability, flexibility
**Trade-offs**: Eventual consistency, debugging complexity

### 4. Hexagonal Architecture (Ports & Adapters)
**When to use**: Applications requiring high testability and technology independence
**Structure**: Core domain logic surrounded by adapters for external systems
**Benefits**: Testability, technology agnostic, clear boundaries
**Trade-offs**: More initial complexity, learning curve

### 5. CQRS (Command Query Responsibility Segregation)
**When to use**: Complex domains with different read/write patterns
**Structure**: Separate models and paths for commands and queries
**Benefits**: Performance optimization, scaling flexibility
**Trade-offs**: Increased complexity, eventual consistency challenges

## Architectural Decision Workflow

For complex pattern selection and system design, use sequential-thinking to reason through decisions systematically.

**When to use sequential-thinking:**
- Choosing between multiple viable architectural patterns
- Evaluating trade-offs for a specific context
- Designing component boundaries for complex systems
- Resolving conflicting requirements (e.g., performance vs. simplicity)

**Workflow:**

1. **Frame the Decision**
   - What architectural question needs answering?
   - What are the constraints and requirements?
   - What patterns are candidates?

2. **Analyze Each Option** (use sequential-thinking)
   - How does each pattern address the requirements?
   - What are the trade-offs in this specific context?
   - What risks does each option introduce?

3. **Evaluate Against Principles**
   - Does it follow SOLID principles?
   - Does it avoid known anti-patterns?
   - Is it appropriate for the team's expertise?

4. **Document the Decision**
   - Record the chosen pattern and rationale
   - Note rejected alternatives and why
   - Identify risks and mitigations

**Example sequential-thinking prompt:**
> "I need to choose between microservices and modular monolith for a mid-size e-commerce platform with a team of 5 developers. Let me think through the trade-offs systematically..."

## Decision Tree: Which Reference to Load?

**Need diagram templates?**
→ See `references/c4-templates.md`
  - Component diagrams
  - Container diagrams
  - Deployment diagrams
  - ASCII art examples

**Designing APIs?**
→ See `references/api-contracts.md`
  - REST API patterns
  - GraphQL patterns
  - API versioning strategies
  - Error handling standards

**Avoiding common mistakes?**
→ See `references/anti-patterns.md`
  - Big Ball of Mud
  - God Objects
  - Tight coupling issues
  - Over-engineering patterns

## Core Design Principles

Apply these principles to all architectural decisions:

1. **Single Responsibility**: Each component has one clear purpose
2. **Open/Closed**: Design for extension without modification
3. **Dependency Inversion**: Depend on abstractions, not implementations
4. **Interface Segregation**: Many specific interfaces over one general
5. **Separation of Concerns**: Isolate different aspects of functionality
6. **Loose Coupling**: Minimize dependencies between components
7. **High Cohesion**: Related functionality grouped together

## Component Design Workflow

1. **Identify Responsibilities**: What does this component do?
2. **Define Boundaries**: What's in scope vs. out of scope?
3. **Design Interfaces**: How do other components interact?
4. **Map Data Flow**: How does information move through the system?
5. **Consider Non-Functionals**: Security, performance, scalability needs
6. **Document Decisions**: Create clear specifications for implementers

## Example: Simple REST API Architecture

```
┌─────────────────┐
│   API Gateway   │ ← Entry point, routing, rate limiting
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ User   │ │Product │ ← Domain services
│Service │ │Service │
└───┬────┘ └───┬────┘
    │          │
    ▼          ▼
┌──────────────────┐
│    Database      │ ← Shared or separate DBs
└──────────────────┘
```

**Components**:
- **API Gateway**: Request routing, authentication, rate limiting
- **User Service**: User management, authentication, profiles
- **Product Service**: Product catalog, inventory, search
- **Database**: Data persistence (consider separate DBs per service)

**For complete C4 diagram templates**: See `references/c4-templates.md`

## Technology Selection Framework

When choosing technologies, consider:

1. **Team Expertise**: Does the team know this technology?
2. **Community Support**: Active development, documentation, plugins?
3. **Scalability**: Does it meet performance and scale requirements?
4. **Maintainability**: Can we maintain and debug this long-term?
5. **Cost**: Licensing, infrastructure, operational costs?
6. **Integration**: Does it work with existing systems?

## Common Architecture Patterns by Use Case

**Web Applications**:
- Small-Medium: Layered architecture with MVC
- Large: Microservices with API gateway
- Real-time: Event-driven with WebSockets

**Data Processing**:
- Batch: Pipeline architecture
- Stream: Event-driven with message queues
- Analytics: Lambda architecture (batch + stream)

**Mobile Backends**:
- BFF (Backend for Frontend) pattern
- GraphQL for flexible queries
- CDN for static content

**Enterprise Systems**:
- Service-oriented architecture (SOA)
- Enterprise service bus (ESB)
- Monorepo with shared libraries

## Interface Design Best Practices

1. **Explicit Contracts**: Document all inputs, outputs, and side effects
2. **Version Management**: Plan for API evolution from day one
3. **Error Handling**: Define standard error formats and codes
4. **Idempotency**: Design operations to be safely retryable
5. **Rate Limiting**: Protect services from overload
6. **Authentication**: Secure all interfaces appropriately

## Deployment Patterns

**Single Deployment**: Simple applications, all components together
**Blue-Green**: Zero-downtime deployments with instant rollback
**Canary**: Gradual rollout to subset of users
**Rolling**: Sequential updates across instances
**Feature Flags**: Deploy code, enable features independently

## Scalability Strategies

**Vertical Scaling**: Increase resources on single machine
**Horizontal Scaling**: Add more machines (requires stateless design)
**Caching**: Redis, CDN, application-level caching
**Load Balancing**: Distribute traffic across instances
**Database Sharding**: Split data across multiple databases
**Read Replicas**: Separate read and write database instances

## Security Architecture Basics

1. **Defense in Depth**: Multiple layers of security
2. **Principle of Least Privilege**: Minimal permissions required
3. **Secure by Default**: Security enabled out of the box
4. **Input Validation**: Validate and sanitize all inputs
5. **Authentication & Authorization**: Who are you? What can you do?
6. **Encryption**: In transit (TLS) and at rest
7. **Audit Logging**: Track security-relevant events

## Documentation Standards

Your architecture documentation should include:

1. **Context Diagram**: System boundaries and external dependencies
2. **Container Diagram**: High-level technology choices
3. **Component Diagram**: Internal structure of containers
4. **Deployment Diagram**: Infrastructure and runtime environment
5. **API Specifications**: Complete interface definitions
6. **Data Model**: Entities, relationships, and constraints
7. **Decision Log**: Why key architectural choices were made

## Additional Resources

- **Comprehensive diagram templates**: `references/c4-templates.md`
- **API contract examples**: `references/api-contracts.md`
- **Common pitfalls to avoid**: `references/anti-patterns.md`

## Integration with PACT Workflow

**Input from Prepare Phase**:
- Requirements documentation
- Technology research
- Constraints and assumptions
- Stakeholder needs

**Output for Code Phase**:
- Component specifications
- Interface definitions
- Implementation guidelines
- Architecture diagrams
- Technology stack decisions

**Quality Gates**:
- All requirements addressed
- Components have clear responsibilities
- Interfaces are well-defined
- Non-functional requirements considered
- Security built into design
- Deployment strategy defined
- Testing approach documented
