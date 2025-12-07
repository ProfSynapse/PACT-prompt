# Input Validation and Sanitization Patterns

Complete guide to secure input handling and context-aware output encoding.

## Input Validation Philosophy

```
Defense in Depth for Input:

1. CLIENT-SIDE VALIDATION (User Experience)
   └─ Immediate feedback, prevent accidents, reduce server load
      ⚠️ NEVER rely on this for security (easily bypassed)

2. SERVER-SIDE VALIDATION (Security)
   ├─ Syntactic validation (format, type, structure)
   ├─ Semantic validation (business rules, ranges)
   └─ Context validation (authorization, state)
      ✅ ALWAYS validate on server - this is your security layer

3. DATABASE CONSTRAINTS (Data Integrity)
   └─ Final safety net for data consistency
      ✅ Complements but doesn't replace application validation
```

## Validation Strategy Decision Tree

```
For each input field:

1. What is the expected data type?
   ├─ String → Define max length, allowed characters, format
   ├─ Number → Define min/max, precision, positive/negative
   ├─ Date → Define format, valid range
   ├─ Boolean → Accept only true/false (or 0/1)
   ├─ Email → Validate format, max length, normalize
   ├─ URL → Validate format, allowlist schemes (http/https)
   └─ File → Validate type, size, content

2. What is the input used for?
   ├─ SQL Query → Use parameterized queries (NO sanitization needed)
   ├─ HTML Output → HTML entity encode
   ├─ JavaScript → JavaScript escape or JSON.stringify
   ├─ Shell Command → Avoid entirely, or strict allowlist
   ├─ File Path → Validate no directory traversal
   └─ Regular Expression → Escape regex special chars

3. What are the business rules?
   ├─ Required vs Optional
   ├─ Format requirements (e.g., phone number format)
   ├─ Uniqueness constraints (e.g., username)
   ├─ Relationships (e.g., user owns resource)
   └─ State requirements (e.g., order must be pending)

4. Validation approach:
   ├─ Allowlist (preferred) → Define what IS allowed
   └─ Denylist (avoid) → Define what is NOT allowed
      ⚠️ Easy to miss edge cases with denylists
```

## Core Validation Patterns

### 1. Type Validation

```javascript
// Using validation library (Joi, Yup, etc.)
const Joi = require('joi');

const userSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required(),

  email: Joi.string()
    .email()
    .required(),

  password: Joi.string()
    .min(12)
    .max(128)
    .required(),

  age: Joi.number()
    .integer()
    .min(13)
    .max(120)
    .optional(),

  website: Joi.string()
    .uri({ scheme: ['http', 'https'] })
    .optional(),

  role: Joi.string()
    .valid('user', 'admin', 'moderator')
    .default('user')
});

// Validate input
function validateUser(data) {
  const { error, value } = userSchema.validate(data, {
    abortEarly: false,  // Return all errors
    stripUnknown: true  // Remove unknown fields
  });

  if (error) {
    throw new ValidationError(error.details);
  }

  return value;
}
```

### 2. String Validation

```python
import re
from typing import Optional

def validate_string(
    value: str,
    min_length: int = 0,
    max_length: int = 1000,
    pattern: Optional[str] = None,
    allowed_chars: Optional[str] = None
) -> str:
    """
    Validate string input with multiple constraints.
    """
    # Check type
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Check length
    if len(value) < min_length:
        raise ValueError(f"String too short (min: {min_length})")

    if len(value) > max_length:
        raise ValueError(f"String too long (max: {max_length})")

    # Check pattern
    if pattern and not re.match(pattern, value):
        raise ValueError(f"String does not match required pattern")

    # Check allowed characters (allowlist)
    if allowed_chars:
        disallowed = set(value) - set(allowed_chars)
        if disallowed:
            raise ValueError(f"String contains disallowed characters: {disallowed}")

    return value

# Usage examples
username = validate_string(
    input_value,
    min_length=3,
    max_length=20,
    pattern=r'^[a-zA-Z0-9_]+$'
)

product_name = validate_string(
    input_value,
    max_length=100,
    allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_'
)
```

### 3. Email Validation

```javascript
// Basic format validation
function isValidEmail(email) {
  // RFC 5322 simplified regex
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

  if (!emailRegex.test(email)) {
    return false;
  }

  // Additional checks
  if (email.length > 254) {  // RFC 5321
    return false;
  }

  const [local, domain] = email.split('@');

  if (local.length > 64) {  // RFC 5321
    return false;
  }

  return true;
}

// Normalize email
function normalizeEmail(email) {
  // Convert to lowercase
  email = email.toLowerCase().trim();

  // For Gmail: remove dots and +alias from local part
  const [local, domain] = email.split('@');

  if (domain === 'gmail.com') {
    const normalized = local.split('+')[0].replace(/\./g, '');
    return `${normalized}@${domain}`;
  }

  return email;
}
```

