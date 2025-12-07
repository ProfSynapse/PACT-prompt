# Error Handling Reference

## Overview

Comprehensive error handling is critical for backend reliability, security, and maintainability. This reference covers error types, logging strategies, recovery patterns, and best practices.

## Error Categories and HTTP Status Codes

### Client Errors (4xx)

**400 Bad Request**
- Invalid request format
- Malformed JSON
- Missing required fields
- Invalid data types

**401 Unauthorized**
- Missing authentication
- Invalid credentials
- Expired token
- Invalid API key

**403 Forbidden**
- Valid authentication but insufficient permissions
- Resource access denied
- Operation not allowed for user role

**404 Not Found**
- Resource doesn't exist
- Invalid resource ID
- Deleted resource

**409 Conflict**
- Duplicate resource (unique constraint violation)
- Concurrent modification conflict
- Business rule conflict

**422 Unprocessable Entity**
- Valid format but business rule violation
- Invalid state transition
- Failed business validation

**429 Too Many Requests**
- Rate limit exceeded
- Quota exceeded
- Throttling applied

### Server Errors (5xx)

**500 Internal Server Error**
- Unhandled exceptions
- Unexpected errors
- Code bugs

**502 Bad Gateway**
- Upstream service error
- Invalid response from dependency

**503 Service Unavailable**
- Service temporarily down
- Maintenance mode
- Overloaded

**504 Gateway Timeout**
- Upstream service timeout
- Long-running operation timeout

## Error Type Hierarchy

### Custom Error Classes

Define semantic error types that map to HTTP status codes:

```typescript
// Base error class
abstract class ApplicationError extends Error {
  abstract statusCode: number;
  abstract isOperational: boolean;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, new.target.prototype);
    Error.captureStackTrace(this);
  }
}

// Client errors
class ValidationError extends ApplicationError {
  statusCode = 400;
  isOperational = true;

  constructor(message: string, public field?: string) {
    super(message);
  }
}

class UnauthorizedError extends ApplicationError {
  statusCode = 401;
  isOperational = true;

  constructor(message: string = 'Unauthorized') {
    super(message);
  }
}

class ForbiddenError extends ApplicationError {
  statusCode = 403;
  isOperational = true;

  constructor(message: string = 'Forbidden') {
    super(message);
  }
}

class NotFoundError extends ApplicationError {
  statusCode = 404;
  isOperational = true;

  constructor(resource: string, id?: string) {
    const message = id
      ? `${resource} not found: ${id}`
      : `${resource} not found`;
    super(message);
  }
}

class ConflictError extends ApplicationError {
  statusCode = 409;
  isOperational = true;

  constructor(message: string) {
    super(message);
  }
}

// Server errors
class InternalServerError extends ApplicationError {
  statusCode = 500;
  isOperational = false;

  constructor(message: string = 'Internal server error') {
    super(message);
  }
}

class ServiceUnavailableError extends ApplicationError {
  statusCode = 503;
  isOperational = true;

  constructor(message: string = 'Service temporarily unavailable') {
    super(message);
  }
}
```

### Python Error Classes

```python
class ApplicationError(Exception):
    """Base class for application errors"""
    status_code = 500
    is_operational = False

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ValidationError(ApplicationError):
    status_code = 400
    is_operational = True

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field

class UnauthorizedError(ApplicationError):
    status_code = 401
    is_operational = True

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)

class NotFoundError(ApplicationError):
    status_code = 404
    is_operational = True

    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message)

class ConflictError(ApplicationError):
    status_code = 409
    is_operational = True
```

## Error Response Format

### Consistent Error Structure

Return errors in a consistent format across all endpoints:

```typescript
interface ErrorResponse {
  status: 'error';
  statusCode: number;
  message: string;
  errors?: Array<{
    field?: string;
    message: string;
  }>;
  requestId?: string;
  timestamp: string;
}

// Example responses
{
  "status": "error",
  "statusCode": 400,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "Invalid email format" },
    { "field": "password", "message": "Password must be at least 8 characters" }
  ],
  "requestId": "req-123-abc",
  "timestamp": "2025-12-04T10:30:00Z"
}

{
  "status": "error",
  "statusCode": 404,
  "message": "User not found: usr-123",
  "requestId": "req-456-def",
  "timestamp": "2025-12-04T10:30:00Z"
}

{
  "status": "error",
  "statusCode": 500,
  "message": "An unexpected error occurred",
  "requestId": "req-789-ghi",
  "timestamp": "2025-12-04T10:30:00Z"
}
```

### Error Response Middleware

```typescript
const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const requestId = req.requestId || 'unknown';

  // Default to 500 for unknown errors
  let statusCode = 500;
  let message = 'An unexpected error occurred';
  let errors: Array<{ field?: string; message: string }> | undefined;

  if (error instanceof ApplicationError) {
    statusCode = error.statusCode;
    message = error.message;

    // Log operational vs programming errors differently
    if (error.isOperational) {
      logger.warn('Operational error', {
        requestId,
        error: error.message,
        statusCode
      });
    } else {
      logger.error('Programming error', {
        requestId,
        error: error.message,
        stack: error.stack,
        statusCode
      });
    }
  } else {
    // Unexpected error
    logger.error('Unexpected error', {
      requestId,
      error: error.message,
      stack: error.stack
    });
  }

  const response: ErrorResponse = {
    status: 'error',
    statusCode,
    message,
    errors,
    requestId,
    timestamp: new Date().toISOString()
  };

  // Don't leak error details in production
  if (process.env.NODE_ENV === 'production' && statusCode === 500) {
    response.message = 'An unexpected error occurred';
  }

  res.status(statusCode).json(response);
};
```

