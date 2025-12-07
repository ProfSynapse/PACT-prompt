---
name: pact-testing-patterns
description: |
  TEST PHASE: Testing strategies, patterns, and quality assurance workflows.

  Provides test strategy frameworks, coverage guidelines, unit/integration/e2e patterns,
  performance testing approaches, and security testing checklists.

  Use when: designing test strategies, writing tests, evaluating coverage,
  planning QA workflows, implementing test automation.
allowed-tools:
  - Read
  - Bash
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Test"
  version: "1.0.0"
  primary-agent: "pact-test-engineer"
  updated: "2025-12-04"
  related-skills:
    - pact-backend-patterns
    - pact-frontend-patterns
    - pact-database-patterns
    - pact-security-patterns
---

# PACT Testing Patterns

## Overview

This skill provides comprehensive testing strategies, patterns, and quality assurance workflows for the PACT framework Test phase. It guides test design from unit tests to end-to-end scenarios, emphasizing meaningful coverage, test maintainability, and integration with the overall PACT workflow.

**Core Testing Philosophy**:
- **Test Pyramid**: Majority unit tests (fast, isolated), fewer integration tests, minimal E2E tests
- **Meaningful Coverage**: Focus on critical paths and edge cases, not arbitrary percentage targets
- **Test Maintainability**: Tests are code - apply same quality standards as production code
- **Test-Driven Mindset**: Design for testability from architecture phase onward

**When to Use This Skill**:
- Designing test strategies for new features
- Writing unit, integration, or E2E tests
- Evaluating test coverage and identifying gaps
- Debugging test failures or flaky tests
- Setting up test infrastructure and CI/CD integration
- Planning performance or security testing

---

## Quick Reference: Test Pyramid Strategy

### Available MCP Tools

- **sequential-thinking**: Test strategy design and complex test scenario planning

See "MCP Tools for Testing" section below for detailed usage guidance.

---

```
           /\
          /  \
         /E2E \ ← 10% - User journeys, critical paths
        /------\
       /        \
      /Integration\ ← 20% - Component interactions, API contracts
     /------------\
    /              \
   /  Unit Tests    \ ← 70% - Business logic, edge cases, error handling
  /------------------\
```

**Distribution Guidelines**:
- **Unit Tests (70%)**: Fast, isolated, test individual functions/methods/components
- **Integration Tests (20%)**: Test component interactions, database queries, API endpoints
- **E2E Tests (10%)**: Test complete user workflows, critical business processes

**Rationale**:
- Unit tests are fast, reliable, easy to debug - maximize these
- Integration tests catch interface issues - use selectively
- E2E tests are slow, brittle, expensive to maintain - minimize to critical paths

---

## Testing Workflow with Sequential Thinking

For complex testing decisions, use the MCP sequential-thinking tool:

**When to Use Sequential Thinking**:
1. **Test Strategy Design**: Determining which types of tests to write
2. **Coverage Analysis**: Identifying critical paths and edge cases to cover
3. **Flaky Test Debugging**: Reasoning through intermittent failures
4. **Performance Test Planning**: Designing load/stress test scenarios
5. **Security Test Design**: Threat modeling and security test case generation

**Example Invocation Pattern**:
```
When designing tests for authentication flow:
1. Use sequential-thinking to reason through:
   - What are the critical paths? (happy path, invalid credentials, token expiry)
   - What edge cases exist? (concurrent logins, rate limiting, session hijacking)
   - What failures modes are possible? (DB down, network timeout, crypto failure)
2. Map findings to test pyramid layers (unit vs integration vs E2E)
3. Prioritize tests by risk and likelihood
```

---

## Unit Testing Patterns

### AAA Pattern (Arrange-Act-Assert)

**Structure**:
```javascript
test('calculateDiscount returns 10% off for premium users', () => {
  // Arrange: Set up test data and dependencies
  const user = { type: 'premium', accountAge: 365 };
  const orderTotal = 100;

  // Act: Execute the function under test
  const discount = calculateDiscount(user, orderTotal);

  // Assert: Verify the outcome
  expect(discount).toBe(10);
});
```

**Guidelines**:
- Keep each section distinct and clear
- One assertion per test (or closely related assertions)
- Test names describe WHAT is being tested and EXPECTED outcome

---

### Test Isolation Principles