### 4. URL Validation

```python
from urllib.parse import urlparse
from typing import List

def validate_url(
    url: str,
    allowed_schemes: List[str] = ['http', 'https'],
    allowed_domains: Optional[List[str]] = None,
    max_length: int = 2048
) -> str:
    """
    Validate URL with scheme and domain restrictions.
    """
    if len(url) > max_length:
        raise ValueError(f"URL too long (max: {max_length})")

    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Invalid URL format")

    # Validate scheme
    if parsed.scheme not in allowed_schemes:
        raise ValueError(f"URL scheme must be one of: {allowed_schemes}")

    # Validate domain (if restricted)
    if allowed_domains and parsed.netloc not in allowed_domains:
        raise ValueError(f"URL domain must be one of: {allowed_domains}")

    # Check for dangerous patterns
    if '@' in url:  # Potential credential leakage
        raise ValueError("URLs with embedded credentials not allowed")

    return url

# Usage
safe_url = validate_url(
    user_input,
    allowed_schemes=['https'],
    allowed_domains=['example.com', 'api.example.com']
)
```

### 5. File Upload Validation

```javascript
const fileType = require('file-type');
const crypto = require('crypto');

async function validateFileUpload(file, options = {}) {
  const {
    maxSize = 10 * 1024 * 1024,  // 10MB default
    allowedTypes = ['image/jpeg', 'image/png', 'image/gif'],
    allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  } = options;

  // Check file size
  if (file.size > maxSize) {
    throw new Error(`File too large (max: ${maxSize} bytes)`);
  }

  // Don't trust client-provided MIME type
  // Verify actual file content
  const type = await fileType.fromBuffer(file.buffer);

  if (!type || !allowedTypes.includes(type.mime)) {
    throw new Error(`File type not allowed (allowed: ${allowedTypes.join(', ')})`);
  }

  // Verify extension matches content
  const ext = '.' + type.ext;
  if (!allowedExtensions.includes(ext)) {
    throw new Error(`File extension not allowed`);
  }

  // Generate safe filename
  const hash = crypto.createHash('sha256').update(file.buffer).digest('hex');
  const safeFilename = `${hash}${ext}`;

  return {
    originalName: file.originalname,
    safeFilename,
    mimeType: type.mime,
    size: file.size
  };
}

// Express middleware
const multer = require('multer');

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024,  // 10MB
    files: 5  // Max 5 files
  },
  fileFilter: (req, file, cb) => {
    // Initial filter (will verify content later)
    const allowedMimes = ['image/jpeg', 'image/png', 'image/gif'];

    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    // Verify actual file content
    const validated = await validateFileUpload(req.file);

    // Scan for malware (optional but recommended)
    await scanForMalware(req.file.buffer);

    // Save file
    await saveFile(validated.safeFilename, req.file.buffer);

    res.json({ filename: validated.safeFilename });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

## Context-Specific Sanitization

### 1. SQL Injection Prevention

```python
import psycopg2

# ❌ WRONG: String concatenation
def get_user_wrong(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    # Vulnerable to: ' OR '1'='1 --

# ✅ CORRECT: Parameterized query
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))

# ❌ WRONG: Dynamic table/column names (can't be parameterized)
def get_data_wrong(table_name, column_name):
    query = f"SELECT {column_name} FROM {table_name}"
    # SQL injection via table/column names

# ✅ CORRECT: Allowlist for identifiers
ALLOWED_TABLES = {'users', 'posts', 'comments'}
ALLOWED_COLUMNS = {'id', 'name', 'email', 'created_at'}

def get_data(table_name, column_name):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    if column_name not in ALLOWED_COLUMNS:
        raise ValueError("Invalid column name")

    # Use psycopg2.sql for safe identifier quoting
    from psycopg2 import sql
    query = sql.SQL("SELECT {column} FROM {table}").format(
        column=sql.Identifier(column_name),
        table=sql.Identifier(table_name)
    )
    cursor.execute(query)
