# Authentication Implementation Example: JWT-Based API Authentication with Refresh Tokens

## Context

**Application**: RESTful API for a mobile and web application
**Requirements**:
- Stateless authentication (JWT tokens)
- Secure password storage
- Token refresh mechanism (access + refresh tokens)
- Account lockout after failed login attempts
- Password reset flow
- Multi-device session support

**Stack**: Node.js + Express + PostgreSQL

---

## Implementation

### Step 1: Password Storage with bcrypt

```javascript
// services/password-service.js
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12; // Computational cost factor (higher = more secure but slower)

export class PasswordService {
  /**
   * Hash a plain-text password using bcrypt
   * @param {string} password - Plain-text password
   * @returns {Promise<string>} Hashed password
   */
  async hashPassword(password) {
    // bcrypt automatically generates a unique salt per password
    return await bcrypt.hash(password, SALT_ROUNDS);
  }

  /**
   * Verify a password against its hash
   * @param {string} password - Plain-text password
   * @param {string} hash - Stored hash
   * @returns {Promise<boolean>} True if password matches
   */
  async verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
  }

  /**
   * Validate password strength
   * @param {string} password - Password to validate
   * @returns {object} { valid: boolean, errors: string[] }
   */
  validatePasswordStrength(password) {
    const errors = [];

    if (password.length < 12) {
      errors.push('Password must be at least 12 characters');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain lowercase letters');
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain uppercase letters');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain numbers');
    }

    if (!/[^a-zA-Z0-9]/.test(password)) {
      errors.push('Password must contain special characters');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
```

**Key Security Decisions**:
- **bcrypt with 12 rounds**: Balances security and performance (takes ~200ms)
- **Minimum 12 characters**: Increases entropy, discourages weak passwords
- **Complexity requirements**: Enforces character diversity
- **Automatic salting**: bcrypt handles salt generation and storage

---

### Step 2: JWT Token Generation

```javascript
// services/token-service.js
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { db } from '../database';

const ACCESS_TOKEN_SECRET = process.env.ACCESS_TOKEN_SECRET; // 256-bit secret
const REFRESH_TOKEN_SECRET = process.env.REFRESH_TOKEN_SECRET; // Different secret
const ACCESS_TOKEN_EXPIRY = '15m'; // Short-lived
const REFRESH_TOKEN_EXPIRY = '7d'; // Long-lived

export class TokenService {
  /**
   * Generate access token (short-lived)
   */
  generateAccessToken(userId, email, role) {
    return jwt.sign(
      {
        userId,
        email,
        role,
        type: 'access',
      },
      ACCESS_TOKEN_SECRET,
      {
        expiresIn: ACCESS_TOKEN_EXPIRY,
        issuer: 'myapp.com',
        audience: 'myapp-api',
      }
    );
  }

  /**
   * Generate refresh token (long-lived, stored in database)
   */
  async generateRefreshToken(userId, deviceInfo) {
    const tokenId = crypto.randomBytes(32).toString('hex');

    const refreshToken = jwt.sign(
      {
        userId,
        tokenId,
        type: 'refresh',
      },
      REFRESH_TOKEN_SECRET,
      {
        expiresIn: REFRESH_TOKEN_EXPIRY,
        issuer: 'myapp.com',
      }
    );

    // Store refresh token in database for revocation capability
    await db.refreshTokens.create({
      id: tokenId,
      user_id: userId,
      token_hash: crypto.createHash('sha256').update(refreshToken).digest('hex'),
      device_info: deviceInfo,
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
      created_at: new Date(),
    });

    return refreshToken;
  }

  /**
   * Verify access token
   */
  verifyAccessToken(token) {
    try {
      const decoded = jwt.verify(token, ACCESS_TOKEN_SECRET, {
        issuer: 'myapp.com',
        audience: 'myapp-api',
      });

      if (decoded.type !== 'access') {
        throw new Error('Invalid token type');
      }

      return decoded;
    } catch (error) {
      throw new Error('Invalid or expired access token');
    }
  }

  /**
   * Verify refresh token and check database
   */
  async verifyRefreshToken(token) {
    try {
      const decoded = jwt.verify(token, REFRESH_TOKEN_SECRET, {
        issuer: 'myapp.com',
      });

      if (decoded.type !== 'refresh') {
        throw new Error('Invalid token type');
      }

      // Check if token exists in database and hasn't been revoked
      const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
      const storedToken = await db.refreshTokens.findOne({
        where: {
          id: decoded.tokenId,
          user_id: decoded.userId,
          token_hash: tokenHash,
          revoked: false,
          expires_at: { [db.Op.gt]: new Date() },
        },
      });

      if (!storedToken) {
        throw new Error('Refresh token revoked or expired');
      }

      return decoded;
    } catch (error) {
      throw new Error('Invalid or expired refresh token');
    }
  }

  /**
   * Revoke refresh token (logout)
   */
  async revokeRefreshToken(tokenId) {
    await db.refreshTokens.update(
      { revoked: true, revoked_at: new Date() },
      { where: { id: tokenId } }
    );
  }

  /**
   * Revoke all refresh tokens for a user (logout all devices)
   */
  async revokeAllUserTokens(userId) {
    await db.refreshTokens.update(
      { revoked: true, revoked_at: new Date() },
      { where: { user_id: userId, revoked: false } }
    );
  }
}
```

