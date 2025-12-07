# Requirement Templates for Prepare Phase

**Purpose**: Standardized templates for capturing and organizing functional, non-functional, and acceptance criteria during the Prepare phase.

**When to Use**: Beginning a new project, defining feature scope, gathering stakeholder requirements, or documenting system constraints.

---

## Quick Reference

### Requirement Types

**Functional Requirements**:
- WHAT the system must do
- User-facing features and capabilities
- Business logic and workflows
- Data operations (CRUD)

**Non-Functional Requirements**:
- HOW the system must perform
- Performance, scalability, security
- Reliability, availability, maintainability
- Usability, accessibility, compliance

**Acceptance Criteria**:
- HOW to verify requirements are met
- Testable conditions for "done"
- Edge cases and error scenarios
- User acceptance tests

---

## Functional Requirements Template

### Format: User Story with Acceptance Criteria

```markdown
# Feature: [Feature Name]

## User Story

**As a** [type of user]
**I want** [to perform some action]
**So that** [I can achieve some goal]

**Priority**: [Must-Have / Should-Have / Nice-to-Have]
**Estimated Effort**: [Small / Medium / Large]
**Dependencies**: [List any dependencies]

## Functional Requirements

### FR-001: [Requirement Title]

**Description**: [Detailed description of what the system must do]

**Inputs**:
- [Input 1]: [Description, format, constraints]
- [Input 2]: [Description, format, constraints]

**Processing**:
- [Step 1]: [What happens]
- [Step 2]: [What happens]
- [Step 3]: [What happens]

**Outputs**:
- [Output 1]: [Description, format]
- [Output 2]: [Description, format]

**Business Rules**:
- [Rule 1]: [Constraint or validation]
- [Rule 2]: [Constraint or validation]

**Acceptance Criteria**:
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [edge case], when [action], then [expected result]

## Example Scenarios

### Scenario 1: Happy Path
```
Given: User has valid credentials
When: User submits login form
Then: User is redirected to dashboard
And: User session is created
And: Last login timestamp is updated
```

### Scenario 2: Error Path
```
Given: User has invalid credentials
When: User submits login form
Then: Error message "Invalid username or password" is displayed
And: Login form remains visible
And: Password field is cleared
And: Failed login attempt is logged
```

### Scenario 3: Edge Case
```
Given: User's account is locked
When: User submits valid credentials
Then: Error message "Account locked due to multiple failed attempts" is displayed
And: Instructions to unlock account are provided
And: Support contact information is shown
```
```

---

## Functional Requirements: Detailed Example

### Example: User Authentication System

