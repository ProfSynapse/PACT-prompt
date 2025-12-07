# Service Scaffold Template

## Service: [ServiceName]

### Directory Structure

```
src/
├── [service-name]/
│   ├── __init__.py              # Python: module init
│   ├── index.ts                 # TypeScript: barrel export
│   │
│   ├── domain/                  # Business logic layer
│   │   ├── entities/            # Domain entities
│   │   │   └── [entity].ts
│   │   ├── services/            # Domain services
│   │   │   └── [service].ts
│   │   └── events/              # Domain events
│   │       └── [event].ts
│   │
│   ├── application/             # Use cases / Application services
│   │   ├── commands/            # Write operations
│   │   │   └── [command].ts
│   │   ├── queries/             # Read operations
│   │   │   └── [query].ts
│   │   └── handlers/            # Event handlers
│   │       └── [handler].ts
│   │
│   ├── infrastructure/          # External concerns
│   │   ├── persistence/         # Database access
│   │   │   ├── repositories/
│   │   │   └── migrations/
│   │   ├── messaging/           # Queue/event infrastructure
│   │   └── external/            # Third-party integrations
│   │
│   └── presentation/            # API layer
│       ├── controllers/         # HTTP controllers
│       ├── middleware/          # Request middleware
│       └── dto/                 # Data transfer objects
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── config/
    ├── default.ts
    └── production.ts
```

### Core Files

#### Domain Entity Template
```typescript
// domain/entities/[entity].ts
export interface [Entity]Props {
  id: string;
  // Add properties
}

export class [Entity] {
  private constructor(private readonly props: [Entity]Props) {}

  static create(props: Omit<[Entity]Props, 'id'>): [Entity] {
    return new [Entity]({
      id: generateId(),
      ...props,
    });
  }

  // Getters
  get id(): string {
    return this.props.id;
  }

  // Business methods
}
```

#### Repository Interface Template
```typescript
// domain/repositories/[entity]-repository.ts
export interface [Entity]Repository {
  findById(id: string): Promise<[Entity] | null>;
  save(entity: [Entity]): Promise<void>;
  delete(id: string): Promise<void>;
}
```

#### Use Case Template
```typescript
// application/commands/[action]-[entity].ts
export interface [Action][Entity]Command {
  // Command properties
}

export class [Action][Entity]Handler {
  constructor(
    private readonly repository: [Entity]Repository,
    private readonly eventBus: EventBus,
  ) {}

  async execute(command: [Action][Entity]Command): Promise<Result> {
    // 1. Validate command
    // 2. Load/create entity
    // 3. Execute business logic
    // 4. Persist changes
    // 5. Publish events
    // 6. Return result
  }
}
```

#### Controller Template
```typescript
// presentation/controllers/[entity]-controller.ts
export class [Entity]Controller {
  constructor(private readonly handler: [Action][Entity]Handler) {}

  async [action](req: Request, res: Response): Promise<void> {
    const command = this.mapToCommand(req.body);
    const result = await this.handler.execute(command);

    if (result.isFailure) {
      res.status(400).json({ error: result.error });
      return;
    }

    res.status(200).json(result.value);
  }
}
```

### Configuration Checklist

- [ ] Environment variables defined
- [ ] Database connection configured
- [ ] Logging configured
- [ ] Health check endpoint added
- [ ] Error handling middleware added
- [ ] Request validation middleware added
- [ ] Authentication middleware configured
- [ ] Rate limiting configured

---
*Generated from pact-backend-patterns skill template*