### FastAPI Error Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    request_id = request.state.request_id

    error_response = {
        "status": "error",
        "statusCode": exc.status_code,
        "message": exc.message,
        "requestId": request_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    if exc.is_operational:
        logger.warning(f"Operational error: {exc.message}", extra={
            "request_id": request_id,
            "status_code": exc.status_code
        })
    else:
        logger.error(f"Programming error: {exc.message}", extra={
            "request_id": request_id,
            "stack": traceback.format_exc()
        })

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    request_id = request.state.request_id

    logger.error(f"Unexpected error: {str(exc)}", extra={
        "request_id": request_id,
        "stack": traceback.format_exc()
    })

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "statusCode": 500,
            "message": "An unexpected error occurred",
            "requestId": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Logging Strategies

### Structured Logging

Use structured logging with contextual information:

```typescript
interface LogContext {
  requestId?: string;
  userId?: string;
  action?: string;
  resource?: string;
  duration?: number;
  [key: string]: any;
}

class Logger {
  info(message: string, context?: LogContext) {
    console.log(JSON.stringify({
      level: 'info',
      message,
      timestamp: new Date().toISOString(),
      ...context
    }));
  }

  warn(message: string, context?: LogContext) {
    console.warn(JSON.stringify({
      level: 'warn',
      message,
      timestamp: new Date().toISOString(),
      ...context
    }));
  }

  error(message: string, context?: LogContext & { error?: Error }) {
    console.error(JSON.stringify({
      level: 'error',
      message,
      timestamp: new Date().toISOString(),
      stack: context?.error?.stack,
      ...context
    }));
  }
}
```

### Request Correlation

Track requests across services with correlation IDs:

```typescript
const correlationMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // Use existing correlation ID or generate new one
  const correlationId = req.headers['x-correlation-id'] as string || uuid();

  req.correlationId = correlationId;
  res.setHeader('x-correlation-id', correlationId);

  next();
};

// Use in logging
logger.info('Processing request', {
  correlationId: req.correlationId,
  method: req.method,
  path: req.path
});
```

### Log Levels

**DEBUG**: Detailed information for diagnosing problems
```typescript
logger.debug('Query executed', {
  query: 'SELECT * FROM users WHERE id = $1',
  params: [userId],
  duration: 23
});
```

**INFO**: General informational messages
```typescript
logger.info('User created', {
  userId: user.id,
  email: user.email
});
```

**WARN**: Warning messages for potentially harmful situations
```typescript
logger.warn('Rate limit approaching', {
  userId: user.id,
  current: 95,
  limit: 100
});
```

**ERROR**: Error events that might still allow the application to continue
```typescript
logger.error('Failed to send email', {
  userId: user.id,
  error: error.message,
  stack: error.stack
});
```

**FATAL**: Severe error events that might cause the application to abort
```typescript
logger.fatal('Database connection lost', {
  error: error.message,
  stack: error.stack
});
```

### What NOT to Log

**Never log sensitive data**:
- Passwords (plain or hashed)
- API keys or tokens
- Credit card numbers
- Social security numbers
- Personal health information
- Session IDs
- Authentication tokens

**Bad example**:
```typescript
logger.info('User login', {
  email: user.email,
  password: password  // NEVER DO THIS
});
```

**Good example**:
```typescript
logger.info('User login successful', {
  userId: user.id,
  email: user.email
});
```

## Error Recovery Strategies

### Retry Pattern

Retry transient failures with exponential backoff:

```typescript
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // Don't retry client errors
      if (error instanceof ApplicationError && error.statusCode < 500) {
        throw error;
      }

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        logger.warn('Operation failed, retrying', {
          attempt: attempt + 1,
          maxRetries,
          delay,
          error: error.message
        });
        await sleep(delay);
      }
    }
  }

  throw lastError!;
}

// Usage
const user = await retryWithBackoff(() =>
  externalAPI.getUser(userId)
);
```

### Circuit Breaker Pattern

Prevent cascading failures by stopping requests to failing services:

```typescript
class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime?: number;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000
  ) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureTime! > this.timeout) {
        this.state = 'half-open';
      } else {
        throw new ServiceUnavailableError('Circuit breaker is open');
      }
    }

    try {
      const result = await operation();

      if (this.state === 'half-open') {
        this.reset();
      }

      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private recordFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.threshold) {
      this.state = 'open';
      logger.error('Circuit breaker opened', {
        failureCount: this.failureCount,
        threshold: this.threshold
      });
    }
  }

  private reset() {
    this.failureCount = 0;
    this.state = 'closed';
    logger.info('Circuit breaker closed');
  }
}

// Usage
const paymentServiceBreaker = new CircuitBreaker(5, 60000);

async function processPayment(orderId: string) {
  return await paymentServiceBreaker.execute(() =>
    paymentService.charge(orderId)
  );
}
```

### Graceful Degradation

Provide reduced functionality when dependencies fail:

```typescript
class UserService {
  async getUserProfile(userId: string): Promise<UserProfile> {
    const user = await this.userRepository.findById(userId);

    if (!user) {
      throw new NotFoundError('User', userId);
    }

    // Try to enrich with additional data
    let preferences;
    try {
      preferences = await this.preferencesService.getPreferences(userId);
    } catch (error) {
      logger.warn('Failed to load preferences, using defaults', {
        userId,
        error: error.message
      });
      preferences = this.getDefaultPreferences();
    }

    return {
      ...user,
      preferences
    };
  }
}
```

### Fallback Pattern

Provide alternative implementations when primary fails:

```typescript
class CacheService {
  async get(key: string): Promise<string | null> {
    try {
      return await this.redisClient.get(key);
    } catch (error) {
      logger.error('Redis unavailable, using in-memory cache', {
        error: error.message
      });
      return this.memoryCache.get(key);
    }
  }
}
```

## Validation Error Handling

### Collecting Multiple Validation Errors

```typescript
class ValidationErrorCollector {
  private errors: Array<{ field: string; message: string }> = [];

  add(field: string, message: string) {
    this.errors.push({ field, message });
  }

  hasErrors(): boolean {
    return this.errors.length > 0;
  }

  throw() {
    if (this.hasErrors()) {
      const error = new ValidationError('Validation failed');
      error.errors = this.errors;
      throw error;
    }
  }
}

// Usage
function validateUserInput(data: CreateUserData) {
  const errors = new ValidationErrorCollector();

  if (!data.email || !isValidEmail(data.email)) {
    errors.add('email', 'Invalid email format');
  }

  if (!data.password || data.password.length < 8) {
    errors.add('password', 'Password must be at least 8 characters');
  }

  if (!data.name || data.name.trim().length === 0) {
    errors.add('name', 'Name is required');
  }

  errors.throw();
}
```

## Database Error Handling

### Handling Unique Constraint Violations

```typescript
async createUser(userData: CreateUserData): Promise<User> {
  try {
    return await this.userRepository.create(userData);
  } catch (error) {
    // PostgreSQL unique violation code
    if (error.code === '23505') {
      throw new ConflictError('User with this email already exists');
    }

    // MySQL duplicate entry error
    if (error.code === 'ER_DUP_ENTRY') {
      throw new ConflictError('User with this email already exists');
    }

    throw error;
  }
}
```

### Handling Foreign Key Violations

```typescript
async deleteUser(userId: string): Promise<void> {
  try {
    await this.userRepository.delete(userId);
  } catch (error) {
    // PostgreSQL foreign key violation
    if (error.code === '23503') {
      throw new ConflictError(
        'Cannot delete user with existing related records'
      );
    }

    throw error;
  }
}
```

## External Service Error Handling

### Timeout Handling

```typescript
async function callExternalAPI<T>(
  url: string,
  timeout: number = 5000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new ServiceUnavailableError('External service timeout');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
```

### HTTP Error Mapping

```typescript
async function fetchUserFromAPI(userId: string): Promise<User> {
  try {
    const response = await httpClient.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          throw new NotFoundError('User', userId);
        case 401:
          throw new UnauthorizedError('Invalid API credentials');
        case 429:
          throw new ServiceUnavailableError('Rate limit exceeded');
        default:
          throw new InternalServerError(
            `External service error: ${error.response.status}`
          );
      }
    }

    throw new ServiceUnavailableError('External service unavailable');
  }
}
```

## Best Practices Summary

### Do's
- ✅ Use semantic error types (ValidationError, NotFoundError, etc.)
- ✅ Return consistent error response format
- ✅ Log errors with context (request ID, user ID, etc.)
- ✅ Distinguish operational vs programming errors
- ✅ Retry transient failures with backoff
- ✅ Use circuit breakers for external dependencies
- ✅ Provide graceful degradation
- ✅ Validate inputs early and thoroughly
- ✅ Map database errors to business errors
- ✅ Use correlation IDs for request tracing

### Don'ts
- ❌ Swallow errors silently
- ❌ Return generic "Error occurred" messages
- ❌ Log sensitive data (passwords, tokens, PII)
- ❌ Expose internal error details to clients
- ❌ Use try/catch as flow control
- ❌ Retry non-transient errors
- ❌ Let unhandled exceptions crash the server
- ❌ Mix error handling concerns across layers
- ❌ Return different error formats from different endpoints
- ❌ Forget to clean up resources in error paths

## Summary

Effective error handling requires:
1. **Semantic error types** that map to HTTP status codes
2. **Consistent error response format** across all endpoints
3. **Structured logging** with correlation IDs and context
4. **Recovery strategies** including retry, circuit breaker, and fallback
5. **Proper validation** at API boundaries
6. **Security awareness** to avoid leaking sensitive information
7. **Operational/programming error distinction** for appropriate handling