```

### 2. XSS Prevention (HTML Output)

```javascript
// HTML Entity Encoding
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };

  return text.replace(/[&<>"'/]/g, char => map[char]);
}

// Using template engine with auto-escaping (Handlebars)
const Handlebars = require('handlebars');

// ✅ Automatically escaped
const template = Handlebars.compile('<div>{{userInput}}</div>');
const html = template({ userInput: '<script>alert("XSS")</script>' });
// Result: <div>&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;</div>

// ⚠️ Unescaped (use only for trusted content)
const dangerousTemplate = Handlebars.compile('<div>{{{trustedHtml}}}</div>');

// DOMPurify for rich text (sanitizes HTML while allowing safe tags)
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

function sanitizeHtml(dirty) {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href'],
    ALLOWED_URI_REGEXP: /^https?:\/\//  // Only allow http(s) URLs
  });
}

const safeHtml = sanitizeHtml('<p>Safe content</p><script>alert("XSS")</script>');
// Result: <p>Safe content</p>
```

### 3. JavaScript Context Encoding

```javascript
// For embedding in JavaScript
function escapeJavaScript(text) {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t')
    .replace(/\f/g, '\\f')
    .replace(/</g, '\\x3C')  // Prevent </script> injection
    .replace(/>/g, '\\x3E');
}

// ✅ CORRECT: JSON.stringify for data
const userData = { name: user.name, email: user.email };
const script = `
  <script>
    const user = ${JSON.stringify(userData)};
  </script>
`;

// ❌ WRONG: Direct interpolation
const badScript = `
  <script>
    const userName = "${user.name}";  // XSS if name contains quotes
  </script>
`;
```

### 4. URL Context Encoding

```javascript
// For URL parameters
function encodeForURL(text) {
  return encodeURIComponent(text);
}

// For building URLs
const baseUrl = 'https://example.com/search';
const query = user.input;  // Could be malicious

// ✅ CORRECT: Use URLSearchParams
const url = new URL(baseUrl);
url.searchParams.set('q', query);
// Result: https://example.com/search?q=encoded%20value

// ❌ WRONG: String concatenation
const badUrl = `${baseUrl}?q=${query}`;  // Injection possible
```

### 5. Shell Command Sanitization

```python
import subprocess
import shlex

# ❌ WRONG: Shell injection vulnerable
def run_command_wrong(filename):
    subprocess.run(f'cat {filename}', shell=True)
    # Vulnerable to: file.txt; rm -rf /

# ✅ BETTER: Avoid shell, use list
def run_command_better(filename):
    subprocess.run(['cat', filename], shell=False)
    # Still vulnerable to path traversal

# ✅ BEST: Avoid shell commands entirely
def read_file(filename):
    # Validate filename
    if not re.match(r'^[a-zA-Z0-9_-]+\.txt$', filename):
        raise ValueError("Invalid filename")

    # Use safe path joining
    from pathlib import Path
    safe_path = Path('/safe/directory') / filename

    # Prevent directory traversal
    if not str(safe_path.resolve()).startswith('/safe/directory'):
        raise ValueError("Path traversal attempt")

    with open(safe_path, 'r') as f:
        return f.read()

# If shell commands are absolutely necessary:
def safe_shell_command(user_input):
    # Use shlex.quote to escape for shell
    safe_input = shlex.quote(user_input)
    subprocess.run(f'echo {safe_input}', shell=True)
```

## Path Traversal Prevention

```javascript
const path = require('path');

function validateFilePath(userPath, baseDir) {
  // Resolve to absolute path
  const fullPath = path.resolve(baseDir, userPath);

  // Ensure path is within base directory
  if (!fullPath.startsWith(path.resolve(baseDir))) {
    throw new Error('Path traversal attempt detected');
  }

  // Additional checks
  if (userPath.includes('\0')) {  // Null byte injection
    throw new Error('Invalid path');
  }

  return fullPath;
}

