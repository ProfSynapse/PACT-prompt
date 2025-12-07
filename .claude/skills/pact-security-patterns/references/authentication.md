# Authentication and Authorization Patterns

Complete guide to implementing secure authentication and authorization patterns.

## Authentication Decision Tree

```
What type of application?
├─ Web Application (Browser-based)
│   ├─ Traditional server-rendered pages?
│   │   └─ Use: Server-side sessions with secure cookies
│   │       - HttpOnly, Secure, SameSite flags
│   │       - Session store (Redis, database)
│   │       - CSRF protection required
│   │
│   └─ Single Page Application (SPA)?
│       └─ Use: JWT with refresh tokens
│           - Short-lived access token (15-60 min)
│           - Long-lived refresh token (days/weeks)
│           - Store refresh token in HttpOnly cookie
│           - Store access token in memory (not localStorage)
│
├─ Mobile Application
│   └─ Use: OAuth 2.0 with PKCE + JWT
│       - Proof Key for Code Exchange (PKCE)
│       - Secure storage (Keychain/Keystore)
│       - Biometric authentication support
│       - Certificate pinning for API calls
│
├─ Machine-to-Machine (API)
│   ├─ Internal services?
│   │   └─ Use: API keys or mutual TLS (mTLS)
│   │       - Rotate keys regularly
│   │       - Use service accounts
│   │       - Network-level security
│   │
│   └─ External integrations?
│       └─ Use: OAuth 2.0 Client Credentials
│           - Client ID and secret
│           - Token endpoint authentication
│           - Scope-based access control
│
└─ Third-party authentication needed?
    └─ Use: OAuth 2.0 / OpenID Connect
        - Authorization Code flow (most secure)
        - PKCE for public clients
        - State parameter for CSRF protection
        - Nonce for replay attack prevention
```

## Session-Based Authentication

### Implementation Pattern

**1. User Login**
```python
from flask import Flask, session, request
import bcrypt
import secrets

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# Configure session
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Get user from database
    user = User.query.filter_by(username=username).first()

    if not user:
        # Prevent user enumeration - same error message
        return {'error': 'Invalid credentials'}, 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        # Log failed attempt
        log_failed_login(username, request.remote_addr)

        # Check if account should be locked
        if should_lock_account(user.id):
            lock_account(user.id)
            return {'error': 'Account locked due to too many failed attempts'}, 423

        return {'error': 'Invalid credentials'}, 401

    # Regenerate session ID (prevent session fixation)
    session.clear()
    session.regenerate()

    # Set session data
    session['user_id'] = user.id
    session['username'] = user.username
    session['roles'] = [role.name for role in user.roles]
    session['login_time'] = datetime.utcnow().isoformat()

    # Log successful login
    log_successful_login(user.id, request.remote_addr)

    return {'success': True, 'username': user.username}
```

**2. Session Validation Middleware**
```python
from functools import wraps
from flask import session, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Check session timeout
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.utcnow() - login_time > timedelta(minutes=30):
            session.clear()
            return jsonify({'error': 'Session expired'}), 401

        # Optional: Validate session in database (for immediate logout)
        if not is_session_valid(session['user_id'], session.sid):
            session.clear()
            return jsonify({'error': 'Session invalidated'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/api/profile')
@require_auth
def get_profile():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return jsonify(user.to_dict())
```

**3. Session Storage (Redis)**
```python
from flask_session import Session
import redis

# Configure Redis session store
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDIS_URL'])
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'

Session(app)
```

**4. Logout**
```python
@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    user_id = session.get('user_id')

    # Invalidate session in database (if tracking)
    invalidate_session(user_id, session.sid)

    # Clear session
    session.clear()

    # Log logout
    log_logout(user_id)

    return {'success': True}
```

### CSRF Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# For AJAX requests, include CSRF token in header
@app.route('/api/csrf-token')
def get_csrf_token():
    token = generate_csrf()
    return {'csrf_token': token}

# Client-side (JavaScript)
"""
// Get CSRF token
const response = await fetch('/api/csrf-token');
const { csrf_token } = await response.json();

// Include in POST requests
fetch('/api/data', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrf_token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
"""
```

---

## JWT-Based Authentication

### Implementation Pattern

**1. Token Generation**
```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// Environment variables
const ACCESS_TOKEN_SECRET = process.env.ACCESS_TOKEN_SECRET;
const REFRESH_TOKEN_SECRET = process.env.REFRESH_TOKEN_SECRET;
const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';

