---
name: pact-security-patterns
description: |
  CROSS-CUTTING: Security patterns and best practices for ALL PACT phases.

  Provides OWASP Top 10 guidance, authentication/authorization patterns, input validation,
  secure coding practices, secrets management, and security testing checklists.

  Use when: implementing authentication, handling user input, storing secrets,
  designing authorization, reviewing code for vulnerabilities, planning security tests.
allowed-tools:
  - Read
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Cross-cutting"
  version: "1.0.0"
  primary-agents:
    - pact-backend-coder
    - pact-frontend-coder
    - pact-database-engineer
    - pact-test-engineer
---

# Security Patterns Skill

Cross-cutting security patterns and best practices for ALL phases of PACT framework.

## Quick Reference

### Security Decision Tree

```
Implementing authentication/authorization?
├─ YES → Use Authentication Decision Tree (see references/authentication.md)
│   ├─ Stateless API → JWT with refresh tokens
│   ├─ Stateful web app → Server-side sessions
│   └─ Third-party auth → OAuth 2.0 / OpenID Connect
│
├─ Handling user input?
│   └─ YES → Use Input Validation Checklist (see references/input-validation.md)
│       ├─ Validate format and type
│       ├─ Sanitize for context (SQL, HTML, shell)
│       ├─ Enforce length and range limits
│       └─ Use allowlists over denylists
│
├─ Storing sensitive data?
│   └─ YES → Secrets Management Patterns
│       ├─ Never commit secrets to version control
│       ├─ Use environment variables or secret management service
│       ├─ Encrypt at rest and in transit
│       └─ Rotate credentials regularly
│
└─ Review OWASP Top 10 (see references/owasp-top10.md)
```

### When to Use Sequential Thinking for Security

Use `mcp__sequential-thinking__sequentialthinking` when:
- Designing authentication/authorization flows with multiple decision points
- Analyzing security vulnerabilities and their cascading impacts
- Planning defense-in-depth strategies across multiple layers
- Evaluating trade-offs between security and usability
- Designing incident response and recovery procedures

## OWASP Top 10 Quick Reference

### 2021 OWASP Top 10

1. **A01:2021 - Broken Access Control**
   - Risk: Users acting outside intended permissions
   - Prevention: Deny by default, enforce ownership checks, disable directory listing

2. **A02:2021 - Cryptographic Failures**
   - Risk: Exposure of sensitive data due to weak/missing encryption
   - Prevention: Encrypt data in transit (TLS) and at rest, use strong algorithms

3. **A03:2021 - Injection**
   - Risk: Untrusted data sent to interpreter as part of command/query
   - Prevention: Parameterized queries, input validation, ORMs with escaping

4. **A04:2021 - Insecure Design**
   - Risk: Missing or ineffective security controls by design
   - Prevention: Threat modeling, secure design patterns, defense in depth

5. **A05:2021 - Security Misconfiguration**
   - Risk: Insecure default configurations, incomplete setups, verbose errors
   - Prevention: Hardened configurations, minimal platform, automated security scanning

6. **A06:2021 - Vulnerable and Outdated Components**
   - Risk: Using components with known vulnerabilities
   - Prevention: Inventory dependencies, monitor CVEs, automated updates

7. **A07:2021 - Identification and Authentication Failures**
   - Risk: Weak authentication allowing credential stuffing, brute force
   - Prevention: MFA, strong password policies, secure session management

8. **A08:2021 - Software and Data Integrity Failures**
   - Risk: Code/infrastructure without integrity verification
   - Prevention: Digital signatures, trusted repos, CI/CD security controls

9. **A09:2021 - Security Logging and Monitoring Failures**
   - Risk: Insufficient logging preventing detection of breaches
   - Prevention: Log auth events, maintain audit trails, real-time monitoring

10. **A10:2021 - Server-Side Request Forgery (SSRF)**
    - Risk: Application fetching remote resource without validating URL
    - Prevention: Sanitize user input, allowlist destinations, network segmentation

**Detailed prevention strategies:** See `references/owasp-top10.md`

## Security Checklist by PACT Phase

### PREPARE Phase Security Checklist

When gathering requirements and researching:
- [ ] Identify all sensitive data types (PII, credentials, financial, health)
- [ ] Document compliance requirements (GDPR, HIPAA, PCI-DSS, SOC2)
- [ ] Map data flows and trust boundaries
- [ ] Research security requirements for third-party integrations
- [ ] Identify authentication and authorization requirements
- [ ] Document threat model based on asset value and attack surface
- [ ] Review security incidents in similar systems
- [ ] Identify applicable security standards (ISO 27001, NIST)
- [ ] Document encryption requirements (at rest, in transit)
- [ ] Understand rate limiting and DDoS protection needs