```markdown
# Feature: User Authentication

## User Stories

### US-001: User Login

**As a** registered user
**I want** to log in with my email and password
**So that** I can access my personal account

**Priority**: Must-Have
**Estimated Effort**: Medium
**Dependencies**: User registration system

## Functional Requirements

### FR-001: Email/Password Login

**Description**: System must authenticate users with email and password credentials

**Inputs**:
- Email: String, valid email format, max 255 characters
- Password: String, min 8 characters, max 128 characters
- Remember Me: Boolean, optional (default: false)

**Processing**:
1. Validate email format
2. Retrieve user record by email
3. Compare submitted password with stored hash (bcrypt)
4. If match, generate session token (JWT)
5. If "Remember Me" is true, set token expiry to 30 days; else 24 hours
6. Record login timestamp and IP address
7. Return authentication token and user profile

**Outputs**:
- Success: Authentication token (JWT), user profile (ID, name, email, role)
- Failure: Error message with specific reason

**Business Rules**:
- Passwords must be hashed with bcrypt (minimum cost factor: 10)
- After 5 failed attempts within 15 minutes, lock account for 30 minutes
- Email comparison must be case-insensitive
- Passwords are case-sensitive
- Session tokens must expire (24 hours default, 30 days with "Remember Me")
- Failed login attempts must be logged for security monitoring

**Acceptance Criteria**:
- [ ] Given valid email and password, when user submits login form, then user receives auth token and is redirected to dashboard
- [ ] Given invalid email format, when user submits form, then error "Invalid email format" is displayed immediately
- [ ] Given valid email but wrong password, when user submits form, then error "Invalid credentials" is displayed
- [ ] Given 5 failed attempts within 15 minutes, when user submits 6th attempt, then error "Account locked for 30 minutes" is displayed
- [ ] Given "Remember Me" is checked, when user logs in successfully, then token expiry is set to 30 days
- [ ] Given "Remember Me" is unchecked, when user logs in successfully, then token expiry is set to 24 hours

---

### FR-002: Session Management

**Description**: System must manage user sessions and enforce session expiration

**Inputs**:
- Session token (JWT) in Authorization header

**Processing**:
1. Extract token from Authorization header
2. Verify token signature
3. Check token expiration
4. If valid, load user data from token claims
5. If expired, return 401 Unauthorized

**Outputs**:
- Success: User data from token
- Failure: 401 Unauthorized error

**Business Rules**:
- Tokens must be signed with HS256 algorithm
- Expired tokens cannot be renewed (must re-authenticate)
- Token payload must include: user_id, email, role, issued_at, expires_at
- Server must maintain secret key for token signing (rotate every 90 days)

**Acceptance Criteria**:
- [ ] Given valid unexpired token, when user makes authenticated request, then request is processed
- [ ] Given expired token, when user makes request, then 401 error is returned with message "Session expired"
- [ ] Given tampered token, when user makes request, then 401 error is returned with message "Invalid token"
- [ ] Given missing token, when user makes authenticated request, then 401 error is returned with message "Authentication required"

---

### FR-003: Logout

**Description**: System must allow users to terminate their session

**Inputs**:
- Logout request from authenticated user

**Processing**:
1. Verify user is authenticated
2. Invalidate session token (add to revocation list)
3. Clear client-side session data

**Outputs**:
- Success: Logout confirmation, redirect to login page

**Business Rules**:
- Revoked tokens must remain in revocation list until expiration
- Logout must be idempotent (multiple calls have same effect)

**Acceptance Criteria**:
- [ ] Given authenticated user, when user clicks logout, then user is redirected to login page
- [ ] Given authenticated user, when user logs out, then session token is invalidated
- [ ] Given logged out user, when using old token, then 401 error is returned
```

---

## Non-Functional Requirements Template

### Performance Requirements

```markdown
## Performance Requirements

### NFR-P001: Response Time

**Category**: Performance
**Priority**: Must-Have

**Requirement**: API endpoints must respond within specified time limits

**Metrics**:
- **P50 (Median)**: ≤ 200ms for read operations
- **P95**: ≤ 500ms for read operations
- **P99**: ≤ 1000ms for read operations
- **P50**: ≤ 500ms for write operations
- **P95**: ≤ 1000ms for write operations

**Measurement Approach**:
- Load testing with realistic workload (10,000 concurrent users)
- Continuous monitoring in production
- Alert if P95 exceeds threshold for 5 minutes

**Acceptance Criteria**:
- [ ] Under normal load (1,000 users), P95 response time ≤ 500ms
- [ ] Under peak load (10,000 users), P95 response time ≤ 1000ms
- [ ] Dashboard page loads in ≤ 2 seconds (measured by Lighthouse)

---

### NFR-P002: Throughput

**Category**: Performance
**Priority**: Must-Have

**Requirement**: System must handle expected request volume

**Metrics**:
- **Normal Load**: 1,000 requests/second
- **Peak Load**: 5,000 requests/second
- **Sustained Peak**: Support peak load for 1 hour

**Measurement Approach**:
- Load testing with gradual ramp-up
- Monitor CPU, memory, database connections
- Measure degradation under load

**Acceptance Criteria**:
- [ ] System handles 1,000 req/s with <5% error rate
- [ ] System handles 5,000 req/s with <10% error rate
- [ ] System maintains peak load for 1 hour without crashes

---

### NFR-P003: Database Query Performance

**Category**: Performance
**Priority**: Should-Have

**Requirement**: Database queries must be optimized

**Metrics**:
- **Simple SELECT**: ≤ 10ms
- **JOIN queries**: ≤ 50ms
- **Aggregation queries**: ≤ 100ms
- **Full-text search**: ≤ 200ms

**Measurement Approach**:
- Explain query plans for all queries
- Monitor slow query log (threshold: 100ms)
- Use database performance monitoring tools

**Acceptance Criteria**:
- [ ] All queries have appropriate indexes
- [ ] No N+1 query problems
- [ ] Query plans reviewed and optimized
```