function generateAccessToken(user) {
  return jwt.sign(
    {
      userId: user.id,
      username: user.username,
      roles: user.roles,
      type: 'access'
    },
    ACCESS_TOKEN_SECRET,
    { expiresIn: ACCESS_TOKEN_EXPIRY }
  );
}

function generateRefreshToken(user) {
  const token = jwt.sign(
    {
      userId: user.id,
      type: 'refresh',
      // Include token ID for revocation
      jti: crypto.randomBytes(16).toString('hex')
    },
    REFRESH_TOKEN_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY }
  );

  // Store refresh token in database for revocation capability
  storeRefreshToken(user.id, token);

  return token;
}

async function login(req, res) {
  const { username, password } = req.body;

  // Validate credentials
  const user = await User.findOne({ username });
  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Generate tokens
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  // Set refresh token as HttpOnly cookie
  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: true,  // HTTPS only
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
  });

  // Return access token
  res.json({
    accessToken,
    expiresIn: 900,  // 15 minutes in seconds
    user: {
      id: user.id,
      username: user.username,
      roles: user.roles
    }
  });
}
```

**2. Token Validation Middleware**
```javascript
async function authenticateToken(req, res, next) {
  // Get token from Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];  // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, ACCESS_TOKEN_SECRET);

    // Check token type
    if (decoded.type !== 'access') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    // Attach user info to request
    req.user = {
      id: decoded.userId,
      username: decoded.username,
      roles: decoded.roles
    };

    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Invalid token' });
    }
    return res.status(500).json({ error: 'Token verification failed' });
  }
}

// Protected route
app.get('/api/profile', authenticateToken, async (req, res) => {
  const user = await User.findById(req.user.id);
  res.json(user);
});
```

**3. Token Refresh**
```javascript
async function refreshAccessToken(req, res) {
  const refreshToken = req.cookies.refreshToken;

  if (!refreshToken) {
    return res.status(401).json({ error: 'Refresh token required' });
  }

  try {
    // Verify refresh token
    const decoded = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET);

    // Check token type
    if (decoded.type !== 'refresh') {
      return res.status(401).json({ error: 'Invalid token type' });
    }

    // Verify token hasn't been revoked
    const isValid = await isRefreshTokenValid(decoded.userId, decoded.jti);
    if (!isValid) {
      return res.status(401).json({ error: 'Refresh token revoked' });
    }

    // Get user
    const user = await User.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    // Generate new access token
    const accessToken = generateAccessToken(user);

    res.json({
      accessToken,
      expiresIn: 900
    });

  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      // Refresh token expired, require re-login
      return res.status(401).json({ error: 'Refresh token expired, please login again' });
    }
    return res.status(401).json({ error: 'Invalid refresh token' });
  }
}
```

**4. Token Revocation**
```javascript
async function logout(req, res) {
  const refreshToken = req.cookies.refreshToken;

  if (refreshToken) {
    try {
      const decoded = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET);
      // Revoke refresh token
      await revokeRefreshToken(decoded.userId, decoded.jti);
    } catch (error) {
      // Token already invalid, continue with logout
    }
  }

  // Clear refresh token cookie
  res.clearCookie('refreshToken');
  res.json({ success: true });
}

// Revoke all user's refresh tokens (e.g., after password change)
async function revokeAllUserTokens(userId) {
  await RefreshToken.deleteMany({ userId });
}
```

**5. Client-Side Token Storage**
```javascript
// ❌ WRONG: Store in localStorage (vulnerable to XSS)
localStorage.setItem('accessToken', token);

// ✅ CORRECT: Store in memory
class AuthService {
  constructor() {
    this.accessToken = null;
    this.refreshInterval = null;
  }

