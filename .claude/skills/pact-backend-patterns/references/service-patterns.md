# Service Layer Patterns Reference

## Overview

This reference provides detailed patterns for structuring backend services following clean architecture principles. These patterns promote separation of concerns, testability, and maintainability.

## Repository Pattern

### Purpose

The Repository pattern abstracts data access logic, providing a collection-like interface for accessing domain objects. It decouples the business logic from data access implementation details.

### Key Principles

- Repository is a mediator between domain and data mapping layers
- Provides collection-like interface (add, remove, find)
- Hides database implementation details
- Returns domain objects, not database records
- One repository per aggregate root

### Structure

```
Repository Interface (Contract)
├── Define methods (findById, findAll, create, update, delete)
├── Use domain types in signatures
└── No implementation details

Repository Implementation
├── Implements interface contract
├── Contains database-specific logic
├── Maps between database records and domain models
└── Handles database connections and queries
```

### Implementation Example (TypeScript)

```typescript
// Domain model
interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

// Repository interface
interface UserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findAll(options?: PaginationOptions): Promise<User[]>;
  create(user: Omit<User, 'id' | 'createdAt'>): Promise<User>;
  update(id: string, updates: Partial<User>): Promise<User>;
  delete(id: string): Promise<void>;
}

// Repository implementation (e.g., PostgreSQL)
class PostgresUserRepository implements UserRepository {
  constructor(private db: Database) {}

  async findById(id: string): Promise<User | null> {
    const row = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return row ? this.mapToUser(row) : null;
  }

  async create(userData: Omit<User, 'id' | 'createdAt'>): Promise<User> {
    const result = await this.db.query(
      'INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *',
      [userData.email, userData.name]
    );
    return this.mapToUser(result);
  }

  private mapToUser(row: DatabaseRow): User {
    return {
      id: row.id,
      email: row.email,
      name: row.name,
      createdAt: new Date(row.created_at)
    };
  }
}
```

### Implementation Example (Python)

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, email: str, name: str) -> User:
        pass

class SQLUserRepository(UserRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def find_by_id(self, user_id: str) -> Optional[User]:
        cursor = self.db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return self._map_to_user(row) if row else None

    def create(self, email: str, name: str) -> User:
        cursor = self.db.execute(
            "INSERT INTO users (email, name) VALUES (?, ?) RETURNING *",
            (email, name)
        )
        return self._map_to_user(cursor.fetchone())

    def _map_to_user(self, row) -> User:
        return User(
            id=row['id'],
            email=row['email'],
            name=row['name'],
            created_at=row['created_at']
        )
```

### Benefits

- **Testability**: Service layer can use mock repositories for testing
- **Flexibility**: Can swap database implementations without changing business logic
- **Separation of Concerns**: Data access logic isolated from business logic
- **Consistency**: Centralized place for all data access operations

### When to Use

- ✅ Any application with business logic that accesses data
- ✅ When you need to support multiple data sources
- ✅ When testability is important
- ✅ When data access logic is complex

### When NOT to Use

- ❌ Simple CRUD applications with no business logic
- ❌ Prototypes or proof-of-concept code
- ❌ When performance requires database-specific optimizations throughout

## Service Pattern

### Purpose

The Service pattern encapsulates business logic and orchestrates operations across multiple repositories or external services. Services implement use cases and business rules.

### Key Principles

- Contains business logic, not data access logic
- Orchestrates repositories and other services
- Validates business rules
- Manages transactions
- Returns domain models or DTOs
- One service per bounded context or aggregate

### Structure

```
Service Layer
├── Business logic and validation
├── Transaction management
├── Orchestration of repositories
├── Coordination of other services
└── Error handling and logging
```

### Implementation Example (TypeScript)

```typescript
interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
}