**Each Test Must Be Independent**:
```javascript
// BAD - Tests depend on execution order
let globalCounter = 0;

test('increments counter', () => {
  globalCounter++;
  expect(globalCounter).toBe(1); // Fails if tests run out of order
});

test('counter is now 2', () => {
  expect(globalCounter).toBe(2); // Depends on previous test
});

// GOOD - Each test is isolated
test('increments counter from zero', () => {
  let counter = 0;
  counter++;
  expect(counter).toBe(1);
});

test('increments counter from any value', () => {
  let counter = 42;
  counter++;
  expect(counter).toBe(43);
});
```

**Isolation Techniques**:
- Use `beforeEach()` to reset state before each test
- Avoid shared mutable state between tests
- Use test-specific fixtures/factories for data generation
- Mock external dependencies (databases, APIs, file system)

---

### Deterministic Test Design

**Tests Must Produce Same Result Every Time**:
```javascript
// BAD - Non-deterministic due to random data
test('generates unique user ID', () => {
  const id = generateUserId();
  expect(id).toBe('user_12345'); // Fails randomly if ID is random
});

// GOOD - Deterministic with mocked randomness
test('generates unique user ID', () => {
  jest.spyOn(Math, 'random').mockReturnValue(0.12345);
  const id = generateUserId();
  expect(id).toBe('user_12345');
});

// BAD - Time-dependent test
test('validates expiry date', () => {
  const token = { expiresAt: new Date('2025-01-01') };
  expect(isExpired(token)).toBe(true); // Fails after 2025-01-01
});

// GOOD - Time is controlled
test('validates expiry date', () => {
  const mockNow = new Date('2025-12-04');
  jest.spyOn(Date, 'now').mockReturnValue(mockNow.getTime());
  const token = { expiresAt: new Date('2025-01-01') };
  expect(isExpired(token)).toBe(true);
});
```

**Sources of Non-Determinism to Avoid**:
- Random number generators
- Current date/time
- Network requests
- File system operations
- Concurrent/async operations without proper synchronization

---

## Integration Testing Strategies

### API Endpoint Testing

**Test the Full Request-Response Cycle**:
```javascript
describe('POST /api/users', () => {
  let app, db;

  beforeAll(async () => {
    db = await setupTestDatabase();
    app = createApp(db);
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.truncate('users'); // Clean slate for each test
  });

  test('creates user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Alice', email: 'alice@example.com' })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      name: 'Alice',
      email: 'alice@example.com',
    });

    // Verify database state
    const user = await db.users.findByEmail('alice@example.com');
    expect(user).toBeDefined();
  });

  test('returns 400 for invalid email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Bob', email: 'invalid-email' })
      .expect(400);

    expect(response.body.error).toContain('email');
  });
});
```

**Integration Test Checklist**:
- [ ] Use test database (not production!)
- [ ] Clean state before each test (truncate tables, clear cache)
- [ ] Test authentication/authorization if applicable
- [ ] Verify response status codes, headers, body structure
- [ ] Confirm side effects (database writes, emails sent, events emitted)

---

### Database Integration Testing

**Test Queries and Transactions**:
```javascript
describe('UserRepository', () => {
  let db, userRepo;

  beforeEach(async () => {
    db = await setupTestDatabase();
    userRepo = new UserRepository(db);
    await seedTestData(db); // Load fixture data
  });

  test('findByEmail returns user when found', async () => {
    const user = await userRepo.findByEmail('test@example.com');
    expect(user).toMatchObject({
      email: 'test@example.com',
      name: expect.any(String),
    });
  });

  test('findByEmail returns null when not found', async () => {
    const user = await userRepo.findByEmail('nonexistent@example.com');
    expect(user).toBeNull();
  });

  test('transaction rolls back on error', async () => {
    await expect(async () => {
      await db.transaction(async (tx) => {
        await userRepo.create({ email: 'new@example.com' }, tx);
        throw new Error('Simulated error');
      });
    }).rejects.toThrow('Simulated error');

    // Verify user was NOT created
    const user = await userRepo.findByEmail('new@example.com');
    expect(user).toBeNull();
  });
});
```

---

## End-to-End Testing Design

### User Journey Coverage

