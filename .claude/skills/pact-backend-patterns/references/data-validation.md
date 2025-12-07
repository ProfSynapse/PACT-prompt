# Data Validation Reference

## Overview

Data validation is the first line of defense against invalid input, security vulnerabilities, and data corruption. This reference covers validation strategies, sanitization techniques, and schema design patterns.

## Defense in Depth Strategy

Implement validation at multiple layers:

```
1. Schema Validation (API Boundary)
   ├── Request format validation
   ├── Data type checking
   ├── Required field enforcement
   └── Basic constraint validation

2. Business Validation (Service Layer)
   ├── Business rule enforcement
   ├── State transition validation
   ├── Relationship validation
   └── Cross-field validation

3. Database Constraints (Data Layer)
   ├── Unique constraints
   ├── Foreign key constraints
   ├── Check constraints
   └── Not null constraints
```

## Schema Validation

### JSON Schema

Define request/response schemas with JSON Schema:

```typescript
const createUserSchema = {
  type: 'object',
  required: ['email', 'name', 'password'],
  properties: {
    email: {
      type: 'string',
      format: 'email',
      maxLength: 255
    },
    name: {
      type: 'string',
      minLength: 1,
      maxLength: 100,
      pattern: '^[a-zA-Z\\s]+$'
    },
    password: {
      type: 'string',
      minLength: 8,
      maxLength: 128
    },
    age: {
      type: 'integer',
      minimum: 18,
      maximum: 120
    },
    role: {
      type: 'string',
      enum: ['user', 'admin', 'moderator']
    }
  },
  additionalProperties: false
};

// Validation with Ajv
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv();
addFormats(ajv);

const validate = ajv.compile(createUserSchema);

function validateRequest(data: unknown) {
  if (!validate(data)) {
    throw new ValidationError(
      'Validation failed',
      validate.errors
    );
  }
  return data;
}
```

### Joi Validation

Use Joi for expressive schema validation:

```typescript
import Joi from 'joi';

const createUserSchema = Joi.object({
  email: Joi.string()
    .email()
    .required()
    .max(255),

  name: Joi.string()
    .min(1)
    .max(100)
    .pattern(/^[a-zA-Z\s]+$/)
    .required(),

  password: Joi.string()
    .min(8)
    .max(128)
    .required(),

  age: Joi.number()
    .integer()
    .min(18)
    .max(120)
    .optional(),

  role: Joi.string()
    .valid('user', 'admin', 'moderator')
    .default('user'),

  preferences: Joi.object({
    newsletter: Joi.boolean().default(false),
    notifications: Joi.boolean().default(true)
  }).optional()
});

// Validation middleware
const validateSchema = (schema: Joi.Schema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));

      throw new ValidationError('Validation failed', errors);
    }

    req.body = value; // Use validated/sanitized value
    next();
  };
};

// Usage
router.post('/users', validateSchema(createUserSchema), userController.create);
```

### Zod Validation

Type-safe validation with Zod:

```typescript
import { z } from 'zod';

const createUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
  password: z.string().min(8).max(128),
  age: z.number().int().min(18).max(120).optional(),
  role: z.enum(['user', 'admin', 'moderator']).default('user'),
  preferences: z.object({
    newsletter: z.boolean().default(false),
    notifications: z.boolean().default(true)
  }).optional()
});

// Infer TypeScript type from schema
type CreateUserInput = z.infer<typeof createUserSchema>;

// Validation
function validateCreateUser(data: unknown): CreateUserInput {
  try {
    return createUserSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.map(err => ({
        field: err.path.join('.'),
        message: err.message
      }));
      throw new ValidationError('Validation failed', errors);
    }
    throw error;
  }
}
```