  async login(username, password) {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: 'include'  // Include cookies
    });

    const data = await response.json();

    if (response.ok) {
      // Store access token in memory
      this.accessToken = data.accessToken;

      // Set up auto-refresh
      this.scheduleTokenRefresh(data.expiresIn);
    }

    return data;
  }

  scheduleTokenRefresh(expiresIn) {
    // Refresh token 1 minute before expiry
    const refreshTime = (expiresIn - 60) * 1000;

    this.refreshInterval = setTimeout(async () => {
      await this.refreshToken();
    }, refreshTime);
  }

  async refreshToken() {
    const response = await fetch('/api/refresh', {
      method: 'POST',
      credentials: 'include'
    });

    const data = await response.json();

    if (response.ok) {
      this.accessToken = data.accessToken;
      this.scheduleTokenRefresh(data.expiresIn);
    } else {
      // Refresh failed, redirect to login
      this.logout();
    }
  }

  async request(url, options = {}) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.accessToken}`
    };

    const response = await fetch(url, options);

    if (response.status === 401) {
      // Token expired, try refresh
      await this.refreshToken();
      // Retry original request
      return fetch(url, options);
    }

    return response;
  }

  logout() {
    this.accessToken = null;
    if (this.refreshInterval) {
      clearTimeout(this.refreshInterval);
    }
    fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    });
    window.location.href = '/login';
  }
}
```

---

## OAuth 2.0 / OpenID Connect

### Authorization Code Flow (Most Secure)

**1. Authorization Request**
```javascript
const crypto = require('crypto');

// Generate PKCE code verifier and challenge
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto
    .createHash('sha256')
    .update(verifier)
    .digest('base64url');

  return { verifier, challenge };
}

// Initiate OAuth flow
app.get('/auth/login', (req, res) => {
  const { verifier, challenge } = generatePKCE();

  // Store verifier in session
  req.session.codeVerifier = verifier;

  // Generate state for CSRF protection
  const state = crypto.randomBytes(16).toString('hex');
  req.session.oauthState = state;

  // Build authorization URL
  const authUrl = new URL('https://provider.com/oauth/authorize');
  authUrl.searchParams.set('client_id', process.env.OAUTH_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', process.env.OAUTH_REDIRECT_URI);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', 'openid profile email');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('code_challenge', challenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');

  res.redirect(authUrl.toString());
});
```

**2. Handle Callback**
```javascript
app.get('/auth/callback', async (req, res) => {
  const { code, state } = req.query;

  // Verify state (CSRF protection)
  if (state !== req.session.oauthState) {
    return res.status(400).send('Invalid state parameter');
  }

  // Exchange code for token
  const tokenResponse = await fetch('https://provider.com/oauth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: process.env.OAUTH_REDIRECT_URI,
      client_id: process.env.OAUTH_CLIENT_ID,
      client_secret: process.env.OAUTH_CLIENT_SECRET,
      code_verifier: req.session.codeVerifier
    })
  });

  const tokens = await tokenResponse.json();

  // Verify ID token (OpenID Connect)
  const idToken = jwt.decode(tokens.id_token, { complete: true });

  // Create or update user
  const user = await findOrCreateUser({
    providerId: idToken.payload.sub,
    email: idToken.payload.email,
    name: idToken.payload.name
  });

  // Create session
  req.session.userId = user.id;

  // Clean up OAuth session data
  delete req.session.codeVerifier;
  delete req.session.oauthState;

  res.redirect('/dashboard');
});
```

---

## Authorization Patterns

### Role-Based Access Control (RBAC)

```javascript
// Define roles and permissions
const ROLES = {
  ADMIN: {
    name: 'admin',
    permissions: ['user:read', 'user:write', 'user:delete', 'post:read', 'post:write', 'post:delete']
  },
  EDITOR: {
    name: 'editor',
    permissions: ['user:read', 'post:read', 'post:write']
  },
  USER: {
    name: 'user',
    permissions: ['user:read', 'post:read']
  }
};

// Check permission
function hasPermission(user, permission) {
  const role = ROLES[user.role.toUpperCase()];
  return role && role.permissions.includes(permission);
}

// Authorization middleware
function requirePermission(permission) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!hasPermission(req.user, permission)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// Usage
app.delete('/api/posts/:id',
  authenticateToken,
  requirePermission('post:delete'),
  async (req, res) => {
    const post = await Post.findById(req.params.id);

    // Also check ownership
    if (post.authorId !== req.user.id && req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Not authorized to delete this post' });
    }

    await post.delete();
    res.sendStatus(204);
  }
);
```

### Attribute-Based Access Control (ABAC)