class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService,
    private passwordHasher: PasswordHasher,
    private logger: Logger
  ) {}

  async createUser(request: CreateUserRequest): Promise<User> {
    // Business validation
    if (!this.isValidEmail(request.email)) {
      throw new ValidationError('Invalid email format');
    }

    // Check business rules
    const existingUser = await this.userRepository.findByEmail(request.email);
    if (existingUser) {
      throw new ConflictError('User with this email already exists');
    }

    // Orchestrate operations
    try {
      const hashedPassword = await this.passwordHasher.hash(request.password);

      const user = await this.userRepository.create({
        email: request.email,
        name: request.name,
        passwordHash: hashedPassword
      });

      // Trigger side effects
      await this.emailService.sendWelcomeEmail(user.email);

      this.logger.info('User created', { userId: user.id });

      return user;
    } catch (error) {
      this.logger.error('Failed to create user', { error, request });
      throw error;
    }
  }

  async getUserById(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);

    if (!user) {
      throw new NotFoundError(`User not found: ${id}`);
    }

    return user;
  }

  private isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}
```

### Implementation Example (Python)

```python
class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        password_hasher: PasswordHasher,
        logger: Logger
    ):
        self.user_repo = user_repository
        self.email_service = email_service
        self.password_hasher = password_hasher
        self.logger = logger

    def create_user(self, email: str, name: str, password: str) -> User:
        # Business validation
        if not self._is_valid_email(email):
            raise ValidationError("Invalid email format")

        # Check business rules
        existing_user = self.user_repo.find_by_email(email)
        if existing_user:
            raise ConflictError("User with this email already exists")

        # Orchestrate operations
        try:
            hashed_password = self.password_hasher.hash(password)

            user = self.user_repo.create(
                email=email,
                name=name,
                password_hash=hashed_password
            )

            # Trigger side effects
            self.email_service.send_welcome_email(user.email)

            self.logger.info(f"User created: {user.id}")

            return user
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> User:
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise NotFoundError(f"User not found: {user_id}")

        return user

    def _is_valid_email(self, email: str) -> bool:
        return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email))
```

### Transaction Management

Services should manage transaction boundaries:

```typescript
class OrderService {
  constructor(
    private orderRepository: OrderRepository,
    private inventoryRepository: InventoryRepository,
    private paymentService: PaymentService,
    private transactionManager: TransactionManager
  ) {}

  async createOrder(orderData: CreateOrderRequest): Promise<Order> {
    return await this.transactionManager.runInTransaction(async (tx) => {
      // All operations in this transaction
      const order = await this.orderRepository.create(orderData, tx);

      await this.inventoryRepository.decrementStock(
        orderData.items,
        tx
      );

      await this.paymentService.charge(
        order.id,
        order.total,
        tx
      );

      return order;
    });
  }
}
```

### Benefits

- **Reusability**: Business logic can be used from multiple controllers or consumers
- **Testability**: Can test business logic without HTTP layer
- **Consistency**: Business rules enforced in one place
- **Maintainability**: Clear separation of concerns

### When to Use

- ✅ When you have business logic beyond simple CRUD
- ✅ When operations span multiple repositories
- ✅ When you need transaction management
- ✅ When business rules need validation

## Controller Pattern

### Purpose

Controllers handle HTTP request/response concerns, delegate to services, and transform data between HTTP and domain representations.

### Key Principles

- Thin controllers (minimal logic)
- Handle HTTP-specific concerns only
- Delegate business logic to services
- Map between DTOs and domain models
- Return appropriate HTTP status codes
- Handle HTTP errors

### Structure

```
Controller Layer
├── Parse and validate request
├── Extract data from request
├── Call service layer
├── Map service response to HTTP response
└── Handle HTTP errors
```

### Implementation Example (Express/TypeScript)

```typescript
class UserController {
  constructor(
    private userService: UserService,
    private logger: Logger
  ) {}

  createUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Request validation handled by middleware
      const createUserDto: CreateUserDTO = req.body;

      const user = await this.userService.createUser({
        email: createUserDto.email,
        name: createUserDto.name,
        password: createUserDto.password
      });

      // Map to response DTO (hide sensitive fields)
      const response: UserResponseDTO = {
        id: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt
      };

