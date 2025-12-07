# OWASP Top 10 (2021) - Detailed Prevention Strategies

Complete guide to understanding and preventing the OWASP Top 10 web application security risks.

## A01:2021 - Broken Access Control

### Description
Restrictions on authenticated users are not properly enforced, allowing them to:
- Access unauthorized functionality
- Modify or view others' data
- Perform actions beyond their permission level
- Elevate privileges

### Common Vulnerabilities
- Insecure Direct Object References (IDOR)
- Missing function-level access control
- Metadata manipulation (JWT tokens, cookies, hidden fields)
- CORS misconfiguration
- Bypassing access control via URL manipulation
- Elevation of privilege (acting as user without being logged in, or as admin when logged in as user)

### Prevention Strategies

**1. Deny by Default**
```python
# ❌ WRONG: Allow by default
def can_access(user, resource):
    if user.is_admin:
        return True
    if resource.owner_id == user.id:
        return True
    return False  # Only denies if not admin or owner

# ✅ CORRECT: Deny by default
def can_access(user, resource):
    if not user or not user.is_authenticated:
        return False  # Deny unauthenticated
    if resource.owner_id != user.id and not user.is_admin:
        return False  # Deny by default
    return True  # Explicitly allow
```

**2. Verify Ownership on Every Access**
```javascript
// ❌ WRONG: Trust client-provided ID
app.delete('/api/documents/:id', async (req, res) => {
  await Document.findByIdAndDelete(req.params.id);
  res.sendStatus(204);
});

// ✅ CORRECT: Verify ownership
app.delete('/api/documents/:id', auth, async (req, res) => {
  const doc = await Document.findById(req.params.id);

  if (!doc) {
    return res.sendStatus(404);
  }

  // Verify ownership or admin privilege
  if (doc.ownerId !== req.user.id && !req.user.isAdmin) {
    return res.sendStatus(403); // Forbidden
  }

  await doc.delete();
  res.sendStatus(204);
});
```

**3. Rate Limit Sensitive Operations**
```javascript
const rateLimit = require('express-rate-limit');

const sensitiveOpLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too many requests, please try again later.'
    });
  }
});

app.post('/api/password-reset', sensitiveOpLimiter, async (req, res) => {
  // Handle password reset
});
```

**4. Disable Directory Listing and Metadata Exposure**
```nginx
# nginx configuration
location / {
    autoindex off;  # Disable directory listing
}

# Remove server version header
server_tokens off;
```

**5. Log Access Control Failures**
```python
import logging

def check_authorization(user, resource, action):
    if not can_perform_action(user, resource, action):
        logging.warning(
            f"Authorization failure: user={user.id} "
            f"attempted {action} on resource={resource.id} "
            f"type={resource.__class__.__name__}"
        )
        return False
    return True
```