### Pydantic Validation (Python)

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class CreateUserInput(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z\s]+$')
    password: str = Field(..., min_length=8, max_length=128)
    age: Optional[int] = Field(None, ge=18, le=120)
    role: UserRole = UserRole.USER

    @validator('password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

    class Config:
        extra = 'forbid'  # Reject unknown fields

# Usage
try:
    user_input = CreateUserInput(**request_data)
except ValidationError as e:
    errors = [
        {"field": err["loc"][0], "message": err["msg"]}
        for err in e.errors()
    ]
    raise ValidationError("Validation failed", errors)
```

## Business Validation

### Service Layer Validation

Validate business rules in the service layer:

```typescript
class UserService {
  async createUser(input: CreateUserInput): Promise<User> {
    // Business rule: email must be unique
    const existingUser = await this.userRepository.findByEmail(input.email);
    if (existingUser) {
      throw new ConflictError('User with this email already exists');
    }

    // Business rule: admin role requires approval
    if (input.role === 'admin') {
      throw new ValidationError(
        'Admin role requires manual approval',
        'role'
      );
    }

    // Business rule: validate age for certain countries
    if (input.country === 'US' && input.age < 21) {
      throw new ValidationError(
        'Users must be 21 or older in the US',
        'age'
      );
    }

    return await this.userRepository.create(input);
  }

  async updateUser(userId: string, updates: UpdateUserInput): Promise<User> {
    const user = await this.userRepository.findById(userId);

    if (!user) {
      throw new NotFoundError('User', userId);
    }

    // Business rule: can't change email to existing email
    if (updates.email && updates.email !== user.email) {
      const existing = await this.userRepository.findByEmail(updates.email);
      if (existing) {
        throw new ConflictError('Email already in use');
      }
    }

    // Business rule: role changes require authorization
    if (updates.role && updates.role !== user.role) {
      throw new ForbiddenError('Role changes require admin authorization');
    }

    return await this.userRepository.update(userId, updates);
  }
}
```

### State Transition Validation

Validate state machine transitions:

```typescript
enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled'
}

const validTransitions: Record<OrderStatus, OrderStatus[]> = {
  [OrderStatus.PENDING]: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
  [OrderStatus.CONFIRMED]: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
  [OrderStatus.SHIPPED]: [OrderStatus.DELIVERED],
  [OrderStatus.DELIVERED]: [],
  [OrderStatus.CANCELLED]: []
};

class OrderService {
  async updateOrderStatus(
    orderId: string,
    newStatus: OrderStatus
  ): Promise<Order> {
    const order = await this.orderRepository.findById(orderId);

    if (!order) {
      throw new NotFoundError('Order', orderId);
    }

    // Validate state transition
    const allowedTransitions = validTransitions[order.status];
    if (!allowedTransitions.includes(newStatus)) {
      throw new ValidationError(
        `Cannot transition from ${order.status} to ${newStatus}`
      );
    }

    return await this.orderRepository.update(orderId, { status: newStatus });
  }
}
```

### Cross-Field Validation

Validate relationships between fields:

```typescript
interface BookingInput {
  checkInDate: Date;
  checkOutDate: Date;
  guests: number;
  roomType: string;
}

function validateBooking(input: BookingInput) {
  const errors = new ValidationErrorCollector();

  // Check-out must be after check-in
  if (input.checkOutDate <= input.checkInDate) {
    errors.add('checkOutDate', 'Check-out date must be after check-in date');
  }

  // Minimum stay requirement
  const nights = differenceInDays(input.checkOutDate, input.checkInDate);
  if (nights < 1) {
    errors.add('checkOutDate', 'Minimum stay is 1 night');
  }

  // Guest capacity by room type
  const maxGuests: Record<string, number> = {
    single: 1,
    double: 2,
    suite: 4
  };

  if (input.guests > maxGuests[input.roomType]) {
    errors.add(
      'guests',
      `${input.roomType} room can accommodate max ${maxGuests[input.roomType]} guests`
    );
  }

  errors.throw();
}
```

## Input Sanitization

### String Sanitization

Remove or escape dangerous characters:

```typescript
import validator from 'validator';

function sanitizeString(input: string): string {
  // Trim whitespace
  let sanitized = input.trim();

  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');

  // Escape HTML
  sanitized = validator.escape(sanitized);

  return sanitized;
}

function sanitizeEmail(email: string): string {
  return validator.normalizeEmail(email.toLowerCase()) || '';
}

function sanitizeUrl(url: string): string {
  // Ensure valid URL
  if (!validator.isURL(url, { protocols: ['http', 'https'] })) {
    throw new ValidationError('Invalid URL');
  }

  return url;
}
```

### HTML Sanitization

Safely allow some HTML while removing dangerous content:

```typescript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a'],
    ALLOWED_ATTR: ['href'],
    ALLOWED_URI_REGEXP: /^https?:\/\//
  });
}
```

### SQL Injection Prevention

Always use parameterized queries:

```typescript
// ❌ NEVER DO THIS - SQL Injection vulnerability
async function getUserBad(email: string) {
  return await db.query(`SELECT * FROM users WHERE email = '${email}'`);
}