// Usage
app.get('/download/:filename', (req, res) => {
  try {
    const filename = req.params.filename;
    const safeDir = '/var/www/downloads';

    // Validate path
    const safePath = validateFilePath(filename, safeDir);

    // Additional validation
    if (!safePath.endsWith('.pdf')) {
      return res.status(400).json({ error: 'Only PDF files allowed' });
    }

    res.download(safePath);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

## NoSQL Injection Prevention

```javascript
// MongoDB injection prevention
const sanitize = require('mongo-sanitize');

// ❌ WRONG: Direct user input
db.collection('users').findOne({
  username: req.body.username
});
// Vulnerable to: { "$gt": "" } (returns first user)

// ✅ CORRECT: Sanitize input
const username = sanitize(req.body.username);
db.collection('users').findOne({
  username: username
});

// ✅ BETTER: Type validation
if (typeof req.body.username !== 'string') {
  return res.status(400).json({ error: 'Invalid username type' });
}

db.collection('users').findOne({
  username: req.body.username
});

// ✅ BEST: Schema validation with Mongoose
const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    match: /^[a-zA-Z0-9_]+$/,
    minlength: 3,
    maxlength: 30
  }
});
```

## Regular Expression DoS Prevention

```python
import re
import timeout_decorator

# ❌ WRONG: User-controlled regex
def search_wrong(pattern, text):
    regex = re.compile(pattern)
    return regex.findall(text)
    # Vulnerable to ReDoS: (a+)+b

# ✅ BETTER: Allowlist of patterns
ALLOWED_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?1?\d{9,15}$',
    'username': r'^[a-zA-Z0-9_]{3,30}$'
}

def search_safe(pattern_name, text):
    if pattern_name not in ALLOWED_PATTERNS:
        raise ValueError("Invalid pattern name")

    pattern = ALLOWED_PATTERNS[pattern_name]
    regex = re.compile(pattern)
    return regex.findall(text)

# ✅ BEST: Add timeout for regex operations
@timeout_decorator.timeout(1)  # 1 second timeout
def search_with_timeout(pattern, text):
    regex = re.compile(pattern)
    return regex.findall(text)
```

## Validation Checklist

### Input Validation
- [ ] Validate on server-side (never trust client)
- [ ] Validate type, format, length, and range
- [ ] Use allowlists over denylists
- [ ] Reject invalid input (don't try to fix)
- [ ] Normalize input before validation (e.g., trim, lowercase)
- [ ] Validate all sources (body, query, params, headers, cookies)

### Output Encoding
- [ ] Encode based on output context (HTML, JS, URL, CSS)
- [ ] Use auto-escaping template engines
- [ ] Never insert untrusted data into dangerous contexts
- [ ] Use Content-Security-Policy headers
- [ ] Sanitize rich text with allowlist-based library

### SQL Injection Prevention
- [ ] Always use parameterized queries
- [ ] Never concatenate strings to build SQL
- [ ] Use allowlists for table/column names
- [ ] Use ORM with proper escaping
- [ ] Implement least privilege database access

### File Security
- [ ] Validate file type by content (not just extension)
- [ ] Limit file size
- [ ] Generate safe filenames (don't trust user input)
- [ ] Store outside web root
- [ ] Scan for malware
- [ ] Prevent path traversal

### API Security
- [ ] Validate all request parameters
- [ ] Implement rate limiting
- [ ] Validate Content-Type header
- [ ] Reject unexpected fields (strict schemas)
- [ ] Return appropriate error codes (don't leak info)

## Testing Input Validation

### Manual Test Inputs

**SQL Injection:**
```
' OR '1'='1
'; DROP TABLE users--
' UNION SELECT * FROM passwords--
admin'--
```

**XSS:**
```
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
javascript:alert('XSS')
<svg onload=alert('XSS')>
```

**Path Traversal:**
```
../../../etc/passwd
..\..\..\..\windows\system32\config\sam
....//....//....//etc/passwd
```

**NoSQL Injection:**
```json
{"$gt": ""}
{"$ne": null}
{"username": {"$regex": ".*"}}
```

**Command Injection:**
```
; ls
| whoami
`id`
$(cat /etc/passwd)
```

### Automated Testing

```javascript
// Fuzzing example with Jest
describe('Input Validation Security', () => {
  const maliciousInputs = [
    "<script>alert('XSS')</script>",
    "'; DROP TABLE users--",
    "../../../etc/passwd",
    '{"$gt": ""}',
    "; ls",
    'A'.repeat(10000)  // Length overflow
  ];

  test.each(maliciousInputs)(
    'should reject malicious input: %s',
    async (maliciousInput) => {
      const response = await request(app)
        .post('/api/users')
        .send({ username: maliciousInput });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    }
  );
});
```

## Integration with PACT Phases

### PREPARE Phase
- Research input validation requirements
- Identify all user input points
- Review validation libraries for tech stack

### ARCHITECT Phase
- Design validation strategy (where, when, how)
- Plan sanitization for output contexts
- Document validation rules and error handling

### CODE Phase
- Implement validation using patterns from this guide
- Use schema validation libraries
- Apply context-specific sanitization

### TEST Phase
- Test with malicious inputs from this guide
- Use automated fuzzing tools
- Verify all input points are validated
- Test error messages don't leak information