### Testing for Broken Access Control
- [ ] Try accessing resources by manipulating IDs
- [ ] Test horizontal privilege escalation (access other user's data)
- [ ] Test vertical privilege escalation (access admin functions)
- [ ] Test forced browsing to restricted URLs
- [ ] Test API endpoints without authentication
- [ ] Test CORS policy with different origins
- [ ] Verify access controls on all CRUD operations

---

## A02:2021 - Cryptographic Failures

### Description
Failures related to cryptography (or lack thereof) leading to exposure of sensitive data, including:
- Transmitting data in clear text
- Using weak cryptographic algorithms
- Improper key management
- Missing encryption for sensitive data at rest

### Common Vulnerabilities
- Sensitive data transmitted over HTTP
- Weak encryption algorithms (MD5, SHA1, DES)
- Hardcoded encryption keys
- Storing passwords in plaintext or using weak hashing
- Missing database encryption
- Insufficient TLS configuration

### Prevention Strategies

**1. Encrypt All Sensitive Data in Transit**
```nginx
# Enforce HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    # Strong TLS configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

**2. Use Strong Password Hashing**
```python
import bcrypt

# ❌ WRONG: Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# ❌ WRONG: Unsalted hash
password_hash = hashlib.sha256(password.encode()).hexdigest()

# ✅ CORRECT: bcrypt with automatic salt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# Verify password
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

**3. Encrypt Sensitive Data at Rest**
```python
from cryptography.fernet import Fernet
import os

# Generate key (store securely in environment or secrets manager)
# key = Fernet.generate_key()
key = os.environ['ENCRYPTION_KEY'].encode()
cipher = Fernet(key)

# Encrypt
sensitive_data = "SSN: 123-45-6789"
encrypted = cipher.encrypt(sensitive_data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()
```

**4. Proper Key Management**
```python
# ❌ WRONG: Hardcoded key
SECRET_KEY = "hardcoded-secret-key-123"

# ❌ WRONG: Key in version control
# config.json with keys committed to git

# ✅ CORRECT: Environment variables
import os
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set")

# ✅ BETTER: Secrets manager
import boto3
def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

SECRET_KEY = get_secret('app/secret-key')
```

**5. Classify Data and Encrypt Appropriately**
```python
# Data classification
class DataClassification:
    PUBLIC = 0       # No encryption required
    INTERNAL = 1     # Encrypt in transit
    CONFIDENTIAL = 2 # Encrypt in transit and at rest
    RESTRICTED = 3   # Encrypt in transit and at rest, access logging required

class User:
    username = DataClassification.PUBLIC
    email = DataClassification.INTERNAL
    ssn = DataClassification.RESTRICTED
    credit_card = DataClassification.RESTRICTED
```

### Testing for Cryptographic Failures
- [ ] Verify all traffic uses HTTPS
- [ ] Check TLS configuration (SSL Labs test)
- [ ] Verify password hashing algorithm and strength
- [ ] Confirm encryption at rest for sensitive data
- [ ] Check for hardcoded secrets in codebase
- [ ] Verify key rotation procedures
- [ ] Test certificate validation
- [ ] Scan for sensitive data in logs

---

## A03:2021 - Injection

### Description
Untrusted data is sent to an interpreter as part of a command or query, tricking the interpreter into executing unintended commands or accessing unauthorized data.

### Types of Injection
- SQL Injection
- NoSQL Injection
- OS Command Injection
- LDAP Injection
- XPath Injection
- Template Injection
- Email Header Injection

### Prevention Strategies

**1. Use Parameterized Queries (SQL)**
```python
import sqlite3

# ❌ WRONG: String concatenation
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    # Vulnerable to: ' OR '1'='1

# ✅ CORRECT: Parameterized query
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
```

```javascript
// ❌ WRONG: Template string
const query = `SELECT * FROM users WHERE username = '${username}'`;

// ✅ CORRECT: Parameterized with library
const query = 'SELECT * FROM users WHERE username = ?';
db.query(query, [username]);
```

**2. Use ORM with Proper Escaping**
```python
from sqlalchemy import select

# ✅ CORRECT: ORM handles escaping
user = session.query(User).filter(User.username == username).first()

# ❌ WRONG: Raw SQL in ORM
user = session.execute(f"SELECT * FROM users WHERE username = '{username}'").first()
```

**3. Validate and Sanitize Input**
```python
import re

def validate_username(username):
    # Allowlist: only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")
    return username

# Use validation before query
username = validate_username(request.form['username'])
```

**4. Avoid OS Command Execution**
```python
import subprocess

# ❌ WRONG: Shell injection vulnerable
filename = request.args.get('file')
subprocess.run(f'cat {filename}', shell=True)
# Vulnerable to: file.txt; rm -rf /

# ✅ BETTER: Avoid shell
subprocess.run(['cat', filename], shell=False)

# ✅ BEST: Don't call OS commands, use native functions
with open(filename, 'r') as f:
    content = f.read()
```

**5. Sanitize for Context**
```python
import html
import json

# For HTML output
def escape_html(text):
    return html.escape(text)

# For JavaScript output
def escape_javascript(text):
    return json.dumps(text)

# For SQL (use parameterized queries instead)
# For LDAP (use library escaping)
# For shell (avoid shell execution)
```

### Testing for Injection Vulnerabilities
- [ ] SQL Injection: `' OR '1'='1`, `'; DROP TABLE users--`
- [ ] Test all input fields with special characters
- [ ] Test URL parameters, headers, cookies
- [ ] Test file upload names and content
- [ ] Use automated scanners (SQLMap, Burp Suite)
- [ ] Code review for string concatenation in queries
- [ ] Test NoSQL injection with `{"$gt": ""}`
- [ ] Test command injection with `; ls`, `| whoami`

---

## A04:2021 - Insecure Design

### Description
Missing or ineffective security controls due to design flaws, not implementation bugs. Focuses on risks related to design and architectural flaws.

### Common Issues
- Missing threat modeling
- Insufficient separation of concerns
- No defense in depth
- Lack of security requirements
- Business logic flaws
- Missing rate limiting design
- Inadequate access control design

### Prevention Strategies

**1. Threat Modeling Early**
```
STRIDE Framework:
├─ Spoofing: Can attacker impersonate another user?
├─ Tampering: Can attacker modify data in transit or at rest?
├─ Repudiation: Can user deny performing action?
├─ Information Disclosure: Can attacker access sensitive data?
├─ Denial of Service: Can attacker make system unavailable?
└─ Elevation of Privilege: Can attacker gain unauthorized privileges?

For each threat:
1. Identify attack vector
2. Design mitigation
3. Implement defense in depth
4. Test effectiveness
```

**2. Secure Design Patterns**
```python
# Pattern: Circuit Breaker (prevent cascading failures)
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

**3. Business Logic Security**
```python
# Example: Prevent race condition in balance transfer
from django.db import transaction

@transaction.atomic
def transfer_money(from_account, to_account, amount):
    # Lock rows to prevent concurrent modification
    from_acc = Account.objects.select_for_update().get(id=from_account)
    to_acc = Account.objects.select_for_update().get(id=to_account)

    # Validate business rules
    if from_acc.balance < amount:
        raise InsufficientFundsError()

    if amount <= 0:
        raise InvalidAmountError()

    if amount > from_acc.daily_transfer_limit:
        raise TransferLimitExceededError()

    # Perform transfer atomically
    from_acc.balance -= amount
    to_acc.balance += amount

    from_acc.save()
    to_acc.save()

    # Audit log
    log_transfer(from_acc, to_acc, amount)
```

**4. Security Requirements Specification**
```markdown
# Security Requirements Template

## Authentication
- Users MUST authenticate with email and password
- Passwords MUST be at least 12 characters
- Multi-factor authentication MUST be supported
- Sessions MUST expire after 30 minutes of inactivity

## Authorization
- Access control MUST follow principle of least privilege
- Users MUST only access their own resources
- Admin privileges MUST be explicitly granted
- All authorization failures MUST be logged

## Data Protection
- All data in transit MUST use TLS 1.2+
- Sensitive data at rest MUST be encrypted with AES-256
- Encryption keys MUST be stored in secrets manager
- PII MUST be encrypted in database

## Logging and Monitoring
- All authentication events MUST be logged
- All authorization failures MUST be logged
- Logs MUST NOT contain sensitive data
- Security events MUST trigger alerts
```

### Testing for Insecure Design
- [ ] Review threat model for completeness
- [ ] Test business logic edge cases
- [ ] Verify rate limiting on all endpoints
- [ ] Test concurrent operations for race conditions
- [ ] Verify defense in depth (multiple security layers)
- [ ] Test failure modes (fail securely)
- [ ] Review security requirements coverage

---

## A05:2021 - Security Misconfiguration

### Description
Insecure default configurations, incomplete or ad hoc configurations, open cloud storage, misconfigured HTTP headers, and verbose error messages containing sensitive information.

### Common Misconfigurations
- Unnecessary features enabled
- Default accounts/passwords unchanged
- Error messages revealing stack traces
- Missing security headers
- Outdated software
- Insecure SSL/TLS configuration
- Verbose server banners

### Prevention Strategies

**1. Secure HTTP Headers**
```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],  // Avoid unsafe-inline in production
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  noSniff: true,
  frameguard: { action: 'deny' },
  xssFilter: true,
  referrerPolicy: { policy: 'same-origin' }
}));
```

**2. Disable Unnecessary Features**
```python
# Django settings
DEBUG = False  # Never True in production
ALLOWED_HOSTS = ['example.com']