**Test Critical Business Workflows**:
```javascript
describe('E2E: User Registration and Login', () => {
  let browser, page;

  beforeAll(async () => {
    browser = await puppeteer.launch();
  });

  afterAll(async () => {
    await browser.close();
  });

  beforeEach(async () => {
    page = await browser.newPage();
  });

  test('user can register, verify email, and login', async () => {
    // 1. Navigate to registration page
    await page.goto('http://localhost:3000/register');

    // 2. Fill out registration form
    await page.type('#name', 'Test User');
    await page.type('#email', 'test@example.com');
    await page.type('#password', 'SecurePass123!');
    await page.click('button[type="submit"]');

    // 3. Verify redirect to "check email" page
    await page.waitForNavigation();
    expect(page.url()).toContain('/verify-email');

    // 4. Simulate email verification (get token from test mail server)
    const verificationToken = await getTestEmailToken('test@example.com');
    await page.goto(`http://localhost:3000/verify?token=${verificationToken}`);

    // 5. Verify redirect to login page
    await page.waitForNavigation();
    expect(page.url()).toContain('/login');

    // 6. Login with credentials
    await page.type('#email', 'test@example.com');
    await page.type('#password', 'SecurePass123!');
    await page.click('button[type="submit"]');

    // 7. Verify successful login (redirect to dashboard)
    await page.waitForNavigation();
    expect(page.url()).toContain('/dashboard');
    expect(await page.textContent('h1')).toContain('Welcome, Test User');
  });
});
```

**E2E Test Guidelines**:
- Test complete user workflows, not individual features
- Focus on critical paths: registration, login, checkout, data submission
- Use realistic test data and scenarios
- Verify both happy paths AND error scenarios
- Run E2E tests in isolated environment (test database, test email server)
- Keep E2E test count minimal (slow and brittle)

---

## Coverage Guidelines

### Meaningful Coverage > 100% Coverage

**What to Prioritize**:
1. **Critical Business Logic**: Payment processing, authentication, authorization
2. **Edge Cases**: Boundary conditions, null/undefined handling, empty arrays
3. **Error Handling**: What happens when network fails, database is down, invalid input
4. **Integration Points**: APIs, database queries, external services
5. **Security-Sensitive Code**: Input validation, encryption, access control

**What NOT to Prioritize**:
- Simple getters/setters with no logic
- Framework boilerplate (generated code, configuration)
- UI presentation logic with no business logic
- Third-party library code

---

### Coverage Metrics Reference

**Line Coverage**: Percentage of code lines executed by tests
- **Target**: 70-80% for most projects
- **Interpretation**: Basic sanity check, but can be gamed with meaningless tests

**Branch Coverage**: Percentage of conditional branches (if/else) tested
- **Target**: 80-90% for critical modules
- **Interpretation**: Better than line coverage; ensures both true/false paths tested

**Function Coverage**: Percentage of functions called by tests
- **Target**: 80-95%
- **Interpretation**: Identifies completely untested functions

**Mutation Coverage**: Percentage of code mutations detected by tests
- **Target**: 60-80% (more expensive to measure)
- **Interpretation**: Best quality metric; tests actually catch bugs, not just execute code

**Recommended Baseline**:
- New projects: Start with 80% line coverage, 70% branch coverage
- Legacy projects: Incremental improvement; require coverage for new code
- Critical modules (auth, payment): 90%+ branch coverage with mutation testing

---

## Decision Tree: Which Tests to Write?

```
Is this business logic (not UI, not boilerplate)?
├─ Yes → Write unit tests (AAA pattern, isolated, mocked dependencies)
│         Coverage target: 80-90%
│
└─ No → Is this an integration point (API, database, external service)?
    ├─ Yes → Write integration tests (test database, API contracts)
    │         Coverage target: Critical paths only
    │
    └─ No → Is this a critical user workflow (registration, checkout, etc)?
        ├─ Yes → Write E2E test (full browser/app simulation)
        │         Coverage: 1-2 tests per critical workflow
        │
        └─ No → Skip testing (or write minimal smoke test)
```

**When to Load Detailed References**:

Need unit testing patterns and best practices?
→ **Read**: `references/test-strategies.md` for unit, integration, E2E approaches

Need coverage metrics and analysis guidance?
→ **Read**: `references/test-coverage.md` for coverage tools, thresholds, analysis

Need E2E testing patterns (Playwright, Cypress, Selenium)?
→ **Read**: `references/e2e-patterns.md` for browser automation, visual testing

Need contract testing for microservices and APIs?
→ **Read**: `references/contract-testing.md` for consumer-driven contracts, Pact framework, schema validation

Need test data management (fixtures, factories, seeders)?
→ **Read**: `references/test-strategies.md` section on test data

Need performance or security testing guidance?
→ **Read**: `references/test-strategies.md` sections on non-functional testing

---

## Test Data Management

### Fixtures vs Factories

**Fixtures**: Static test data files loaded before tests
```javascript
// fixtures/users.json
[
  { "id": "1", "name": "Alice", "email": "alice@example.com" },
  { "id": "2", "name": "Bob", "email": "bob@example.com" }
]