---

### Scalability Requirements

```markdown
## Scalability Requirements

### NFR-S001: Horizontal Scaling

**Category**: Scalability
**Priority**: Must-Have

**Requirement**: Application must scale horizontally by adding instances

**Constraints**:
- No server-side session state (use stateless authentication)
- Database connections must be pooled
- Shared resources (cache, queues) must be external

**Target Scale**:
- Support 10,000 concurrent users with 3 instances
- Support 100,000 concurrent users with 30 instances
- Linear scaling up to 30 instances

**Acceptance Criteria**:
- [ ] Application runs without modification on 1-30 instances
- [ ] Load balancer distributes traffic evenly
- [ ] No session affinity required
- [ ] Auto-scaling based on CPU/memory thresholds works

---

### NFR-S002: Data Volume

**Category**: Scalability
**Priority**: Should-Have

**Requirement**: System must handle expected data growth

**Projected Growth**:
- Year 1: 1M users, 10M records
- Year 2: 5M users, 100M records
- Year 3: 20M users, 500M records

**Constraints**:
- Query performance must not degrade >20% at 10x data volume
- Database must support partitioning/sharding
- Archive strategy for old data

**Acceptance Criteria**:
- [ ] Tested with 100M records in database
- [ ] Query performance acceptable at 100M records
- [ ] Archival strategy defined for data >2 years old
```

---

### Security Requirements

```markdown
## Security Requirements

### NFR-SEC001: Authentication Security

**Category**: Security
**Priority**: Must-Have

**Requirement**: User authentication must be secure

**Specifications**:
- Passwords hashed with bcrypt (cost factor ≥ 10)
- Session tokens signed with HS256
- HTTPS required for all authentication endpoints
- TLS 1.2 minimum
- Password complexity enforced (min 8 chars, 1 uppercase, 1 number, 1 special)
- Account lockout after 5 failed attempts

**Threats Mitigated**:
- Brute force attacks (rate limiting, account lockout)
- Rainbow table attacks (bcrypt with salt)
- Man-in-the-middle (HTTPS/TLS)
- Session hijacking (secure, httpOnly cookies)

**Acceptance Criteria**:
- [ ] Passwords hashed with bcrypt (verified in code)
- [ ] HTTP authentication endpoints return 403
- [ ] TLS 1.0/1.1 connections rejected
- [ ] Weak passwords rejected with clear error message
- [ ] Account locks after 5 failed attempts

---

### NFR-SEC002: Data Protection

**Category**: Security
**Priority**: Must-Have

**Requirement**: Sensitive data must be protected

**Specifications**:
- PII encrypted at rest (AES-256)
- All data encrypted in transit (TLS 1.2+)
- Secrets managed in secrets manager (not environment variables)
- Database credentials rotated every 90 days
- API keys rotated every 90 days
- Audit log for all data access

**Data Classification**:
- **Public**: Product catalog, marketing content
- **Internal**: User analytics, system logs
- **Confidential**: User PII, payment information
- **Restricted**: Authentication credentials, encryption keys

**Acceptance Criteria**:
- [ ] PII fields encrypted in database
- [ ] Secrets stored in AWS Secrets Manager / HashiCorp Vault
- [ ] Audit log captures all PII access
- [ ] Credential rotation process documented and tested
```

---

### Reliability Requirements

