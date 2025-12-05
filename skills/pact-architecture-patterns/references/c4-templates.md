# C4 Diagram Templates

> **When to use**: Creating architectural diagrams for documentation
> **Phase**: PACT Architect phase documentation

## Table of Contents

1. Component Diagram Template
2. Container Diagram Template
3. Deployment Diagram Template
4. Context Diagram Template
5. Notation Guide
6. Example: E-Commerce System

---

## Overview

The C4 model provides a hierarchical way to visualize software architecture at different levels of detail. These ASCII art templates enable clear, text-based architectural diagrams that are version-controllable and easy to create.

**The Four C's**:
- **Context**: System boundary and external dependencies
- **Container**: High-level technology choices
- **Component**: Internal structure within containers
- **Code**: Class/module level (optional, usually skipped)

---

## Component Diagram Template

**Purpose**: Show major components and their relationships within a system

### Template

```
┌─────────────────────────────────────────────────────────────┐
│                     [System/Container Name]                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐              ┌────────────────┐         │
│  │  Component A   │──────────────>│  Component B   │         │
│  │                │              │                │         │
│  │ - Responsibility            │ - Responsibility            │
│  │ - Key behaviors             │ - Key behaviors             │
│  └────────┬───────┘              └────────┬───────┘         │
│           │                               │                 │
│           │                               │                 │
│           ▼                               ▼                 │
│  ┌──────────────────────────────────────────────┐           │
│  │              Component C                     │           │
│  │                                              │           │
│  │ - Responsibility                             │           │
│  │ - Key behaviors                              │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### When to Use

- High-level system overview
- Showing component interactions
- Documenting major subsystems
- Planning module organization

### Key Elements

- **Component boxes**: Major functional units
- **Arrows**: Data flow or dependencies
- **Responsibilities**: Brief description of purpose
- **Behaviors**: Key operations performed

---

## Container Diagram Template

**Purpose**: Show deployable units and their runtime relationships

### Template

```
┌─────────────────────────────────────────────────────────────┐
│                     [System Name]                            │
└─────────────────────────────────────────────────────────────┘

┌───────────────────┐          ┌───────────────────┐
│   Web Browser     │          │   Mobile App      │
│   [Container]     │          │   [Container]     │
│                   │          │                   │
│   Technology:     │          │   Technology:     │
│   HTML/CSS/JS     │          │   React Native    │
└─────────┬─────────┘          └─────────┬─────────┘
          │                              │
          │         HTTPS/JSON           │
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────┐
│            API Application                       │
│            [Container]                           │
│                                                  │
│   Technology: Node.js, Express                   │
│   Responsibilities: Business logic, auth         │
└───────────────────┬─────────────────────────────┘
                    │
                    │ SQL/ORM
                    │
                    ▼
          ┌─────────────────────┐
          │     Database         │
          │     [Container]      │
          │                      │
          │   Technology:        │
          │   PostgreSQL         │
          └──────────────────────┘
```

### When to Use

- Showing deployment architecture
- Technology stack documentation
- Runtime dependencies
- Network boundaries

### Key Elements

- **Container type**: Web app, API, database, etc.
- **Technology stack**: Specific technologies used
- **Communication protocols**: HTTP, SQL, message queues
- **Deployment boundaries**: What runs where

---

## Deployment Diagram Template

**Purpose**: Show physical deployment infrastructure

### Template

```
┌─────────────────────────────────────────────────────────────┐
│                      Production Environment                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │              Load Balancer                    │           │
│  │              (AWS ALB)                        │           │
│  └──────────────────┬───────────────────────────┘           │
│                     │                                        │
│      ┌──────────────┼──────────────┐                         │
│      │              │              │                         │
│      ▼              ▼              ▼                         │
│  ┌──────┐       ┌──────┐       ┌──────┐                     │
│  │ App  │       │ App  │       │ App  │                     │
│  │Server│       │Server│       │Server│                     │
│  │ EC2  │       │ EC2  │       │ EC2  │                     │
│  └───┬──┘       └───┬──┘       └───┬──┘                     │
│      │              │              │                         │
│      └──────────────┼──────────────┘                         │
│                     │                                        │
│                     ▼                                        │
│           ┌─────────────────┐                                │
│           │   RDS Database  │                                │
│           │   (PostgreSQL)  │                                │
│           │                 │                                │
│           │   - Multi-AZ    │                                │
│           │   - Automated   │                                │
│           │     backups     │                                │
│           └─────────────────┘                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### When to Use

- Infrastructure planning
- DevOps documentation
- Capacity planning
- Disaster recovery planning

### Key Elements

- **Infrastructure services**: Load balancers, servers, databases
- **Cloud providers**: AWS, Azure, GCP specific services
- **Redundancy**: Multiple instances, failover
- **Network zones**: Public/private subnets, VPCs

---

## Context Diagram Template

**Purpose**: Show system boundary and external dependencies

### Template