# Disable directory browsing
STATIC_ROOT = '/var/www/static/'
# In web server config, disable autoindex

# Remove server tokens
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

**3. Implement Proper Error Handling**
```javascript
// ❌ WRONG: Expose stack trace
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack  // Never expose in production
  });
});

// ✅ CORRECT: Generic error to client, detailed log server-side
app.use((err, req, res, next) => {
  // Log full error server-side
  logger.error('Server error', {
    error: err.message,
    stack: err.stack,
    user: req.user?.id,
    url: req.url,
    method: req.method
  });

  // Return generic error to client
  res.status(500).json({
    error: 'Internal server error'
  });
});
```

**4. Automated Security Configuration**
```yaml
# Example: Infrastructure as Code (Terraform) with security defaults
resource "aws_s3_bucket" "data" {
  bucket = "my-secure-bucket"

  # Block public access
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  # Enable encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  # Enable versioning
  versioning {
    enabled = true
  }

  # Enable logging
  logging {
    target_bucket = aws_s3_bucket.logs.id
    target_prefix = "s3-access-logs/"
  }
}
```

### Testing for Security Misconfiguration
- [ ] Scan for unnecessary open ports
- [ ] Verify security headers (securityheaders.com)
- [ ] Test with default credentials
- [ ] Check for directory listing
- [ ] Verify error pages don't leak information
- [ ] Test SSL/TLS configuration (SSL Labs)
- [ ] Review cloud storage permissions
- [ ] Check for outdated software versions