**Key Security Decisions**:
- **Separate secrets for access and refresh tokens**: Limits damage if one is compromised
- **Short-lived access tokens (15 min)**: Reduces window of vulnerability
- **Long-lived refresh tokens (7 days)**: Balance between security and UX
- **Refresh tokens stored in database**: Enables revocation and device management
- **Token hashing in DB**: Even if database is breached, tokens aren't directly exposed
- **Token type validation**: Prevents using refresh token as access token

---

### Step 3: Registration Endpoint

```javascript
// controllers/auth-controller.js
import { PasswordService } from '../services/password-service';
import { TokenService } from '../services/token-service';
import { db } from '../database';
import { RateLimitError } from '../errors';

const passwordService = new PasswordService();
const tokenService = new TokenService();

export class AuthController {
  /**
   * POST /api/auth/register
   */
  async register(req, res, next) {
    try {
      const { email, password, name } = req.body;

      // Validate input
      if (!email || !password || !name) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email, password, and name are required',
          },
        });
      }

      // Validate password strength
      const passwordValidation = passwordService.validatePasswordStrength(password);
      if (!passwordValidation.valid) {
        return res.status(400).json({
          error: {
            code: 'WEAK_PASSWORD',
            message: 'Password does not meet requirements',
            details: passwordValidation.errors,
          },
        });
      }

      // Check if user already exists
      const existingUser = await db.users.findOne({ where: { email } });
      if (existingUser) {
        return res.status(409).json({
          error: {
            code: 'EMAIL_EXISTS',
            message: 'User with this email already exists',
          },
        });
      }

      // Hash password
      const passwordHash = await passwordService.hashPassword(password);

      // Create user
      const user = await db.users.create({
        email,
        password_hash: passwordHash,
        name,
        role: 'user',
        created_at: new Date(),
      });

      // Generate tokens
      const accessToken = tokenService.generateAccessToken(
        user.id,
        user.email,
        user.role
      );
      const refreshToken = await tokenService.generateRefreshToken(
        user.id,
        req.headers['user-agent']
      );

      res.status(201).json({
        data: {
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
          tokens: {
            accessToken,
            refreshToken,
          },
        },
      });
    } catch (error) {
      next(error);
    }
  }
}
```

---

### Step 4: Login Endpoint with Rate Limiting