### ARCHITECT Phase Security Checklist

When designing system architecture:
- [ ] Apply principle of least privilege to all components
- [ ] Design defense in depth with multiple security layers
- [ ] Implement secure defaults (deny by default, fail securely)
- [ ] Separate security domains and enforce boundaries
- [ ] Design authentication flow with MFA support
- [ ] Plan authorization model (RBAC, ABAC, or hybrid)
- [ ] Design session management strategy
- [ ] Plan secrets management (vault, HSM, KMS)
- [ ] Design audit logging and monitoring strategy
- [ ] Plan encryption strategy (algorithms, key management)
- [ ] Design rate limiting and throttling mechanisms
- [ ] Plan security headers and CSP policies
- [ ] Design secure error handling (no information leakage)
- [ ] Plan input validation strategy (allowlists, schemas)
- [ ] Design secure communication channels (TLS, mTLS)
- [ ] Plan security testing approach (SAST, DAST, penetration testing)
- [ ] Document security assumptions and trust boundaries

### CODE Phase Security Checklist

When implementing features:
- [ ] **Input Validation**: Validate all inputs (see `references/input-validation.md`)
  - Type, format, length, range validation
  - Context-specific sanitization (SQL, HTML, shell, LDAP)
  - Allowlist over denylist approach

- [ ] **Authentication**: Implement secure authentication (see `references/authentication.md`)
  - Strong password hashing (bcrypt, Argon2, scrypt)
  - Secure session management
  - MFA support where required
  - Account lockout after failed attempts

- [ ] **Authorization**: Enforce access controls
  - Check permissions on every request
  - Verify resource ownership
  - Deny by default
  - Avoid insecure direct object references

- [ ] **Cryptography**: Use crypto correctly
  - TLS 1.2+ for data in transit
  - AES-256 for data at rest
  - Secure random number generation
  - Proper key management and rotation

- [ ] **Output Encoding**: Prevent injection attacks
  - Context-aware output encoding
  - Parameterized SQL queries
  - Template engines with auto-escaping
  - Content Security Policy headers

- [ ] **Error Handling**: Fail securely
  - Generic error messages to users
  - Detailed logging server-side
  - No stack traces in production
  - Proper exception handling

- [ ] **Logging**: Enable security monitoring
  - Log authentication events (success/failure)
  - Log authorization failures
  - Log input validation failures
  - Include correlation IDs
  - Never log secrets or PII

- [ ] **Dependencies**: Secure supply chain
  - Pin dependency versions
  - Audit for known vulnerabilities
  - Minimize third-party dependencies
  - Verify package integrity

### TEST Phase Security Checklist

When validating implementation:
- [ ] **Authentication Testing**
  - Weak password acceptance
  - Brute force protection
  - Session fixation and hijacking
  - Logout functionality
  - Password reset flow security

- [ ] **Authorization Testing**
  - Privilege escalation attempts
  - Insecure direct object references
  - Missing function-level access control
  - Cross-account access

- [ ] **Input Validation Testing**
  - SQL injection (parameterized queries)
  - XSS (reflected, stored, DOM-based)
  - Command injection
  - Path traversal
  - XML/JSON injection

- [ ] **Cryptography Testing**
  - TLS configuration (cipher suites, protocols)
  - Certificate validation
  - Encryption strength
  - Key storage security

- [ ] **Session Management Testing**
  - Session timeout enforcement
  - Secure cookie flags (HttpOnly, Secure, SameSite)
  - Session invalidation on logout
  - Concurrent session handling

- [ ] **API Security Testing**
  - Rate limiting effectiveness
  - Mass assignment vulnerabilities
  - CORS policy validation
  - API versioning security

- [ ] **Error Handling Testing**
  - Information leakage in errors
  - Stack trace exposure
  - Verbose error messages

- [ ] **OWASP Top 10 Verification**
  - Test all applicable OWASP Top 10 vulnerabilities
  - Use automated scanners (OWASP ZAP, Burp Suite)
  - Manual penetration testing
  - Code review for security issues

## Common Security Patterns

### Secure Password Handling

```
Password Storage:
1. NEVER store passwords in plaintext
2. Use adaptive hashing (bcrypt, Argon2, scrypt)
3. Include per-user salt (handled by algorithm)
4. Use high work factor (bcrypt: 12+, Argon2: depends)

Password Validation:
1. Minimum length: 12+ characters
2. Check against breached password database (HaveIBeenPwned)
3. No complexity requirements that reduce entropy
4. Allow passphrases and long passwords (64+ chars)
5. No password expiration without cause

Password Reset:
1. Send reset link, not password
2. Include time-limited token
3. Invalidate after single use
4. Require current password for change
5. Notify user of password changes
```