```
                    ┌──────────────────┐
                    │   Customer       │
                    │   [Person]       │
                    └────────┬─────────┘
                             │
                             │ Uses
                             │
                             ▼
      ┌──────────────────────────────────────────┐
      │                                          │
      │         [Your System Name]               │
      │                                          │
      │   Core functionality and purpose         │
      │                                          │
      └────┬─────────────────────────────────┬───┘
           │                                 │
           │ Sends email                     │ Reads/writes
           │                                 │
           ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  Email Service   │              │   Database       │
│  [External]      │              │   [External]     │
│                  │              │                  │
│  SendGrid        │              │   PostgreSQL     │
└──────────────────┘              └──────────────────┘
```

### When to Use

- Project kickoff documentation
- Stakeholder communication
- System boundary definition
- External dependency mapping

### Key Elements

- **System boundary**: Clear box around your system
- **External actors**: People, systems that interact
- **External systems**: Third-party services, databases
- **Relationship labels**: Brief description of interaction

---

## Notation Guide

### Arrow Types

```
────>   Synchronous call (request/response)
----->  Asynchronous message (fire and forget)
═══>    Data flow (bulk data transfer)
<───>   Bidirectional communication
```

### Box Types

```
┌────┐
│    │  Service or Component
└────┘

[    ]  External system or person

(    )  Database or data store

{    }  Message queue or broker

<    >  Cloud service or managed service
```

### Relationship Labels

Always label arrows with:
- **Protocol**: HTTP, SQL, AMQP, etc.
- **Format**: JSON, XML, Protocol Buffers, etc.
- **Purpose**: Brief description of what's being communicated

Example: `HTTP/JSON - User authentication requests`

---

## Example: E-Commerce System

### Context Diagram

```
                  ┌──────────────┐
                  │  Customer    │
                  └──────┬───────┘
                         │ Browses, purchases
                         ▼
      ┌──────────────────────────────────┐
      │                                  │
      │    E-Commerce Platform           │
      │                                  │
      │  Online shopping system          │
      └────┬────────────────────────┬────┘
           │                        │
           │ Processes               │ Sends
           │ payments                │ notifications
           ▼                        ▼
┌──────────────────┐      ┌──────────────────┐
│  Payment Gateway │      │  Email Service   │
│  [Stripe]        │      │  [SendGrid]      │
└──────────────────┘      └──────────────────┘
```

### Container Diagram

```
┌───────────────┐
│ Web Browser   │
└───────┬───────┘
        │ HTTPS/JSON
        ▼
┌─────────────────────┐
│   API Gateway       │
│   [Node.js/Express] │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌──────────┐
│User     │ │Product   │
│Service  │ │Service   │
│[Node.js]│ │[Node.js] │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│   PostgreSQL DB     │
└─────────────────────┘
```

### Component Diagram (Product Service)

```
┌─────────────────────────────────────────────────────┐
│              Product Service                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────┐      ┌──────────────────┐      │
│  │ Product         │─────>│  Inventory       │      │
│  │ Controller      │      │  Manager         │      │
│  │                 │      │                  │      │
│  │ - Handle HTTP   │      │ - Track stock    │      │
│  │ - Validate input│      │ - Update qty     │      │
│  └────────┬────────┘      └─────────┬────────┘      │
│           │                         │               │
│           │                         │               │
│           ▼                         ▼               │
│  ┌──────────────────────────────────────────┐       │
│  │          Product Repository              │       │
│  │                                          │       │
│  │ - Database queries                       │       │
│  │ - Data mapping                           │       │
│  └──────────────────────────────────────────┘       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Best Practices

1. **Keep It Simple**: Don't show every detail, focus on key relationships
2. **Label Everything**: Clear labels on all arrows and boxes
3. **Consistent Notation**: Use the same style throughout all diagrams
4. **Level Appropriate**: Match detail level to audience
5. **Update Regularly**: Keep diagrams in sync with implementation
6. **Version Control**: Text-based diagrams are easy to diff and track

## Common Mistakes to Avoid

- **Too Much Detail**: Overwhelming diagrams lose their value
- **Missing Labels**: Unlabeled arrows are ambiguous
- **Mixing Levels**: Don't mix context and component level in one diagram
- **No Legend**: Always explain custom notation
- **Stale Diagrams**: Out-of-date diagrams are worse than none

## Tools for Enhancement

While ASCII diagrams work well for documentation, consider these tools for more polished output:

- **PlantUML**: Text-based UML diagrams
- **Mermaid**: Markdown-based diagrams (GitHub supported)
- **Draw.io**: Visual diagramming tool
- **Structurizr**: C4 model specific tooling
- **Lucidchart**: Collaborative diagramming

However, the ASCII templates here are immediately usable without additional tools and work great in markdown documentation.

---

## Additional Resources

For complementary architectural patterns and guidance:
- Refer back to SKILL.md for other architecture references
- Consider API contract patterns when defining service interfaces
- Review anti-patterns to avoid common architectural mistakes
