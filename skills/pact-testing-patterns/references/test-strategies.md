# Test Strategies Reference

**Location**: `skills/pact-testing-patterns/references/test-strategies.md`

**Purpose**: Comprehensive guide to unit testing, integration testing, E2E testing, test data management, performance testing, and security testing strategies.

**Used by**: pact-test-engineer agent, all coder agents when writing tests

**Related files**:
- `../SKILL.md` - Quick reference and decision tree
- `test-coverage.md` - Coverage metrics and analysis
- `e2e-patterns.md` - End-to-end testing patterns

---

## Unit Testing Strategies

### Philosophy and Principles

**Unit Test Characteristics**:
- **Fast**: Execute in milliseconds (< 100ms per test)
- **Isolated**: No dependencies on external systems (databases, APIs, file system)
- **Deterministic**: Same input always produces same output
- **Focused**: Test one behavior per test
- **Independent**: Can run in any order

**What to Unit Test**:
1. **Business Logic**: Calculations, validations, transformations
2. **Edge Cases**: Boundary values, null/undefined, empty collections
3. **Error Handling**: Invalid inputs, exception scenarios
4. **Conditional Logic**: All branches of if/else, switch statements
5. **State Transitions**: Object state changes over time

**What NOT to Unit Test**:
- Framework code (React rendering, Express middleware unless custom)
- Third-party libraries (already tested by maintainers)
- Simple getters/setters with no logic
- Configuration files (validated by schema)

---

### Test Organization Patterns

#### Mirror Source Structure

```
src/
├── services/
│   └── userService.js
└── utils/
    └── validation.js

tests/
├── services/
│   └── userService.test.js
└── utils/
    └── validation.test.js
```

**Benefits**:
- Easy to locate tests for any source file
- Refactoring moves tests alongside source
- Clear 1-to-1 correspondence

---

#### Feature-Based Organization

```
features/
├── authentication/
│   ├── login.js
│   ├── logout.js
│   └── __tests__/
│       ├── login.test.js
│       └── logout.test.js
└── payments/
    ├── checkout.js
    ├── refund.js
    └── __tests__/
        ├── checkout.test.js
        └── refund.test.js
```

**Benefits**:
- Tests live near implementation
- Feature-based code navigation
- Easy to delete entire feature (tests + code)

---

### Mocking and Stubbing Strategies

#### Dependency Injection for Testability

**Before (Hard to Test)**:
```javascript
// userService.js
import db from './database';

export async function getUserById(id) {
  return await db.users.findById(id); // Tightly coupled to real DB
}
```

**After (Easy to Test)**:
```javascript
// userService.js
export function createUserService(database) {
  return {
    async getUserById(id) {
      return await database.users.findById(id);
    },
  };
}

// Test can inject mock database
test('getUserById returns user from database', async () => {
  const mockDb = {
    users: {
      findById: jest.fn().mockResolvedValue({ id: '1', name: 'Alice' }),
    },
  };

  const userService = createUserService(mockDb);
  const user = await userService.getUserById('1');

  expect(user).toEqual({ id: '1', name: 'Alice' });
  expect(mockDb.users.findById).toHaveBeenCalledWith('1');
});
```

---

#### Mock vs Stub vs Spy

**Stub**: Returns predefined values, no behavior verification
```javascript
const dbStub = {
  findUser: () => ({ id: '1', name: 'Alice' }),
};
```

**Mock**: Returns predefined values AND verifies interactions
```javascript
const dbMock = {
  findUser: jest.fn().mockReturnValue({ id: '1', name: 'Alice' }),
};

// Later verify it was called
expect(dbMock.findUser).toHaveBeenCalledWith('1');
expect(dbMock.findUser).toHaveBeenCalledTimes(1);
```

**Spy**: Wraps real implementation, tracks calls
```javascript
const realService = new UserService();
const spy = jest.spyOn(realService, 'findUser');

// Real implementation runs, but we can verify calls
await realService.findUser('1');
expect(spy).toHaveBeenCalledWith('1');
```

**When to Use Each**:
- **Stub**: Simple tests, no need to verify interactions
- **Mock**: Verify correct method calls, arguments, call counts
- **Spy**: Test real implementation while tracking interactions

---

### Parameterized Testing

