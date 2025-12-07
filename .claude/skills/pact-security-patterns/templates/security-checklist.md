# Security Checklist Template

## Feature: [Feature Name]

### Overview
- **Risk Level**: [High | Medium | Low]
- **Data Sensitivity**: [PII | Financial | Public]
- **Review Date**: [Date]
- **Reviewer**: [Name]

---

## Authentication & Authorization

### Authentication
- [ ] Authentication required for all sensitive endpoints
- [ ] Strong password policy enforced (if applicable)
- [ ] MFA available for high-risk operations
- [ ] Session timeout configured appropriately
- [ ] Secure session token generation (cryptographically random)

### Authorization
- [ ] Role-based access control implemented
- [ ] Principle of least privilege applied
- [ ] Resource ownership verified before access
- [ ] Admin functions properly protected
- [ ] API endpoints require appropriate scopes/permissions

---

## Input Validation

### General
- [ ] All user input validated on server-side
- [ ] Input length limits enforced
- [ ] Input type validation (numbers, emails, etc.)
- [ ] Whitelist validation preferred over blacklist
- [ ] File upload validation (type, size, content)

### Injection Prevention
- [ ] SQL queries use parameterized statements
- [ ] NoSQL injection prevented
- [ ] Command injection prevented
- [ ] LDAP injection prevented (if applicable)
- [ ] XML/XXE injection prevented

---

## Output Encoding

- [ ] HTML output properly encoded
- [ ] JavaScript strings properly escaped
- [ ] URL parameters encoded
- [ ] JSON responses properly formatted
- [ ] Content-Type headers set correctly

---

## Data Protection

### In Transit
- [ ] TLS 1.2+ required for all connections
- [ ] HSTS header configured
- [ ] Certificate pinning (mobile apps)
- [ ] Secure WebSocket (WSS) used

### At Rest
- [ ] Sensitive data encrypted in database
- [ ] Encryption keys properly managed
- [ ] Backups encrypted
- [ ] Logs don't contain sensitive data

### PII Handling
- [ ] PII identified and classified
- [ ] Data minimization applied
- [ ] Retention policies defined
- [ ] Right to deletion supported
- [ ] Data access logged

---

## API Security

- [ ] Rate limiting implemented
- [ ] Request size limits enforced
- [ ] API versioning strategy in place
- [ ] Deprecated endpoints documented
- [ ] CORS properly configured
- [ ] API keys/tokens securely transmitted

---

## Error Handling

- [ ] Generic error messages to users
- [ ] Detailed errors logged server-side
- [ ] Stack traces not exposed
- [ ] Error codes don't leak information
- [ ] Failed login attempts limited

---

## Security Headers

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

- [ ] CSP configured and tested
- [ ] X-Content-Type-Options set
- [ ] X-Frame-Options set
- [ ] HSTS enabled
- [ ] Referrer-Policy configured

---

## Logging & Monitoring

- [ ] Security events logged
- [ ] Failed authentication logged
- [ ] Authorization failures logged
- [ ] Logs protected from tampering
- [ ] Alerting configured for suspicious activity

---

## Dependency Security

- [ ] Dependencies scanned for vulnerabilities
- [ ] Automated vulnerability scanning in CI/CD
- [ ] Patch management process defined
- [ ] No known critical vulnerabilities

---

## Final Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| Security Reviewer | | | |
| Tech Lead | | | |

---
*Generated from pact-security-patterns skill template*
