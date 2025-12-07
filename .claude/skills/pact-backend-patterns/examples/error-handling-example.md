# Error Handling Example

## Scenario: User Registration Service

This example demonstrates comprehensive error handling for a user registration flow.

---

## Domain Errors

```typescript
// domain/errors.ts
export abstract class DomainError extends Error {
  abstract readonly code: string;
  abstract readonly httpStatus: number;

  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }

  toJSON() {
    return {
      code: this.code,
      message: this.message,
    };
  }
}

export class EmailAlreadyExistsError extends DomainError {
  readonly code = 'USER_EMAIL_EXISTS';
  readonly httpStatus = 409;

  constructor(email: string) {
    super(`User with email ${email} already exists`);
  }
}

export class InvalidPasswordError extends DomainError {
  readonly code = 'INVALID_PASSWORD';
  readonly httpStatus = 400;

  constructor(reason: string) {
    super(`Password validation failed: ${reason}`);
  }
}

export class UserNotFoundError extends DomainError {
  readonly code = 'USER_NOT_FOUND';
  readonly httpStatus = 404;

  constructor(identifier: string) {
    super(`User not found: ${identifier}`);
  }
}
```

---

## Result Type Pattern

```typescript
// shared/result.ts
export type Result<T, E = Error> =
  | { success: true; value: T }
  | { success: false; error: E };

export const ok = <T>(value: T): Result<T, never> => ({
  success: true,
  value,
});

export const err = <E>(error: E): Result<never, E> => ({
  success: false,
  error,
});

// Usage in service
export class UserService {
  async register(
    email: string,
    password: string
  ): Promise<Result<User, DomainError>> {
    // Check existing user
    const existing = await this.userRepository.findByEmail(email);
    if (existing) {
      return err(new EmailAlreadyExistsError(email));
    }

    // Validate password
    const passwordValidation = this.validatePassword(password);
    if (!passwordValidation.valid) {
      return err(new InvalidPasswordError(passwordValidation.reason));
    }

    // Create user
    const user = await this.userRepository.create({ email, password });
    return ok(user);
  }
}
```

---

## Controller Error Handling

```typescript
// presentation/controllers/user-controller.ts
import { Request, Response, NextFunction } from 'express';

export class UserController {
  constructor(private userService: UserService) {}

  register = async (
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { email, password } = req.body;

      const result = await this.userService.register(email, password);

      if (!result.success) {
        // Domain error - return appropriate HTTP response
        res.status(result.error.httpStatus).json({
          error: result.error.toJSON(),
        });
        return;
      }

      res.status(201).json({
        data: {
          id: result.value.id,
          email: result.value.email,
        },
      });
    } catch (error) {
      // Unexpected error - pass to error middleware
      next(error);
    }
  };
}
```

---

## Global Error Middleware

```typescript
// middleware/error-handler.ts
import { Request, Response, NextFunction } from 'express';
import { logger } from '../shared/logger';
import { DomainError } from '../domain/errors';

export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Log the error
  logger.error('Unhandled error', {
    error: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    requestId: req.headers['x-request-id'],
  });

  // Domain errors (should be handled in controller, but fallback)
  if (error instanceof DomainError) {
    res.status(error.httpStatus).json({
      error: error.toJSON(),
    });
    return;
  }

  // Validation errors (from express-validator, zod, etc.)
  if (error.name === 'ValidationError') {
    res.status(400).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
        details: (error as any).details,
      },
    });
    return;
  }

  // Database errors
  if (error.name === 'SequelizeConnectionError') {
    res.status(503).json({
      error: {
        code: 'SERVICE_UNAVAILABLE',
        message: 'Database temporarily unavailable',
      },
    });
    return;
  }

  // Default: Internal server error
  // NEVER expose internal error details to client
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
}
```

---

## Async Error Wrapper

```typescript
// middleware/async-handler.ts
import { Request, Response, NextFunction, RequestHandler } from 'express';

export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
): RequestHandler => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Usage
router.post(
  '/users',
  asyncHandler(async (req, res) => {
    // Errors automatically passed to error middleware
    const user = await userService.register(req.body);
    res.status(201).json(user);
  })
);
```

---

## Key Takeaways

1. **Separate domain errors from infrastructure errors**
2. **Use Result types for expected failures**
3. **Use exceptions for unexpected failures**
4. **Never expose stack traces to clients**
5. **Always log errors with context**
6. **Map errors to appropriate HTTP status codes**

---
*Generated from pact-backend-patterns skill example*