**Test Multiple Cases Efficiently**:
```javascript
describe('isValidEmail', () => {
  const testCases = [
    { input: 'test@example.com', expected: true, description: 'valid email' },
    { input: 'test@example.co.uk', expected: true, description: 'valid email with subdomain' },
    { input: 'test', expected: false, description: 'missing domain' },
    { input: '@example.com', expected: false, description: 'missing local part' },
    { input: 'test@', expected: false, description: 'missing domain' },
    { input: '', expected: false, description: 'empty string' },
    { input: null, expected: false, description: 'null value' },
  ];

  testCases.forEach(({ input, expected, description }) => {
    test(`returns ${expected} for ${description}`, () => {
      expect(isValidEmail(input)).toBe(expected);
    });
  });
});
```

**When to Use**:
- Testing validation logic with many edge cases
- Boundary value testing (0, -1, MAX_INT, etc.)
- Cross-browser/cross-platform compatibility tests

**When NOT to Use**:
- Tests require different setup/teardown
- Assertions are complex and test-specific
- Test readability suffers from abstraction

---

## Integration Testing Strategies

### Philosophy and Principles

**Integration Test Characteristics**:
- **Moderate Speed**: Slower than unit tests (< 1 second per test)
- **Real Dependencies**: Use test database, test APIs (not mocks)
- **Component Interaction**: Test how components work together
- **Contract Validation**: Ensure APIs/interfaces work as specified

**What to Integration Test**:
1. **API Endpoints**: Request/response contracts, status codes, error handling
2. **Database Operations**: Queries, transactions, constraints, migrations
3. **External Service Integration**: Third-party APIs (with test mode or mocks)
4. **Message Queues**: Producer/consumer interactions
5. **File System Operations**: Read/write files, uploads

---

### Test Database Strategies

#### Strategy 1: In-Memory Database (SQLite)

**Pros**:
- Extremely fast (no network I/O)
- No external dependencies
- Automatic cleanup (destroyed after tests)

**Cons**:
- May not match production database (SQL dialect differences)
- Limited feature support (triggers, stored procedures)

**When to Use**: Fast feedback for majority of tests, SQL-based applications

```javascript
import { createTestDatabase } from './testUtils';

describe('UserRepository', () => {
  let db, userRepo;

  beforeAll(async () => {
    db = await createTestDatabase(':memory:'); // SQLite in-memory
    await db.migrate(); // Run migrations
  });

  beforeEach(async () => {
    await db.truncate('users'); // Clean slate
  });

  afterAll(async () => {
    await db.close();
  });

  test('create inserts user into database', async () => {
    userRepo = new UserRepository(db);
    const user = await userRepo.create({ name: 'Alice', email: 'alice@example.com' });

    expect(user.id).toBeDefined();
    expect(user.name).toBe('Alice');

    // Verify in database
    const found = await db.query('SELECT * FROM users WHERE id = ?', [user.id]);
    expect(found.length).toBe(1);
  });
});
```

---

#### Strategy 2: Dockerized Test Database

**Pros**:
- Exact match to production database (Postgres, MySQL, etc.)
- Full feature support (triggers, stored procedures, replication)
- Isolated per test run (no shared state)

**Cons**:
- Slower (Docker startup, network I/O)
- Requires Docker installed
- More complex setup

**When to Use**: Database-specific features, critical production queries, CI/CD environments

```javascript
import { GenericContainer } from 'testcontainers';

describe('UserRepository (Postgres)', () => {
  let container, db, userRepo;

  beforeAll(async () => {
    // Start Postgres container
    container = await new GenericContainer('postgres:15')
      .withExposedPorts(5432)
      .withEnv('POSTGRES_PASSWORD', 'test')
      .start();

    const port = container.getMappedPort(5432);
    db = await connectToPostgres({ port, password: 'test' });
    await db.migrate();
  }, 30000); // Longer timeout for Docker startup

  afterAll(async () => {
    await db.close();
    await container.stop();
  });

  // Tests same as Strategy 1
});
```

---

### API Contract Testing