```javascript
// Policy-based authorization
class AuthorizationPolicy {
  constructor() {
    this.policies = [];
  }

  addPolicy(name, evaluator) {
    this.policies.push({ name, evaluator });
  }

  async evaluate(context) {
    for (const policy of this.policies) {
      const result = await policy.evaluator(context);
      if (!result.allowed) {
        return {
          allowed: false,
          reason: `Policy '${policy.name}' denied access: ${result.reason}`
        };
      }
    }
    return { allowed: true };
  }
}

// Define policies
const policies = new AuthorizationPolicy();

policies.addPolicy('document-access', async (context) => {
  const { user, resource, action } = context;

  // Owner can do anything
  if (resource.ownerId === user.id) {
    return { allowed: true };
  }

  // Check sharing permissions
  const sharing = await DocumentSharing.findOne({
    documentId: resource.id,
    userId: user.id
  });

  if (!sharing) {
    return { allowed: false, reason: 'Document not shared with user' };
  }

  // Check if action is permitted
  if (action === 'write' && sharing.permission !== 'write') {
    return { allowed: false, reason: 'User has read-only access' };
  }

  return { allowed: true };
});

// Usage in route
app.put('/api/documents/:id', authenticateToken, async (req, res) => {
  const document = await Document.findById(req.params.id);

  const result = await policies.evaluate({
    user: req.user,
    resource: document,
    action: 'write'
  });

  if (!result.allowed) {
    return res.status(403).json({ error: result.reason });
  }

  // Proceed with update
  await document.update(req.body);
  res.json(document);
});
```

---

## Multi-Factor Authentication (MFA)

### TOTP (Time-based One-Time Password)

```javascript
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

// Generate secret for user
async function generateMFASecret(user) {
  const secret = speakeasy.generateSecret({
    name: `MyApp (${user.email})`,
    issuer: 'MyApp'
  });

  // Store secret in database (encrypted)
  await User.updateOne(
    { id: user.id },
    { mfaSecret: encryptSecret(secret.base32) }
  );

  // Generate QR code for user to scan
  const qrCode = await QRCode.toDataURL(secret.otpauth_url);

  return {
    secret: secret.base32,
    qrCode
  };
}

// Verify TOTP token
function verifyTOTP(user, token) {
  const secret = decryptSecret(user.mfaSecret);

  return speakeasy.totp.verify({
    secret,
    encoding: 'base32',
    token,
    window: 2  // Allow 2 time steps before/after
  });
}

// Login with MFA
async function loginWithMFA(username, password, totpToken) {
  // First verify username and password
  const user = await User.findOne({ username });

  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    return { success: false, error: 'Invalid credentials' };
  }

  // If MFA is enabled, verify TOTP token
  if (user.mfaEnabled) {
    if (!totpToken) {
      return {
        success: false,
        requiresMFA: true,
        error: 'MFA token required'
      };
    }

    if (!verifyTOTP(user, totpToken)) {
      return {
        success: false,
        requiresMFA: true,
        error: 'Invalid MFA token'
      };
    }
  }

  // Generate tokens
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  return {
    success: true,
    accessToken,
    refreshToken
  };
}
```

---

## Security Best Practices Summary

### Password Security
- [ ] Use bcrypt, Argon2, or scrypt for hashing
- [ ] Minimum 12-character passwords
- [ ] Check against breach databases
- [ ] Implement account lockout after failed attempts
- [ ] Require current password for password changes

### Session Security
- [ ] Use HttpOnly, Secure, SameSite cookie flags
- [ ] Implement session timeout (idle and absolute)
- [ ] Regenerate session ID after login
- [ ] Implement CSRF protection
- [ ] Provide logout functionality

### JWT Security
- [ ] Use short-lived access tokens (15-60 min)
- [ ] Store refresh tokens securely
- [ ] Sign tokens with strong secrets
- [ ] Include token revocation capability
- [ ] Never store sensitive data in JWT payload

### OAuth Security
- [ ] Use Authorization Code flow (not Implicit)
- [ ] Implement PKCE for public clients
- [ ] Validate state parameter
- [ ] Use HTTPS for redirect URIs
- [ ] Validate redirect URIs server-side

### General
- [ ] Log all authentication events
- [ ] Implement rate limiting on auth endpoints
- [ ] Use MFA for sensitive accounts
- [ ] Regularly rotate secrets and keys
- [ ] Monitor for suspicious activity