// ✅ CORRECT - Parameterized query
async function getUserGood(email: string) {
  return await db.query('SELECT * FROM users WHERE email = $1', [email]);
}

// ✅ CORRECT - ORM with parameter binding
async function getUserORM(email: string) {
  return await User.findOne({ where: { email } });
}
```

### NoSQL Injection Prevention

Validate input types for NoSQL databases:

```typescript
// ❌ VULNERABLE - NoSQL injection
async function findUserBad(userId: any) {
  return await User.findOne({ _id: userId });
}

// User could send: { $gt: "" } to query all users

// ✅ CORRECT - Type validation
async function findUserGood(userId: string) {
  if (typeof userId !== 'string') {
    throw new ValidationError('Invalid user ID type');
  }

  if (!/^[a-f0-9]{24}$/.test(userId)) {
    throw new ValidationError('Invalid user ID format');
  }

  return await User.findOne({ _id: userId });
}
```

### Path Traversal Prevention

Validate file paths to prevent directory traversal:

```typescript
import path from 'path';

function sanitizeFilePath(userPath: string, baseDir: string): string {
  // Resolve to absolute path
  const absolutePath = path.resolve(baseDir, userPath);

  // Ensure path is within base directory
  if (!absolutePath.startsWith(path.resolve(baseDir))) {
    throw new ValidationError('Invalid file path');
  }

  return absolutePath;
}

// Usage
const safeFilePath = sanitizeFilePath(
  req.query.file as string,
  '/app/uploads'
);
```

## File Upload Validation

### File Type Validation

```typescript
import { fromBuffer } from 'file-type';

async function validateFileUpload(file: Buffer, options: {
  allowedTypes: string[];
  maxSize: number;
}) {
  // Check file size
  if (file.length > options.maxSize) {
    throw new ValidationError(
      `File size exceeds maximum of ${options.maxSize} bytes`
    );
  }

  // Verify actual file type (not just extension)
  const fileType = await fromBuffer(file);

  if (!fileType) {
    throw new ValidationError('Could not determine file type');
  }

  if (!options.allowedTypes.includes(fileType.mime)) {
    throw new ValidationError(
      `File type ${fileType.mime} not allowed. Allowed types: ${options.allowedTypes.join(', ')}`
    );
  }

  return fileType;
}

// Usage
const fileType = await validateFileUpload(fileBuffer, {
  allowedTypes: ['image/jpeg', 'image/png', 'image/gif'],
  maxSize: 5 * 1024 * 1024 // 5MB
});
```

### Image Validation

```typescript
import sharp from 'sharp';

async function validateImage(buffer: Buffer): Promise<{
  width: number;
  height: number;
  format: string;
}> {
  try {
    const metadata = await sharp(buffer).metadata();

    if (!metadata.width || !metadata.height) {
      throw new ValidationError('Invalid image dimensions');
    }

    // Enforce size limits
    if (metadata.width > 4096 || metadata.height > 4096) {
      throw new ValidationError('Image dimensions too large (max 4096x4096)');
    }

    // Enforce minimum dimensions
    if (metadata.width < 100 || metadata.height < 100) {
      throw new ValidationError('Image dimensions too small (min 100x100)');
    }

    return {
      width: metadata.width,
      height: metadata.height,
      format: metadata.format || 'unknown'
    };
  } catch (error) {
    throw new ValidationError('Invalid image file');
  }
}
```

## Database Constraints

### Schema Design with Constraints

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  age INTEGER CHECK (age >= 18 AND age <= 120),
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'admin', 'moderator')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
  total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### Handling Constraint Violations

```typescript
async function handleDatabaseError(error: any): never {
  // PostgreSQL error codes
  switch (error.code) {
    case '23505': // unique_violation
      throw new ConflictError('Resource already exists');

    case '23503': // foreign_key_violation
      throw new ValidationError('Referenced resource does not exist');

    case '23514': // check_violation
      throw new ValidationError('Value violates constraint');

    case '23502': // not_null_violation
      throw new ValidationError('Required field is missing');

    default:
      throw new InternalServerError('Database error occurred');
  }
}
```

## Custom Validators

### Email Domain Validation

```typescript
function isAllowedEmailDomain(email: string, allowedDomains: string[]): boolean {
  const domain = email.split('@')[1]?.toLowerCase();
  return allowedDomains.includes(domain);
}