**Test Request/Response Schemas**:
```javascript
import request from 'supertest';
import { app } from '../app';

describe('POST /api/users', () => {
  test('returns 201 with created user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Alice', email: 'alice@example.com' })
      .expect(201)
      .expect('Content-Type', /json/);

    // Validate response schema
    expect(response.body).toMatchObject({
      id: expect.any(String),
      name: 'Alice',
      email: 'alice@example.com',
      createdAt: expect.any(String), // ISO 8601 timestamp
    });

    // Validate ISO 8601 format
    expect(new Date(response.body.createdAt).toISOString()).toBe(response.body.createdAt);
  });

  test('returns 400 for invalid email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Bob', email: 'not-an-email' })
      .expect(400);

    expect(response.body).toMatchObject({
      error: expect.objectContaining({
        field: 'email',
        message: expect.stringContaining('valid email'),
      }),
    });
  });

  test('returns 409 for duplicate email', async () => {
    // Create first user
    await request(app)
      .post('/api/users')
      .send({ name: 'Alice', email: 'alice@example.com' })
      .expect(201);

    // Try to create duplicate
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Alice2', email: 'alice@example.com' })
      .expect(409);

    expect(response.body.error.message).toContain('already exists');
  });
});
```

---

### External Service Integration

#### Strategy 1: Test Mode / Sandbox

Many services provide test modes (Stripe test keys, SendGrid sandbox, etc.):

```javascript
describe('PaymentService (Stripe Test Mode)', () => {
  let paymentService;

  beforeAll(() => {
    // Use Stripe test API key
    paymentService = new PaymentService(process.env.STRIPE_TEST_KEY);
  });

  test('creates payment intent', async () => {
    const intent = await paymentService.createIntent({
      amount: 1000,
      currency: 'usd',
    });

    expect(intent.id).toMatch(/^pi_test_/); // Test mode prefix
    expect(intent.amount).toBe(1000);
    expect(intent.status).toBe('requires_payment_method');
  });
});
```

**When to Use**: Service provides test mode, need to validate full integration

---

#### Strategy 2: HTTP Mocking (nock, msw)

For services without test mode or to avoid API rate limits:

```javascript
import nock from 'nock';

describe('WeatherService', () => {
  let weatherService;

  beforeAll(() => {
    weatherService = new WeatherService('fake-api-key');
  });

  afterEach(() => {
    nock.cleanAll();
  });

  test('fetches weather data', async () => {
    // Mock HTTP response
    nock('https://api.weather.com')
      .get('/current')
      .query({ city: 'London' })
      .reply(200, {
        temperature: 15,
        conditions: 'Cloudy',
      });

    const weather = await weatherService.getCurrent('London');

    expect(weather).toEqual({
      temperature: 15,
      conditions: 'Cloudy',
    });
  });

  test('handles API errors gracefully', async () => {
    nock('https://api.weather.com')
      .get('/current')
      .query({ city: 'Unknown' })
      .reply(404, { error: 'City not found' });

    await expect(weatherService.getCurrent('Unknown')).rejects.toThrow('City not found');
  });
});
```

**When to Use**: Avoid API costs, test error scenarios, offline testing

---

## Test Data Management

### Fixture Strategies

**Fixture Files**:
```yaml
# fixtures/users.yml
- id: user-1
  name: Alice Admin
  email: alice@example.com
  role: admin
  createdAt: 2025-01-01T00:00:00Z

- id: user-2
  name: Bob User
  email: bob@example.com
  role: user
  createdAt: 2025-01-02T00:00:00Z
```

**Loading Fixtures**:
```javascript
import fs from 'fs';
import yaml from 'yaml';

async function loadFixtures(db, fixturePath) {
  const content = fs.readFileSync(fixturePath, 'utf8');
  const data = yaml.parse(content);

  for (const user of data) {
    await db.users.insert(user);
  }
}

beforeEach(async () => {
  await db.truncate('users');
  await loadFixtures(db, 'fixtures/users.yml');
});
```

**When to Use Fixtures**:
- Reference data (countries, categories, roles)
- Complex relationships (user → posts → comments)
- Data shared across many tests
- Snapshot testing baseline

---

### Factory Strategies

**Factory Pattern with Faker**:
```javascript
import { faker } from '@faker-js/faker';

const userFactory = {
  build(overrides = {}) {
    return {
      id: faker.string.uuid(),
      name: faker.person.fullName(),
      email: faker.internet.email(),
      role: 'user',
      createdAt: faker.date.past(),
      ...overrides,
    };
  },

  buildMany(count, overrides = {}) {
    return Array.from({ length: count }, () => this.build(overrides));
  },

  async create(db, overrides = {}) {
    const user = this.build(overrides);
    return await db.users.insert(user);
  },

  async createMany(db, count, overrides = {}) {
    const users = this.buildMany(count, overrides);
    return await Promise.all(users.map((u) => db.users.insert(u)));
  },
};

// Usage in tests
test('admin can view all users', async () => {
  const admin = await userFactory.create(db, { role: 'admin' });
  const users = await userFactory.createMany(db, 10);

  const result = await adminService.listUsers(admin.id);
  expect(result.length).toBe(11); // 10 + admin
});
```