---

## A06:2021 - Vulnerable and Outdated Components

### Description
Using components (libraries, frameworks, software) with known vulnerabilities.

### Prevention Strategies

**1. Inventory Dependencies**
```json
// package.json with exact versions
{
  "dependencies": {
    "express": "4.18.2",      // Not "^4.18.2" or "latest"
    "helmet": "7.0.0"
  },
  "devDependencies": {
    "jest": "29.5.0"
  }
}
```

**2. Automated Vulnerability Scanning**
```yaml
# GitHub Actions workflow
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run npm audit
        run: npm audit --audit-level=moderate

      - name: Run Snyk scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

**3. Update Process**
```bash
# Regular dependency updates (weekly/monthly)
npm outdated
npm audit
npm audit fix

# For vulnerabilities without fix:
# 1. Check if you actually use vulnerable code path
# 2. Find alternative package
# 3. Apply workaround/mitigation
# 4. Monitor for patch
```

**4. Software Composition Analysis**
```javascript
// Use Renovate or Dependabot for automated updates
// renovate.json
{
  "extends": ["config:base"],
  "schedule": ["before 3am on Monday"],
  "packageRules": [
    {
      "updateTypes": ["patch", "minor"],
      "automerge": true
    }
  ],
  "vulnerabilityAlerts": {
    "labels": ["security"],
    "assignees": ["@security-team"]
  }
}
```

### Testing for Vulnerable Components
- [ ] Run dependency scanner (npm audit, pip-audit)
- [ ] Check OWASP Dependency-Check
- [ ] Use Snyk or similar SCA tool
- [ ] Review CVE databases for used components
- [ ] Verify all components are still maintained
- [ ] Check for deprecated packages

---

## Quick Reference for Remaining OWASP Top 10

### A07:2021 - Identification and Authentication Failures
**Prevention:**
- Implement MFA
- Use strong password requirements
- Implement account lockout
- Secure session management
- Protect against credential stuffing

**See:** `authentication.md` for detailed patterns

### A08:2021 - Software and Data Integrity Failures
**Prevention:**
- Use digital signatures for software updates
- Verify dependencies from trusted repositories
- Implement CI/CD security controls
- Use integrity checks (checksums, signatures)

### A09:2021 - Security Logging and Monitoring Failures
**Prevention:**
- Log authentication events
- Log authorization failures
- Implement alerting on suspicious patterns
- Maintain audit trails
- Centralize log management
- Never log sensitive data

### A10:2021 - Server-Side Request Forgery (SSRF)
**Prevention:**
- Sanitize and validate all user-supplied URLs
- Use allowlist of permitted destinations
- Disable HTTP redirections
- Implement network segmentation
- Use DNS resolution allowlists

---

## Integration with PACT Phases

### PREPARE Phase
- Review OWASP Top 10 for your tech stack
- Identify applicable vulnerabilities
- Research prevention patterns

### ARCHITECT Phase
- Design security controls for each OWASP item
- Plan defense in depth
- Document security requirements

### CODE Phase
- Implement prevention strategies
- Use secure coding patterns
- Avoid vulnerable patterns

### TEST Phase
- Test for each OWASP Top 10 vulnerability
- Use automated scanners
- Perform manual penetration testing
- Verify security controls effectiveness
