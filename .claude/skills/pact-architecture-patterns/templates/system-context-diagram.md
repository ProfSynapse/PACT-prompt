# System Context Diagram Template (C4 Level 1)

## System: [System Name]

### Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USERS & ACTORS                            │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │  Actor   │    │  Actor   │    │  Actor   │                  │
│  │   [1]    │    │   [2]    │    │   [3]    │                  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                  │
│       │               │               │                          │
└───────┼───────────────┼───────────────┼──────────────────────────┘
        │               │               │
        ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    ┌─────────────────────┐                      │
│                    │                     │                      │
│                    │   [SYSTEM NAME]     │                      │
│                    │                     │                      │
│                    │   [Brief desc of    │                      │
│                    │    what system      │                      │
│                    │    does]            │                      │
│                    │                     │                      │
│                    └──────────┬──────────┘                      │
│                               │                                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   External   │       │   External   │       │   External   │
│   System 1   │       │   System 2   │       │   System 3   │
│              │       │              │       │              │
│ [Provider/   │       │ [Payment/    │       │ [Analytics/  │
│  Identity]   │       │  Billing]    │       │  Reporting]  │
└──────────────┘       └──────────────┘       └──────────────┘
```

### Actors

| Actor | Type | Description | Interaction |
|-------|------|-------------|-------------|
| [Actor 1] | [User/Admin/System] | [Who they are] | [How they interact] |
| [Actor 2] | [User/Admin/System] | [Who they are] | [How they interact] |

### External Systems

| System | Type | Purpose | Protocol |
|--------|------|---------|----------|
| [System 1] | [SaaS/Internal/Partner] | [What it provides] | [REST/gRPC/SFTP] |
| [System 2] | [SaaS/Internal/Partner] | [What it provides] | [REST/gRPC/SFTP] |

### Key Interactions

1. **[Actor] → [System]**: [Description of primary flow]
2. **[System] → [External]**: [Description of integration]
3. **[External] → [System]**: [Description of callback/webhook]

### Boundaries

- **Trust Boundary**: [What's inside vs outside the security perimeter]
- **Data Boundary**: [What data stays internal vs shared externally]
- **Compliance Boundary**: [Regulatory considerations]

---
*Generated from pact-architecture-patterns skill template*