// Usage
if (!isAllowedEmailDomain(input.email, ['company.com', 'partner.com'])) {
  throw new ValidationError('Email domain not allowed');
}
```

### Credit Card Validation

```typescript
function validateCreditCard(cardNumber: string): boolean {
  // Remove spaces and dashes
  const cleaned = cardNumber.replace(/[\s-]/g, '');

  // Check format
  if (!/^\d{13,19}$/.test(cleaned)) {
    return false;
  }

  // Luhn algorithm
  let sum = 0;
  let isEven = false;

  for (let i = cleaned.length - 1; i >= 0; i--) {
    let digit = parseInt(cleaned[i]);

    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }

    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 === 0;
}
```

### Date Range Validation

```typescript
function validateDateRange(
  startDate: Date,
  endDate: Date,
  options: {
    minDays?: number;
    maxDays?: number;
    allowSameDay?: boolean;
  } = {}
): void {
  if (endDate < startDate) {
    throw new ValidationError('End date must be after start date');
  }

  if (!options.allowSameDay && endDate.getTime() === startDate.getTime()) {
    throw new ValidationError('Start and end dates cannot be the same');
  }

  const days = differenceInDays(endDate, startDate);

  if (options.minDays && days < options.minDays) {
    throw new ValidationError(`Date range must be at least ${options.minDays} days`);
  }

  if (options.maxDays && days > options.maxDays) {
    throw new ValidationError(`Date range cannot exceed ${options.maxDays} days`);
  }
}
```

## Validation Middleware Patterns

### Reusable Validation Middleware

```typescript
interface ValidationRules {
  body?: Joi.Schema;
  query?: Joi.Schema;
  params?: Joi.Schema;
}

function validate(rules: ValidationRules) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (rules.body) {
        req.body = await rules.body.validateAsync(req.body, {
          abortEarly: false,
          stripUnknown: true
        });
      }

      if (rules.query) {
        req.query = await rules.query.validateAsync(req.query, {
          abortEarly: false,
          stripUnknown: true
        });
      }

      if (rules.params) {
        req.params = await rules.params.validateAsync(req.params, {
          abortEarly: false
        });
      }

      next();
    } catch (error) {
      if (error instanceof Joi.ValidationError) {
        const errors = error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message
        }));
        next(new ValidationError('Validation failed', errors));
      } else {
        next(error);
      }
    }
  };
}

// Usage
router.post(
  '/users',
  validate({
    body: createUserSchema,
    query: Joi.object({
      sendEmail: Joi.boolean().default(true)
    })
  }),
  userController.create
);
```

## Best Practices

### Do's
- ✅ Validate at multiple layers (schema, business, database)
- ✅ Use established validation libraries
- ✅ Sanitize all user input
- ✅ Use parameterized queries
- ✅ Validate file types by content, not extension
- ✅ Enforce strong type checking
- ✅ Provide clear, specific error messages
- ✅ Validate early (fail fast)
- ✅ Use allow-lists over deny-lists
- ✅ Validate on both client and server

### Don'ts
- ❌ Trust client-side validation alone
- ❌ Allow arbitrary HTML without sanitization
- ❌ Concatenate user input into SQL queries
- ❌ Accept any file type without validation
- ❌ Use generic validation error messages
- ❌ Skip validation for "trusted" users
- ❌ Allow unlimited input sizes
- ❌ Forget to validate nested objects
- ❌ Use regex for complex validation
- ❌ Log validation failures with sensitive data

## Summary

Effective data validation requires:

1. **Schema Validation**: Type checking and format validation at API boundary
2. **Business Validation**: Enforce business rules in service layer
3. **Database Constraints**: Final safety net for data integrity
4. **Input Sanitization**: Clean and escape user input
5. **Security Focus**: Prevent injection attacks and path traversal
6. **Clear Error Messages**: Help users understand what went wrong
7. **Performance Awareness**: Validate efficiently without blocking

Use validation libraries and follow established patterns to build robust, secure backend systems.
