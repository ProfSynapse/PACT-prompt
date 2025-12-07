# Component Specification Template

## Component: [Component Name]

### Overview
**Purpose**: [One-sentence description of what this component does]
**Domain**: [Business domain this component belongs to]
**Type**: [Service | Library | Module | API | Worker]

### Responsibilities
- [ ] [Primary responsibility 1]
- [ ] [Primary responsibility 2]
- [ ] [Primary responsibility 3]

### Dependencies

#### Upstream (This component depends on)
| Dependency | Type | Purpose |
|------------|------|---------|
| [Name] | [Service/Library/External] | [Why needed] |

#### Downstream (Depends on this component)
| Consumer | Integration Type | Contract |
|----------|------------------|----------|
| [Name] | [REST/gRPC/Event] | [Link to contract] |

### Interface Contract

#### Public API
```typescript
// Define the public interface this component exposes
interface [ComponentName]Service {
  // Method signatures
}
```

#### Events Published
| Event | Payload | Trigger |
|-------|---------|---------|
| [EventName] | [Schema reference] | [When emitted] |

#### Events Consumed
| Event | Source | Handler |
|-------|--------|---------|
| [EventName] | [Producer] | [Handler function] |

### Data Ownership
**Entities Owned**: [List entities this component is source of truth for]
**Read-Only Access**: [List entities accessed but not owned]

### Non-Functional Requirements
- **Availability**: [Target SLA, e.g., 99.9%]
- **Latency**: [P50/P99 targets]
- **Throughput**: [Expected RPS]
- **Data Retention**: [How long data is kept]

### Security Considerations
- **Authentication**: [How callers authenticate]
- **Authorization**: [Permission model]
- **Data Sensitivity**: [PII, financial, etc.]

### Deployment
- **Scaling Strategy**: [Horizontal/Vertical, triggers]
- **Resource Requirements**: [CPU/Memory baseline]
- **Health Check**: [Endpoint and criteria]

---
*Generated from pact-architecture-patterns skill template*