// In test
beforeEach(async () => {
  await db.loadFixtures('fixtures/users.json');
});
```

**When to Use Fixtures**:
- Reference data (countries, categories, roles)
- Small, stable datasets
- Data shared across many tests

**Factories**: Dynamic test data generators
```javascript
// factories/userFactory.js
const userFactory = {
  build: (overrides = {}) => ({
    id: faker.datatype.uuid(),
    name: faker.name.fullName(),
    email: faker.internet.email(),
    createdAt: new Date(),
    ...overrides,
  }),
};

// In test
const user = userFactory.build({ name: 'Specific Name' });
```

**When to Use Factories**:
- Unique data needed per test (avoid conflicts)
- Large, complex data structures
- Need to customize specific attributes

---

## Test Maintainability Principles

### DRY in Tests (But Not Too DRY)

**Balance Readability and Reusability**:
```javascript
// TOO DRY - Hard to understand what each test does
describe('UserService', () => {
  const testCases = [
    ['valid email', 'test@example.com', true],
    ['invalid email', 'not-an-email', false],
    // 20 more cases...
  ];

  testCases.forEach(([desc, email, expected]) => {
    test(desc, () => {
      expect(isValidEmail(email)).toBe(expected);
    });
  });
});

// GOOD - Clear, self-documenting tests
describe('UserService.isValidEmail', () => {
  test('returns true for valid email format', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
  });

  test('returns false for missing @ symbol', () => {
    expect(isValidEmail('notemail.com')).toBe(false);
  });

  test('returns false for missing domain', () => {
    expect(isValidEmail('test@')).toBe(false);
  });
});
```

**Guidelines**:
- Extract common setup to `beforeEach()`, but keep assertions in each test
- Use helper functions for complex setup, but keep test logic visible
- Prefer explicit over implicit - tests should be easy to understand in isolation

---

### Flaky Test Prevention

**Common Causes and Solutions**:

| Cause | Example | Solution |
|-------|---------|----------|
| Timing issues | `await waitForElement()` with short timeout | Use longer, explicit waits; retry logic |
| Test order dependency | Tests share global state | Isolate tests with `beforeEach()` cleanup |
| Non-deterministic data | Random IDs cause assertion failures | Mock randomness; use fixed test data |
| External service failures | API call fails intermittently | Mock external services; use contract testing |
| Async race conditions | Callback fires before assertion | Use proper async/await; avoid arbitrary sleeps |

**Flaky Test Debugging Process**:
1. Run test 100 times: `npm test -- --repeat 100`
2. Identify failure pattern (random vs specific conditions)
3. Add logging to capture state at failure point
4. Isolate: Does test fail alone? In different order?
5. Fix root cause (don't just increase timeouts)

---

## Self-Validation Checklist

Before completing Test phase, verify:

**Test Coverage**:
- [ ] Critical business logic has unit tests (80%+ coverage)
- [ ] Integration points have integration tests (API, database, external services)
- [ ] Critical user workflows have E2E tests (1-2 per workflow)
- [ ] Edge cases and error scenarios are tested
- [ ] Security requirements validated (see pact-security-patterns skill)

**Test Quality**:
- [ ] Tests are deterministic (no random failures)
- [ ] Tests are isolated (can run in any order)
- [ ] Tests are fast (unit tests < 100ms, integration < 1s)
- [ ] Test names clearly describe what is tested and expected outcome
- [ ] No skipped or commented-out tests without justification

**Test Maintenance**:
- [ ] Tests use AAA pattern (Arrange-Act-Assert)
- [ ] Common setup extracted to `beforeEach()`
- [ ] Test data uses fixtures or factories (not hardcoded magic values)
- [ ] Tests are organized by feature/component (not random)
- [ ] Test failures provide clear, actionable error messages

**Integration with PACT**:
- [ ] Tests validate architectural specifications from Architect phase
- [ ] Test results documented in `docs/testing/` or CI/CD output
- [ ] Coverage reports generated and reviewed
- [ ] Failed tests block deployment (unless explicitly overridden)
- [ ] Test suite integrated into CI/CD pipeline

---

## MCP Tools for Testing

This section provides guidance on WHEN and WHY to use MCP tools during the Test phase. See agent documentation for invocation syntax.

### Available MCP Tools

The following MCP tool enhances testing strategy and execution:
- **sequential-thinking**: Test strategy design and complex test scenario planning

---

### sequential-thinking

**Purpose**: Extended reasoning capability for complex testing decisions and scenario analysis

**When to use**:
- Designing test strategies for complex features with multiple integration points (e.g., payment flow with inventory, shipping, notifications, accounting integrations)
- Identifying critical test scenarios for high-risk features (e.g., authentication system with MFA, account recovery, session management edge cases)
- Debugging flaky tests with intermittent failures across multiple potential causes (e.g., race conditions, timing issues, test pollution, external service instability)
- Planning performance test scenarios for realistic user behaviors (e.g., e-commerce load testing with cart abandonment, concurrent checkouts, flash sale spikes)
- Designing security test cases from threat model analysis (e.g., API security testing covering OWASP Top 10 with domain-specific attack vectors)
- Evaluating test pyramid balance for specific project constraints (e.g., adjusting unit/integration/E2E ratio based on deployment frequency and team expertise)

**When NOT to use**:
- Writing straightforward unit tests for pure functions
- Following established test patterns for CRUD operations
- Simple test data setup with clear requirements
- Running existing test suites without modification
- Debugging tests with obvious failure messages pointing to specific code

**Value for testing phase**: Systematic reasoning identifies edge cases and failure modes that simple test checklists miss. Creates comprehensive test coverage for critical business workflows. Provides clear rationale for test strategy decisions to stakeholders.

**Integration approach**: Review implementation and architectural specifications → Identify complex testing decision or high-risk feature → Use sequential-thinking to enumerate scenarios, edge cases, and failure modes → Prioritize test cases by risk and impact → Implement tests with documented coverage rationale.

**See pact-test-engineer agent for invocation syntax and workflow integration.**

---

## Related Skills

This skill focuses on testing strategies and patterns. For complementary guidance:

- **pact-architecture-patterns**: System-level architectural context for testability design
- **pact-backend-patterns**: Backend API implementation details to inform integration tests
- **pact-frontend-patterns**: Frontend component patterns to inform UI testing
- **pact-database-patterns**: Database design to inform data integrity testing
- **pact-security-patterns**: Security testing strategies and OWASP validation

## Reference Files

Detailed reference documentation:
- **references/test-strategies.md**: Unit, integration, E2E testing approaches
- **references/test-coverage.md**: Coverage tools, thresholds, analysis
- **references/e2e-patterns.md**: Browser automation, visual testing
- **references/contract-testing.md**: Consumer-driven contracts, Pact framework, schema validation

## Templates

Ready-to-use templates for test planning:
- **templates/test-plan.md**: Test plan template with scope, cases, data requirements, acceptance criteria

## Examples

(Examples to be added in future iterations)

## Integration with PACT Workflow

### Test Phase Inputs

**From ARCHITECT Phase** (`docs/architecture/`):
- Component specifications (what to test)
- API contracts (integration test requirements)
- Data models (database test scenarios)
- Security requirements (security test cases)

**From CODE Phase** (implementation):
- Implemented features (what's ready to test)
- Code structure (how to organize test files)
- Edge cases discovered during coding (additional test cases)
- Performance characteristics (performance test baselines)

---

### Test Phase Outputs

**Test Suites and Results**:
- Unit test suite (70% of tests, fast execution)
- Integration test suite (20% of tests, moderate speed)
- E2E test suite (10% of tests, slow execution)
- Coverage reports (line, branch, function coverage)
- Test execution logs (pass/fail status, error messages)

**Quality Reports**:
- Coverage summary (meets thresholds?)
- Failed test analysis (root causes, fixes needed)
- Performance test results (latency, throughput, resource usage)
- Security test results (vulnerabilities found, severity)

**Back to CODE Phase (if tests fail)**:
- Bug reports with failing test details
- Regression test cases for fixed bugs
- Refactoring recommendations (if testability is poor)

**To PRODUCTION (if tests pass)**:
- Confidence level for deployment
- Smoke test suite for production validation
- Monitoring recommendations (what to watch post-deploy)

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-12-04
**Maintained by**: PACT Framework Team