      res.status(201).json(response);
    } catch (error) {
      next(error); // Pass to error handling middleware
    }
  };

  getUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;

      const user = await this.userService.getUserById(id);

      const response: UserResponseDTO = {
        id: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt
      };

      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  };

  updateUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;
      const updates: UpdateUserDTO = req.body;

      const user = await this.userService.updateUser(id, updates);

      const response: UserResponseDTO = {
        id: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt
      };

      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  };
}
```

### Implementation Example (FastAPI/Python)

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    email: str
    name: str
    password: str

class UserResponseDTO(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

router = APIRouter()

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @router.post("/users", status_code=status.HTTP_201_CREATED)
    async def create_user(self, dto: CreateUserDTO) -> UserResponseDTO:
        try:
            user = self.user_service.create_user(
                email=dto.email,
                name=dto.name,
                password=dto.password
            )

            return UserResponseDTO(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except ConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )

    @router.get("/users/{user_id}")
    async def get_user(self, user_id: str) -> UserResponseDTO:
        try:
            user = self.user_service.get_user_by_id(user_id)

            return UserResponseDTO(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at
            )
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}"
            )
```

### Benefits

- **Framework Independence**: Services aren't coupled to HTTP framework
- **Testability**: Can test services without HTTP server
- **Clear Responsibilities**: Controller handles HTTP, service handles business logic
- **Reusability**: Same service can be used by different controllers (REST, GraphQL, CLI)

## Middleware Pattern

### Purpose

Middleware provides cross-cutting concerns that apply to multiple requests, such as authentication, logging, validation, and error handling.

### Common Middleware Types

**Authentication Middleware**
```typescript
const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      throw new UnauthorizedError('No token provided');
    }

    const user = await jwtService.verify(token);
    req.user = user; // Attach to request

    next();
  } catch (error) {
    next(error);
  }
};
```

**Request Logging Middleware**
```typescript
const loggingMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const requestId = uuid();
  req.requestId = requestId;

  logger.info('Incoming request', {
    requestId,
    method: req.method,
    path: req.path,
    ip: req.ip
  });

  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('Request completed', {
      requestId,
      statusCode: res.statusCode,
      duration
    });
  });

  next();
};
```

**Validation Middleware**
```typescript
const validateSchema = (schema: Schema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.body);

    if (error) {
      throw new ValidationError(error.details[0].message);
    }

    req.body = value; // Use validated/sanitized value
    next();
  };
};
```

## Caching Patterns

### Cache-Aside Pattern

```typescript
class CachedUserRepository implements UserRepository {
  constructor(
    private repository: UserRepository,
    private cache: CacheService
  ) {}

  async findById(id: string): Promise<User | null> {
    const cacheKey = `user:${id}`;

    // Try cache first
    const cached = await this.cache.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Fetch from database
    const user = await this.repository.findById(id);

    // Store in cache
    if (user) {
      await this.cache.set(cacheKey, JSON.stringify(user), { ttl: 3600 });
    }

    return user;
  }

  async update(id: string, updates: Partial<User>): Promise<User> {
    const user = await this.repository.update(id, updates);

    // Invalidate cache
    await this.cache.delete(`user:${id}`);

    return user;
  }
}
```

### Write-Through Cache Pattern

```typescript
async create(userData: CreateUserData): Promise<User> {
  const user = await this.repository.create(userData);

  // Write to cache immediately
  await this.cache.set(
    `user:${user.id}`,
    JSON.stringify(user),
    { ttl: 3600 }
  );

  return user;
}
```

## Async Patterns

### Background Jobs

```typescript
class OrderService {
  constructor(
    private orderRepository: OrderRepository,
    private jobQueue: JobQueue
  ) {}

  async createOrder(orderData: CreateOrderData): Promise<Order> {
    const order = await this.orderRepository.create(orderData);

    // Queue background job for email
    await this.jobQueue.add('send-order-confirmation', {
      orderId: order.id,
      email: orderData.customerEmail
    });

    return order;
  }
}
```

### Event-Driven Pattern

```typescript
class UserService {
  constructor(
    private userRepository: UserRepository,
    private eventBus: EventBus
  ) {}

  async createUser(userData: CreateUserData): Promise<User> {
    const user = await this.userRepository.create(userData);

    // Emit event for other services to react
    await this.eventBus.publish('user.created', {
      userId: user.id,
      email: user.email,
      createdAt: user.createdAt
    });

    return user;
  }
}
```

## Summary

These service patterns provide the foundation for clean, maintainable backend architecture:

- **Repository**: Abstracts data access
- **Service**: Encapsulates business logic
- **Controller**: Handles HTTP concerns
- **Middleware**: Implements cross-cutting concerns
- **Caching**: Improves performance
- **Async Processing**: Handles long-running operations

Use these patterns together to create layered, testable, and maintainable backend systems.
