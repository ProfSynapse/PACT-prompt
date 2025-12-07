# Test Plan Template

## Feature: [Feature Name]

### Overview
- **Component**: [Component being tested]
- **Type**: [Unit | Integration | E2E | Performance]
- **Priority**: [P0 | P1 | P2]
- **Owner**: [Team/Person]

---

## Test Scope

### In Scope
- [ ] [Functionality 1]
- [ ] [Functionality 2]
- [ ] [Functionality 3]

### Out of Scope
- [Explicitly excluded items]
- [Dependencies tested elsewhere]

---

## Test Cases

### Happy Path Tests

| ID | Description | Preconditions | Steps | Expected Result |
|----|-------------|---------------|-------|-----------------|
| TC-001 | [Test name] | [Setup needed] | 1. [Step] 2. [Step] | [Expected outcome] |
| TC-002 | [Test name] | [Setup needed] | 1. [Step] 2. [Step] | [Expected outcome] |

### Edge Cases

| ID | Description | Preconditions | Steps | Expected Result |
|----|-------------|---------------|-------|-----------------|
| TC-101 | Empty input | None | Submit empty form | Validation error shown |
| TC-102 | Max length | None | Enter max chars + 1 | Input rejected |
| TC-103 | Special chars | None | Enter <script> tag | Input sanitized |

### Error Scenarios

| ID | Description | Trigger | Expected Behavior |
|----|-------------|---------|-------------------|
| TC-201 | Network failure | Disconnect network | Retry with backoff, show error |
| TC-202 | Timeout | Delay > 30s | Cancel request, show timeout error |
| TC-203 | Invalid response | Return malformed JSON | Log error, show generic message |

### Security Tests

| ID | Description | Attack Vector | Expected Defense |
|----|-------------|---------------|------------------|
| TC-301 | SQL Injection | `'; DROP TABLE--` | Query parameterized, no injection |
| TC-302 | XSS | `<script>alert(1)</script>` | Output encoded |
| TC-303 | CSRF | Cross-origin request | Token validated, request rejected |

---

## Test Data

### Required Fixtures
```
fixtures/
├── users/
│   ├── valid-user.json
│   └── admin-user.json
├── [resource]/
│   ├── valid-[resource].json
│   └── invalid-[resource].json
└── mocks/
    └── external-service-response.json
```

### Data Requirements
- [ ] Test database seeded
- [ ] External service mocks configured
- [ ] Test credentials available

---

## Environment Requirements

- [ ] Test environment accessible
- [ ] Test data loaded
- [ ] Feature flags configured
- [ ] Mock services running

---

## Acceptance Criteria

- [ ] All P0 test cases pass
- [ ] Code coverage >= [X]%
- [ ] No critical/high severity bugs
- [ ] Performance within SLA
- [ ] Security scan clean

---
*Generated from pact-testing-patterns skill template*