**When to Use Factories**:
- Each test needs unique data (avoid ID conflicts)
- Data doesn't need to be readable/debuggable
- Dynamic test data based on test context
- Performance testing (generate large datasets)

---

## Performance Testing

### Load Testing Strategy

**Objective**: Validate system handles expected traffic volume

**Tools**: Artillery, k6, JMeter, Locust

**Example (k6)**:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 10 },   // Stay at 10 users
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 50 },   // Stay at 50 users
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Error rate under 1%
  },
};

export default function () {
  const res = http.get('https://test.example.com/api/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1); // Think time between requests
}
```

**What to Measure**:
- **Response Time**: p50, p95, p99 latency
- **Throughput**: Requests per second
- **Error Rate**: Failed requests / total requests
- **Resource Utilization**: CPU, memory, database connections

**Performance Test Types**:
1. **Smoke Test**: Minimal load (1 user) to verify system works
2. **Load Test**: Expected production load (100 concurrent users)
3. **Stress Test**: Beyond expected load to find breaking point (500+ users)
4. **Spike Test**: Sudden traffic surge (0 → 1000 users in 1 minute)
5. **Soak Test**: Sustained load over long period (detect memory leaks)

---

## Security Testing

### Static Analysis (SAST)

**Tools**: ESLint security plugins, Bandit (Python), Brakeman (Ruby), SonarQube

**What to Detect**:
- Hardcoded secrets (API keys, passwords)
- SQL injection vulnerabilities
- XSS vulnerabilities (unescaped user input)
- Insecure dependencies (vulnerable libraries)
- Insecure configurations (weak crypto, debug mode in production)

**Example (npm audit)**:
```bash
npm audit --audit-level=moderate
```

---

### Dynamic Analysis (DAST)

**Tools**: OWASP ZAP, Burp Suite, Nikto

**What to Detect**:
- Authentication bypass
- Authorization flaws (privilege escalation)
- Session management issues
- Injection attacks (SQL, command, LDAP)
- Misconfigured CORS, CSP headers

**Example (OWASP ZAP Baseline Scan)**:
```bash
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://test.example.com \
  -r zap-report.html
```

---

### Security Test Cases

**Authentication Tests**:
- [ ] Password requirements enforced (length, complexity)
- [ ] Account lockout after N failed attempts
- [ ] Password reset token expires after 1 hour
- [ ] Multi-factor authentication works correctly
- [ ] Session expires after inactivity

**Authorization Tests**:
- [ ] User cannot access another user's data
- [ ] Admin-only endpoints reject non-admin users
- [ ] API returns 403 for unauthorized access (not 404 to avoid enumeration)

**Input Validation Tests**:
- [ ] SQL injection blocked (`'; DROP TABLE users; --`)
- [ ] XSS blocked (`<script>alert('XSS')</script>`)
- [ ] Path traversal blocked (`../../etc/passwd`)
- [ ] File upload validates type and size
- [ ] JSON payloads reject invalid schema

**For comprehensive security testing guidance, consult the `pact-security-patterns` skill.**

---

## Test Execution Strategies

### Continuous Integration (CI)

**Test Execution Pipeline**:
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test -- --testPathPattern=unit

      - name: Run integration tests
        run: npm test -- --testPathPattern=integration
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/test

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          BASE_URL: http://localhost:3000

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Optimization Strategies**:
- Run unit tests first (fast feedback)
- Parallelize integration tests across multiple workers
- Run E2E tests only on main branch or PR merge
- Cache dependencies (`node_modules`, Docker layers)
- Fail fast on first error (don't run all tests if unit tests fail)

---

### Test Execution Order

**Fastest to Slowest**:
1. **Unit Tests**: Run on every commit, pre-commit hook
2. **Integration Tests**: Run on every push to branch
3. **E2E Tests**: Run on PR merge, nightly builds
4. **Performance Tests**: Run weekly, before major releases
5. **Security Scans**: Run nightly, on dependency updates

---

## Common Testing Pitfalls and Solutions

### Pitfall 1: Testing Implementation Details

**Bad**:
```javascript
test('component has correct state after click', () => {
  const component = new MyComponent();
  component.handleClick();
  expect(component.state.count).toBe(1); // Tests internal state
});
```

**Good**:
```javascript
test('displays incremented count after click', () => {
  render(<MyComponent />);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText('Count: 1')).toBeInTheDocument(); // Tests visible outcome
});
```

**Why**: Tests should verify behavior (what users see), not implementation (how it works internally). Testing implementation details makes tests brittle (break on refactoring).

---

### Pitfall 2: Over-Mocking

**Bad**:
```javascript
test('userService.getUser returns user', async () => {
  const mockDb = { findUser: jest.fn().mockResolvedValue({ id: '1' }) };
  const mockCache = { get: jest.fn().mockResolvedValue(null) };
  const mockLogger = { log: jest.fn() };
  const mockMetrics = { increment: jest.fn() };

  const userService = new UserService(mockDb, mockCache, mockLogger, mockMetrics);
  const user = await userService.getUser('1');

  expect(user).toEqual({ id: '1' });
  // Test just verifies mock returns what we told it to return
});
```

**Good**:
```javascript
test('userService.getUser returns user from database', async () => {
  const db = await createTestDatabase();
  await db.users.insert({ id: '1', name: 'Alice' });

  const userService = new UserService(db);
  const user = await userService.getUser('1');

  expect(user).toEqual({ id: '1', name: 'Alice' });
  // Test verifies actual database interaction
});
```

**Why**: Over-mocking tests nothing real. Use integration tests for complex interactions.

---

### Pitfall 3: Flaky Tests

**Common Causes**:
1. **Timing issues**: `setTimeout`, `waitFor` with short timeouts
2. **Test order dependency**: Tests modify shared global state
3. **Non-determinism**: Random data, current time, network variability
4. **Async race conditions**: Callbacks fire before assertions

**Solutions**:
- Mock time: `jest.useFakeTimers()`
- Isolate tests: `beforeEach()` cleanup
- Mock randomness: `jest.spyOn(Math, 'random')`
- Use proper async/await, avoid arbitrary `sleep()`

---

## Recommended Testing Tools by Language/Framework

### JavaScript/TypeScript
- **Unit/Integration**: Jest, Vitest
- **E2E**: Playwright, Cypress
- **API Testing**: Supertest
- **Mocking**: jest.mock(), nock, msw
- **Fixtures**: faker, factory-bot

### Python
- **Unit/Integration**: pytest, unittest
- **E2E**: Selenium, Playwright
- **API Testing**: requests, httpx
- **Mocking**: unittest.mock, responses
- **Fixtures**: factory_boy, Faker

### Ruby
- **Unit/Integration**: RSpec, Minitest
- **E2E**: Capybara, Selenium
- **API Testing**: rack-test
- **Mocking**: rspec-mocks, webmock
- **Fixtures**: FactoryBot, Faker

### Go
- **Unit/Integration**: testing package, testify
- **E2E**: Selenium, chromedp
- **API Testing**: httptest
- **Mocking**: gomock, testify/mock
- **Fixtures**: go-faker, gofakeit

---

## Summary

**Testing Strategy Checklist**:
- [ ] Follow test pyramid: 70% unit, 20% integration, 10% E2E
- [ ] Unit tests are fast, isolated, deterministic
- [ ] Integration tests use test database or mocked external services
- [ ] E2E tests cover critical user workflows only
- [ ] Test data uses fixtures (stable) or factories (dynamic)
- [ ] Performance tests validate latency and throughput SLAs
- [ ] Security tests validate OWASP Top 10 mitigations
- [ ] Tests run in CI on every commit/PR
- [ ] Coverage meets project thresholds (70-80% line coverage)
- [ ] Tests are maintainable: clear names, DRY setup, no flakiness

For specific coverage analysis techniques, see `test-coverage.md`.
For detailed E2E testing patterns, see `e2e-patterns.md`.
For security testing checklists, consult the `pact-security-patterns` skill.

---

**Reference Version**: 1.0.0
**Last Updated**: 2025-12-04