```javascript
  /**
   * POST /api/auth/login
   * Rate limited: 5 attempts per 15 minutes per IP
   */
  async login(req, res, next) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email and password are required',
          },
        });
      }

      // Find user
      const user = await db.users.findOne({ where: { email } });
      if (!user) {
        // Don't reveal whether email exists
        return res.status(401).json({
          error: {
            code: 'INVALID_CREDENTIALS',
            message: 'Invalid email or password',
          },
        });
      }

      // Check if account is locked
      if (user.locked_until && user.locked_until > new Date()) {
        const remainingMinutes = Math.ceil(
          (user.locked_until - new Date()) / 60000
        );
        return res.status(423).json({
          error: {
            code: 'ACCOUNT_LOCKED',
            message: `Account locked due to too many failed login attempts. Try again in ${remainingMinutes} minutes.`,
          },
        });
      }

      // Verify password
      const isValidPassword = await passwordService.verifyPassword(
        password,
        user.password_hash
      );

      if (!isValidPassword) {
        // Increment failed login attempts
        await this.handleFailedLogin(user);

        return res.status(401).json({
          error: {
            code: 'INVALID_CREDENTIALS',
            message: 'Invalid email or password',
          },
        });
      }

      // Reset failed login attempts on successful login
      await db.users.update(
        {
          failed_login_attempts: 0,
          locked_until: null,
          last_login_at: new Date(),
        },
        { where: { id: user.id } }
      );

      // Generate tokens
      const accessToken = tokenService.generateAccessToken(
        user.id,
        user.email,
        user.role
      );
      const refreshToken = await tokenService.generateRefreshToken(
        user.id,
        req.headers['user-agent']
      );

      res.status(200).json({
        data: {
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
          tokens: {
            accessToken,
            refreshToken,
          },
        },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Handle failed login attempts with progressive delays
   */
  async handleFailedLogin(user) {
    const attempts = (user.failed_login_attempts || 0) + 1;

    // Lock account after 5 failed attempts
    if (attempts >= 5) {
      await db.users.update(
        {
          failed_login_attempts: attempts,
          locked_until: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes
        },
        { where: { id: user.id } }
      );
    } else {
      await db.users.update(
        { failed_login_attempts: attempts },
        { where: { id: user.id } }
      );
    }
  }
```

---

### Step 5: Token Refresh Endpoint

```javascript
  /**
   * POST /api/auth/refresh
   */
  async refresh(req, res, next) {
    try {
      const { refreshToken } = req.body;

      if (!refreshToken) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Refresh token is required',
          },
        });
      }

      // Verify refresh token
      const decoded = await tokenService.verifyRefreshToken(refreshToken);

      // Get user details
      const user = await db.users.findByPk(decoded.userId);
      if (!user) {
        return res.status(401).json({
          error: {
            code: 'INVALID_TOKEN',
            message: 'User not found',
          },
        });
      }

      // Generate new access token
      const accessToken = tokenService.generateAccessToken(
        user.id,
        user.email,
        user.role
      );

      res.status(200).json({
        data: {
          accessToken,
        },
      });
    } catch (error) {
      return res.status(401).json({
        error: {
          code: 'INVALID_TOKEN',
          message: error.message,
        },
      });
    }
  }
```

---

### Step 6: Logout Endpoint

```javascript
  /**
   * POST /api/auth/logout
   */
  async logout(req, res, next) {
    try {
      const { refreshToken } = req.body;

      if (!refreshToken) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Refresh token is required',
          },
        });
      }

      // Verify and revoke refresh token
      const decoded = await tokenService.verifyRefreshToken(refreshToken);
      await tokenService.revokeRefreshToken(decoded.tokenId);

      res.status(200).json({
        data: {
          message: 'Logged out successfully',
        },
      });
    } catch (error) {
      // Even if token is invalid, respond with success (idempotent)
      res.status(200).json({
        data: {
          message: 'Logged out successfully',
        },
      });
    }
  }

  /**
   * POST /api/auth/logout-all
   * Logout from all devices
   */
  async logoutAll(req, res, next) {
    try {
      // Get user from authenticated request
      const userId = req.user.userId; // Set by auth middleware

      await tokenService.revokeAllUserTokens(userId);

      res.status(200).json({
        data: {
          message: 'Logged out from all devices',
        },
      });
    } catch (error) {
      next(error);
    }
  }
```

---

### Step 7: Authentication Middleware