### Secure Session Management

```
Session Creation:
1. Generate cryptographically random session ID
2. Set HttpOnly flag (prevent XSS access)
3. Set Secure flag (HTTPS only)
4. Set SameSite flag (CSRF protection)
5. Regenerate session ID after login

Session Validation:
1. Check session ID on every request
2. Validate IP address (optional, breaks mobile)
3. Validate User-Agent (weak protection)
4. Implement absolute timeout (e.g., 24 hours)
5. Implement idle timeout (e.g., 30 minutes)

Session Termination:
1. Invalidate server-side session
2. Clear client-side cookies
3. Provide explicit logout endpoint
4. Log session termination event
```

### Secure API Design

```
Authentication:
├─ API Keys: Simple, limit to server-to-server
│   ├─ Include in header (not URL)
│   ├─ Rotate regularly
│   └─ Scope to minimum required permissions
│
├─ JWT: Stateless, good for distributed systems
│   ├─ Sign with strong secret (HMAC) or private key (RSA)
│   ├─ Include expiration (short-lived: 15-60 min)
│   ├─ Use refresh tokens for renewal
│   └─ Validate signature on every request
│
└─ OAuth 2.0: Third-party access
    ├─ Use authorization code flow (not implicit)
    ├─ Implement PKCE for public clients
    ├─ Validate redirect URIs
    └─ Use state parameter (CSRF protection)

Authorization:
1. Check permissions on every endpoint
2. Use scope-based access control
3. Implement rate limiting per user/IP
4. Validate all request parameters
5. Return 403 Forbidden (not 404) for unauthorized

Security Headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: appropriate policy
- Strict-Transport-Security: max-age=31536000
```

### Secrets Management

```
Storage:
├─ Development: .env files (gitignored)
├─ CI/CD: Environment variables or secrets manager
└─ Production: Dedicated secrets manager
    ├─ AWS Secrets Manager / Systems Manager
    ├─ HashiCorp Vault
    ├─ Azure Key Vault
    └─ GCP Secret Manager

Best Practices:
1. Never commit secrets to version control
2. Use different secrets per environment
3. Rotate secrets regularly (30-90 days)
4. Encrypt secrets at rest and in transit
5. Limit access to secrets (least privilege)
6. Audit secret access
7. Use short-lived credentials when possible
8. Invalidate secrets when no longer needed

Detection:
1. Use pre-commit hooks (detect-secrets, git-secrets)
2. Scan repositories for leaked secrets (GitHub Advanced Security)
3. Monitor for exposed credentials (leaked DB scans)
4. Implement secret scanning in CI/CD
```

### Input Validation Pattern

```
Three-Step Validation:
1. Syntactic validation (format, type, structure)
2. Semantic validation (business rules, ranges)
3. Context validation (authorization, state)

Implementation:
1. Validate on server-side (never trust client)
2. Validate early (before processing)
3. Allowlist over denylist
4. Use schema validation (JSON Schema, Joi, Yup)
5. Provide clear error messages (without leaking info)
6. Reject invalid input (don't try to fix)

Context-Specific Sanitization:
├─ SQL: Use parameterized queries (NEVER string concatenation)
├─ HTML: Escape <, >, &, ", ' or use DOMPurify
├─ JavaScript: JSON.stringify() or escape for context
├─ Shell: Avoid shell execution or use strict allowlist
├─ LDAP: Escape special chars or use library functions
└─ XPath/XML: Use parameterized queries or escape
```

## Security Testing Strategy

### Static Analysis (SAST)

**Tools by Language:**
- JavaScript/TypeScript: ESLint with security plugins, SonarQube
- Python: Bandit, Safety, Semgrep
- Java: SpotBugs, PMD, SonarQube
- C#: Security Code Scan, SonarQube
- Go: GoSec, Semgrep
- Ruby: Brakeman, RuboCop

**What to Check:**
- Hardcoded secrets
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure random number generation
- Weak cryptographic algorithms
- Path traversal vulnerabilities
- Command injection
- Insecure deserialization

### Dynamic Analysis (DAST)

**Tools:**
- OWASP ZAP (Zed Attack Proxy)
- Burp Suite
- Nikto
- SQLMap (SQL injection specific)
- XSStrike (XSS specific)

**What to Test:**
- Authentication bypass
- Authorization flaws
- Session management issues
- Input validation failures
- Error handling weaknesses
- Configuration issues
- TLS/SSL vulnerabilities

### Dependency Scanning

**Tools:**
- npm audit / yarn audit (JavaScript)
- pip-audit / Safety (Python)
- OWASP Dependency-Check (multi-language)
- Snyk
- GitHub Dependabot
- Renovate