```markdown
## Reliability Requirements

### NFR-R001: Availability

**Category**: Reliability
**Priority**: Must-Have

**Requirement**: System must be available during business hours

**Target**:
- **Uptime**: 99.9% (8.76 hours downtime/year)
- **Planned Maintenance**: Max 4 hours/month outside business hours
- **MTTR (Mean Time to Repair)**: < 1 hour

**Measurement**:
- Uptime monitoring (Pingdom, UptimeRobot)
- Incident tracking and postmortem
- Monthly availability reports

**Acceptance Criteria**:
- [ ] Health check endpoint responds within 1 second
- [ ] System recovers from instance failure in < 5 minutes
- [ ] Database failover tested and < 30 seconds

---

### NFR-R002: Error Handling

**Category**: Reliability
**Priority**: Must-Have

**Requirement**: System must handle errors gracefully

**Specifications**:
- All errors logged with context (user_id, request_id, timestamp)
- User-facing errors must be actionable
- No sensitive information in error messages
- Retry logic for transient failures
- Circuit breaker for dependent services

**Error Levels**:
- **User Error (400s)**: Clear message, suggest fix
- **Server Error (500s)**: Generic message, log details, alert team

**Acceptance Criteria**:
- [ ] All API errors return structured JSON error response
- [ ] 500 errors logged with full stack trace
- [ ] Critical errors trigger alerts (PagerDuty, Slack)
- [ ] Database connection failures retry 3 times with backoff
```

---

## Acceptance Criteria Template

### Given-When-Then Format

```markdown
## Acceptance Criteria: [Feature Name]

### AC-001: [Scenario Name]

**Given** [initial context or state]
**And** [additional context]
**When** [action or event occurs]
**Then** [expected outcome]
**And** [additional expected outcome]

**Example**:
Given: User is on login page
And: User has a valid account
When: User enters correct email and password
Then: User is redirected to dashboard
And: Welcome message displays user's name
And: Last login timestamp is shown
```

### Checklist Format

```markdown
## Acceptance Criteria: [Feature Name]

**Functional Criteria**:
- [ ] User can input email address
- [ ] User can input password
- [ ] User can click "Login" button
- [ ] System validates email format
- [ ] System authenticates credentials
- [ ] System creates session on success
- [ ] System redirects to dashboard on success

**Error Handling**:
- [ ] Invalid email format shows error message
- [ ] Wrong password shows "Invalid credentials" error
- [ ] Account lockout after 5 failed attempts
- [ ] Locked account shows unlock instructions

**Non-Functional**:
- [ ] Login completes in < 2 seconds
- [ ] Password is not visible when typing
- [ ] Session expires after 24 hours
- [ ] HTTPS enforced on login endpoint

**Accessibility**:
- [ ] Form is keyboard navigable
- [ ] Error messages announced by screen reader
- [ ] Labels associated with input fields
- [ ] Focus visible on all interactive elements
```

---

## Requirements Traceability Matrix

```markdown
# Requirements Traceability Matrix

| Req ID | Description | Priority | Status | Test Case | Implementation | Notes |
|--------|-------------|----------|--------|-----------|----------------|-------|
| FR-001 | User login | Must | Complete | TC-001, TC-002 | AuthController.login() | ✅ Done |
| FR-002 | Session mgmt | Must | In Progress | TC-003 | SessionMiddleware | 🔄 In Dev |
| FR-003 | Logout | Must | Not Started | TC-004 | AuthController.logout() | 📋 Planned |
| NFR-P001 | Response time | Must | Complete | PT-001 | N/A | ✅ Verified |
| NFR-SEC001 | Auth security | Must | Complete | ST-001, ST-002 | bcrypt, JWT | ✅ Done |

**Status Legend**:
- ✅ Complete: Requirement implemented and tested
- 🔄 In Progress: Requirement in development
- 📋 Planned: Requirement not started
- ⚠️ Blocked: Requirement blocked by dependency
- ❌ Cancelled: Requirement removed from scope
```

---

## User Story Template