```javascript
// middleware/auth-middleware.js
import { TokenService } from '../services/token-service';

const tokenService = new TokenService();

export const authenticateToken = async (req, res, next) => {
  // Extract token from Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({
      error: {
        code: 'NO_TOKEN',
        message: 'Access token is required',
      },
    });
  }

  try {
    // Verify token
    const decoded = tokenService.verifyAccessToken(token);

    // Attach user info to request
    req.user = {
      userId: decoded.userId,
      email: decoded.email,
      role: decoded.role,
    };

    next();
  } catch (error) {
    return res.status(401).json({
      error: {
        code: 'INVALID_TOKEN',
        message: 'Invalid or expired access token',
      },
    });
  }
};

/**
 * Authorization middleware - check user role
 */
export const requireRole = (allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required',
        },
      });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions',
        },
      });
    }

    next();
  };
};
```

---

### Step 8: Protected Route Usage

```javascript
// routes/products.js
import { Router } from 'express';
import { authenticateToken, requireRole } from '../middleware/auth-middleware';
import { ProductController } from '../controllers/product-controller';

const router = Router();
const productController = new ProductController();

// Public route - no authentication
router.get('/api/products', productController.list);

// Protected route - authentication required
router.get(
  '/api/products/:id',
  authenticateToken,
  productController.get
);

// Admin-only route - authentication + role check
router.post(
  '/api/products',
  authenticateToken,
  requireRole(['admin']),
  productController.create
);

router.patch(
  '/api/products/:id',
  authenticateToken,
  requireRole(['admin', 'manager']),
  productController.update
);

export default router;
```

---

## Database Schema

```sql
-- Users table
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'user',
  failed_login_attempts INT DEFAULT 0,
  locked_until TIMESTAMP,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
  id VARCHAR(64) PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(64) NOT NULL,
  device_info TEXT,
  revoked BOOLEAN DEFAULT FALSE,
  revoked_at TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

---

## Key Decisions

### 1. Access vs Refresh Tokens
**Decision**: Use dual-token approach with short-lived access tokens and long-lived refresh tokens
**Rationale**: Balances security (short access token window) with UX (don't require frequent login)
**Implementation**: Access token expires in 15 min, refresh token in 7 days

### 2. Refresh Token Storage
**Decision**: Store refresh tokens in database with hashed values
**Rationale**: Enables revocation (logout, logout all devices) and provides audit trail
**Trade-off**: Database lookup on token refresh (mitigated by short access token TTL means infrequent refresh)

### 3. Password Requirements
**Decision**: Minimum 12 characters with complexity requirements
**Rationale**: NIST guidelines recommend length over complexity, but complexity adds entropy
**Trade-off**: User friction vs security (justified for sensitive applications)

### 4. Account Lockout
**Decision**: Lock account for 15 minutes after 5 failed login attempts
**Rationale**: Prevents brute force attacks while allowing legitimate users to retry
**Risk Mitigation**: Consider CAPTCHA after 3 attempts for better UX

### 5. Token Secrets Management
**Decision**: Store secrets in environment variables, separate secrets for access and refresh tokens
**Rationale**: Limits damage if one secret is compromised
**Production**: Use secret management service (AWS Secrets Manager, HashiCorp Vault)

---

## Common Pitfalls Avoided

1. **Storing passwords in plaintext**: Used bcrypt with appropriate cost factor
2. **Using same secret for all tokens**: Separate secrets for access and refresh tokens
3. **Long-lived access tokens**: 15-minute expiry limits exposure window
4. **No token revocation**: Database storage enables logout functionality
5. **Revealing account existence**: Same error message for invalid email and password
6. **No rate limiting**: Account lockout after failed attempts prevents brute force
7. **Token type confusion**: Validate token type to prevent refresh token misuse

---

## Security Testing Checklist

- [ ] Passwords hashed with bcrypt (verify salt rounds ≥ 12)
- [ ] Access tokens expire within 15 minutes
- [ ] Refresh tokens revoked on logout
- [ ] Account locked after 5 failed login attempts
- [ ] Same error message for invalid email and password
- [ ] Authorization checks on all protected routes
- [ ] Token secrets stored securely (not in code)
- [ ] HTTPS enforced for all authentication endpoints
- [ ] Password validation prevents weak passwords
- [ ] Failed login attempts reset on successful login

---

*Example from pact-security-patterns skill - JWT authentication implementation with security best practices*