**Process:**
1. Scan dependencies for known CVEs
2. Prioritize by severity and exploitability
3. Update to patched versions
4. If no patch: find alternative or mitigate
5. Monitor for new vulnerabilities continuously

### Penetration Testing

**Approach:**
1. Reconnaissance (gather system information)
2. Enumeration (identify entry points)
3. Exploitation (attempt to breach security)
4. Post-exploitation (assess impact)
5. Reporting (document findings)

**Focus Areas:**
- Authentication mechanisms
- Authorization controls
- Session management
- Input validation
- Business logic flaws
- API security
- Infrastructure security

## Security Code Review Checklist

When reviewing code for security:
- [ ] No hardcoded secrets or credentials
- [ ] All inputs validated before use
- [ ] SQL queries use parameterization
- [ ] Output properly encoded for context
- [ ] Authentication required for protected endpoints
- [ ] Authorization checked for every operation
- [ ] Sensitive operations logged
- [ ] Error messages don't leak information
- [ ] Dependencies up to date with no known vulnerabilities
- [ ] Cryptography uses strong, modern algorithms
- [ ] Random values use cryptographically secure generator
- [ ] File uploads validated and scanned
- [ ] Rate limiting on sensitive operations
- [ ] Security headers properly configured
- [ ] HTTPS enforced for sensitive data
- [ ] Sessions managed securely
- [ ] CSRF protection implemented
- [ ] XSS protection in place

## Resources and References

### Detailed Guides
- `references/owasp-top10.md` - Each OWASP vulnerability with prevention strategies
- `references/authentication.md` - JWT, sessions, OAuth patterns and implementation
- `references/input-validation.md` - Sanitization, encoding, validation patterns

### External Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- SANS Secure Coding Practices: https://www.sans.org/secure-coding/

### Security Standards
- PCI-DSS (Payment Card Industry)
- HIPAA (Healthcare)
- GDPR (EU Privacy)
- SOC 2 (Service Organizations)
- ISO 27001 (Information Security Management)

## MCP Tools for Security

This section provides guidance on WHEN and WHY to use MCP tools for security decisions. See agent documentation for invocation syntax.

### Available MCP Tools

The following MCP tool enhances security analysis and design:
- **sequential-thinking**: Threat modeling and security architecture reasoning

---

### sequential-thinking

**Purpose**: Extended reasoning capability for complex security decisions and threat analysis

**When to use**:
- Designing authentication flows with multiple decision points and failure modes (e.g., OAuth2 flow with PKCE, token refresh, account linking, and various attack vectors)
- Analyzing security vulnerabilities and their cascading impacts across system layers (e.g., SQL injection risk leading to data breach, privilege escalation, lateral movement)
- Planning defense-in-depth strategies for high-value assets (e.g., protecting financial transactions with input validation, authorization, encryption, audit logging, anomaly detection)
- Evaluating security vs usability trade-offs in access control design (e.g., MFA requirements, session timeout policies, password complexity rules)
- Designing incident response procedures for security breaches (e.g., detection, containment, eradication, recovery steps for different threat scenarios)
- Planning authorization models for complex multi-tenant systems (e.g., RBAC vs ABAC with hierarchical permissions, resource ownership, delegation)
- Evaluating encryption strategies across multiple threat models (e.g., data at rest, in transit, in use with key management considerations)

**When NOT to use**:
- Implementing well-established security patterns from references (e.g., password hashing with bcrypt)
- Simple HTTPS enforcement or security header configuration
- Routine security updates and vulnerability patching
- Following security checklists for standard OWASP Top 10 mitigation
- Security code reviews with clear violation of documented patterns

**Value for security**: Systematic reasoning reveals attack chains and vulnerabilities that simple checklists miss. Creates comprehensive threat models covering attacker motivations and capabilities. Documents security trade-off rationale for compliance audits.

**Integration approach**: Identify security-critical feature or design decision → Review OWASP Top 10 and threat landscape → Use sequential-thinking to enumerate attack vectors, defense layers, and failure scenarios → Implement controls with documented threat model → Test against reasoned attack scenarios.

**See all PACT coding agents (backend, frontend, database) and pact-test-engineer for invocation syntax and workflow integration.**

---

## When to Escalate

Security concerns that require specialist review:
- Novel authentication or cryptographic schemes
- Custom security protocols or implementations
- High-value targets (financial, healthcare, critical infrastructure)
- Compliance requirements (PCI-DSS, HIPAA, FedRAMP)
- Post-breach analysis or incident response
- Architecture review for security-critical systems
- Threat modeling for complex attack surfaces

**Remember**: Security is not a feature to add later. It must be integrated into every phase of the PACT framework from initial preparation through final testing.