```markdown
# User Story: [Story Title]

**Story ID**: US-[XXX]
**Epic**: [Parent epic if applicable]
**Priority**: [Must-Have / Should-Have / Nice-to-Have]
**Estimation**: [Story points or T-shirt size]

## Story

**As a** [type of user]
**I want** [to perform some action]
**So that** [I can achieve some goal or benefit]

## Background

[Context or business justification for this story]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Technical Notes

[Any technical considerations, constraints, or implementation notes]

## Dependencies

- [Dependency 1]
- [Dependency 2]

## Assumptions

- [Assumption 1]
- [Assumption 2]

## Out of Scope

- [What is explicitly NOT included in this story]

## Definition of Done

- [ ] Code implemented
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests written
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] QA testing passed
- [ ] Product owner approval

---

## Example: User Story

**Story ID**: US-042
**Epic**: User Authentication
**Priority**: Must-Have
**Estimation**: 5 story points

## Story

**As a** registered user
**I want** to reset my forgotten password via email
**So that** I can regain access to my account

## Background

Users frequently forget passwords and contact support for help. This self-service
password reset reduces support burden and improves user experience.

## Acceptance Criteria

- [ ] User can request password reset from login page
- [ ] System sends email with reset link to user's registered email
- [ ] Reset link expires after 1 hour
- [ ] User can set new password meeting complexity requirements
- [ ] Old password is invalidated after reset
- [ ] User receives confirmation email after successful reset

## Technical Notes

- Use JWT token in reset link (signed, 1-hour expiry)
- Reset tokens must be single-use (invalidate after use)
- Email template must be mobile-responsive
- Rate limit: 3 reset requests per hour per email

## Dependencies

- Email service must be configured
- Email templates must be created

## Assumptions

- User has access to registered email address
- Email delivery is reliable

## Out of Scope

- Two-factor authentication for reset (future story)
- SMS-based password reset (future story)
- Security questions

## Definition of Done

- [ ] Code implemented and passes linting
- [ ] Unit tests written (>80% coverage)
- [ ] Integration test for full reset flow
- [ ] Email template reviewed by design team
- [ ] Code reviewed and approved
- [ ] Documentation updated (API docs, user guide)
- [ ] Deployed to staging
- [ ] QA testing passed
- [ ] Product owner approval
- [ ] Deployed to production
```

---

## Requirements Gathering Checklist

Before completing Prepare phase requirements documentation:

**Functional Requirements**:
- [ ] All user stories identified
- [ ] Acceptance criteria defined for each story
- [ ] Edge cases and error scenarios documented
- [ ] Business rules captured
- [ ] Input/output specifications defined

**Non-Functional Requirements**:
- [ ] Performance targets specified (response time, throughput)
- [ ] Scalability requirements defined
- [ ] Security requirements identified
- [ ] Reliability targets set (uptime, MTTR)
- [ ] Usability standards defined
- [ ] Accessibility requirements captured (WCAG level)
- [ ] Compliance requirements identified (GDPR, HIPAA, etc.)

**Validation**:
- [ ] Requirements reviewed with stakeholders
- [ ] Acceptance criteria validated with product owner
- [ ] Technical feasibility confirmed with architects
- [ ] Dependencies identified
- [ ] Risks documented

**Documentation Quality**:
- [ ] Requirements are clear and unambiguous
- [ ] Requirements are testable
- [ ] Requirements are prioritized
- [ ] Requirements are traceable to business goals
- [ ] Templates used consistently

---

## Summary

Well-structured requirements prevent scope creep, missed expectations, and rework. By using standardized templates for functional requirements, non-functional requirements, and acceptance criteria, you create clear, testable specifications that guide the Architecture and Code phases.

**Key Principles**:
- **User-Centric**: Frame functional requirements as user stories
- **Testable**: Every requirement must have measurable acceptance criteria
- **Prioritized**: Distinguish must-haves from nice-to-haves
- **Specific**: Avoid vague terms like "fast" or "secure" (use metrics)
- **Traceable**: Link requirements to implementation and tests

**Remember**: Requirements evolve. Keep them updated as understanding grows, and version them in source control alongside code.
