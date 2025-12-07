# Test Coverage Reference

**Location**: `skills/pact-testing-patterns/references/test-coverage.md`

**Purpose**: Comprehensive guide to coverage metrics, analysis techniques, tools, and coverage-driven test design.

**Used by**: pact-test-engineer agent when analyzing test coverage and identifying gaps

**Related files**:
- `../SKILL.md` - Quick reference and decision tree
- `test-strategies.md` - Testing approaches and patterns
- `e2e-patterns.md` - End-to-end testing patterns

---

## Coverage Metrics Explained

### Line Coverage (Statement Coverage)

**Definition**: Percentage of code lines executed during test runs.

**Example**:
```javascript
function isAdult(age) {
  if (age >= 18) {           // Line 1
    return true;             // Line 2
  }
  return false;              // Line 3
}

// Test with 66% line coverage (2/3 lines)
test('returns true for age 18', () => {
  expect(isAdult(18)).toBe(true);
  // Executes Line 1 and Line 2, skips Line 3
});

// Add test for 100% line coverage
test('returns false for age 17', () => {
  expect(isAdult(17)).toBe(false);
  // Executes Line 1 and Line 3
});
```

**Pros**:
- Easy to understand and measure
- Quick sanity check for untested code

**Cons**:
- Can be gamed (execute line without meaningful assertions)
- Doesn't guarantee all logical paths are tested

**Target**: 70-80% for most projects

---

### Branch Coverage (Decision Coverage)

**Definition**: Percentage of conditional branches (if/else, switch, ternary) tested.

**Example**:
```javascript
function calculateDiscount(user, orderTotal) {
  if (user.isPremium) {                    // Branch 1: true/false
    if (orderTotal > 100) {                // Branch 2: true/false
      return orderTotal * 0.2;             // 20% discount
    }
    return orderTotal * 0.1;               // 10% discount
  }
  return 0;                                // No discount
}

// 50% branch coverage (2/4 branches)
test('premium user with $150 order gets 20% discount', () => {
  const user = { isPremium: true };
  expect(calculateDiscount(user, 150)).toBe(30);
  // Covers: Branch 1 (true), Branch 2 (true)
  // Misses: Branch 1 (false), Branch 2 (false)
});

// 100% branch coverage (4/4 branches)
// Add tests for:
// - Premium user, order <= $100 (Branch 1: true, Branch 2: false)
// - Non-premium user (Branch 1: false)
```

**Pros**:
- Catches missing test cases for conditional logic
- Better than line coverage for quality assurance

**Cons**:
- Doesn't test all combinations (condition coverage)
- Misses logic errors within branches

**Target**: 80-90% for critical modules

---

### Function Coverage

**Definition**: Percentage of functions/methods called during tests.

**Example**:
```javascript
// userService.js
export function getUser(id) { /* ... */ }      // Called in tests
export function updateUser(id) { /* ... */ }   // Called in tests
export function deleteUser(id) { /* ... */ }   // NOT called in tests
export function listUsers() { /* ... */ }      // Called in tests

// Function coverage: 75% (3/4 functions)
```

**Pros**:
- Identifies completely untested functions
- Good starting point for coverage improvement

**Cons**:
- Calling a function doesn't mean it's well-tested
- Doesn't measure quality of tests

**Target**: 80-95% (some utility functions may be untested intentionally)

---

### Mutation Coverage

**Definition**: Percentage of code mutations (changes) detected by tests.

**How It Works**:
1. Tool mutates your code (e.g., change `>` to `>=`, `&&` to `||`)
2. Re-run tests on mutated code
3. If tests still pass, mutation "survived" (indicates missing test case)
4. If tests fail, mutation "killed" (test caught the bug)

**Example**:
```javascript
function isEligibleForDiscount(age, isPremium) {
  return age >= 65 || isPremium;  // Original code
}

// Mutation 1: Change >= to >
function isEligibleForDiscount(age, isPremium) {
  return age > 65 || isPremium;   // Tests should catch this!
}

// Mutation 2: Change || to &&
function isEligibleForDiscount(age, isPremium) {
  return age >= 65 && isPremium;  // Tests should catch this!
}

// If 100% mutation coverage, tests will fail for both mutations
test('65-year-old is eligible', () => {
  expect(isEligibleForDiscount(65, false)).toBe(true);
  // Catches Mutation 1 (age > 65 would fail)
});

test('non-premium under 65 is not eligible', () => {
  expect(isEligibleForDiscount(30, false)).toBe(false);
  // Catches Mutation 2 (age >= 65 && isPremium would fail)
});
```

**Pros**:
- Best indicator of test quality (do tests actually catch bugs?)
- Finds weak tests that execute code but don't verify behavior

**Cons**:
- Very slow (N mutations × full test suite run time)
- Generates false positives (equivalent mutations)

**Target**: 60-80% (expensive to achieve 100%)

**Tools**: Stryker (JavaScript), Pitest (Java), mutmut (Python)

---

## Coverage Tools by Language/Framework

### JavaScript/TypeScript

#### Jest (Built-In Coverage)

```bash
# Generate coverage report
npm test -- --coverage

# Coverage with threshold enforcement
npm test -- --coverage --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'
```

**Output**:
```
File                | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
--------------------|---------|----------|---------|---------|-------------------
userService.js      |   95.45 |    88.89 |     100 |   95.24 | 23,45
paymentService.js   |   78.57 |    66.67 |   85.71 |   77.78 | 12,34,56-58
```

**Configuration** (`jest.config.js`):
```javascript
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/index.js', // Exclude entry point
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './src/critical/': {  // Higher threshold for critical code
      branches: 95,
      functions: 95,
      lines: 95,
    },
  },
};
```

---

#### c8 (V8 Coverage for Vitest, Node.js)

```bash
# Install
npm install -D c8

# Run tests with coverage
c8 npm test

# HTML report
c8 --reporter=html npm test
```

---

### Python

#### pytest-cov

```bash
# Install
pip install pytest-cov

# Run with coverage
pytest --cov=myapp tests/

# HTML report
pytest --cov=myapp --cov-report=html tests/

# Fail if coverage below threshold
pytest --cov=myapp --cov-fail-under=80 tests/
```

**Configuration** (`.coveragerc`):
```ini
[run]
source = myapp
omit =
    */tests/*
    */migrations/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

### Ruby

#### SimpleCov

```ruby
# spec/spec_helper.rb
require 'simplecov'
SimpleCov.start do
  add_filter '/spec/'
  add_filter '/config/'

  add_group 'Models', 'app/models'
  add_group 'Controllers', 'app/controllers'
  add_group 'Services', 'app/services'

  minimum_coverage 80
end
```

---

### Go

#### go test -cover

```bash
# Coverage for current package
go test -cover

# Coverage with detailed report
go test -coverprofile=coverage.out
go tool cover -html=coverage.out

# Coverage for all packages
go test ./... -coverprofile=coverage.out
```

---

## Coverage Analysis Techniques

### Identifying Coverage Gaps

#### Technique 1: Visual Coverage Reports

**HTML Coverage Reports** show uncovered lines in red:

```html
<!-- Generated HTML report -->
<div class="line uncovered">
  if (user.role === 'admin') {  // RED - not tested
</div>
<div class="line covered">
  if (user.role === 'user') {   // GREEN - tested
</div>
```

**Workflow**:
1. Generate HTML coverage report: `npm test -- --coverage`
2. Open `coverage/index.html` in browser
3. Navigate to files with low coverage
4. Identify red (uncovered) lines
5. Write tests to cover those lines

---

#### Technique 2: Coverage Diff (Only New Code)

**Problem**: Legacy code may have low coverage; focus on new code.

**Solution**: Coverage diff tools show coverage for changed files only.

**GitHub Action Example**:
```yaml
- name: Coverage Diff
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/coverage-final.json
    flags: unittests
    fail_ci_if_error: true
    diff_cov: true  # Only fail if new code is uncovered
```

**Manual Diff**:
```bash
# Coverage before changes
git checkout main
npm test -- --coverage
mv coverage/coverage-final.json coverage-main.json

# Coverage after changes
git checkout feature-branch
npm test -- --coverage
mv coverage/coverage-final.json coverage-feature.json

# Compare
npx coverage-diff coverage-main.json coverage-feature.json
```

---

### Prioritizing Coverage Improvements

#### Coverage Priority Matrix

| Code Type | Business Impact | Change Frequency | Priority | Target Coverage |
|-----------|----------------|------------------|----------|-----------------|
| Payment processing | Critical | Low | **P0** | 95%+ |
| Authentication | Critical | Medium | **P0** | 95%+ |
| Authorization | Critical | Low | **P0** | 90%+ |
| Core business logic | High | High | **P1** | 85%+ |
| API endpoints | High | Medium | **P1** | 80%+ |
| Utility functions | Medium | Low | **P2** | 70%+ |
| UI components | Medium | High | **P2** | 70%+ |
| Configuration | Low | Low | **P3** | 50%+ |
| Generated code | N/A | N/A | **Skip** | 0% OK |

**Prioritization Criteria**:
1. **Business Impact**: What's the cost of a bug in this code?
2. **Change Frequency**: How often does this code change? (High churn = higher risk)
3. **Complexity**: More complex code needs more tests

---

### Coverage Trend Tracking

**Monitor Coverage Over Time**:
```javascript
// coverage-trends.json
{
  "2025-01-01": { "lines": 65, "branches": 58 },
  "2025-02-01": { "lines": 70, "branches": 63 },
  "2025-03-01": { "lines": 75, "branches": 68 },
  "2025-04-01": { "lines": 78, "branches": 72 }
}
```

**Ratcheting Strategy**: Never decrease coverage.

```javascript
// jest.config.js
module.exports = {
  coverageThresholds: {
    global: {
      lines: 78,     // Current coverage (update as it improves)
      branches: 72,
    },
  },
};
```

**CI Enforcement**:
```yaml
# .github/workflows/test.yml
- name: Check coverage trend
  run: |
    PREV_COV=$(jq '.lines' coverage-baseline.json)
    CURR_COV=$(jq '.totals.lines.pct' coverage/coverage-summary.json)
    if (( $(echo "$CURR_COV < $PREV_COV" | bc -l) )); then
      echo "Coverage decreased from $PREV_COV% to $CURR_COV%"
      exit 1
    fi
```

---

## Coverage-Driven Test Design

### Technique 1: Coverage-Guided Test Writing

**Workflow**:
1. Write initial tests for happy path
2. Run coverage report
3. Identify uncovered branches
4. Write tests for uncovered branches
5. Repeat until coverage meets threshold

**Example**:
```javascript
// userService.js
export function deleteUser(userId, requestingUser) {
  if (!requestingUser.isAdmin) {
    throw new Error('Unauthorized');  // Branch 1
  }

  if (userId === requestingUser.id) {
    throw new Error('Cannot delete yourself');  // Branch 2
  }

  return db.users.delete(userId);  // Branch 3
}

// Test 1: Happy path
test('admin can delete other users', async () => {
  const admin = { id: '1', isAdmin: true };
  await deleteUser('2', admin);
  // Covers Branch 3 only
});

// Run coverage → see Branch 1 and Branch 2 uncovered

// Test 2: Cover Branch 1
test('non-admin cannot delete users', async () => {
  const user = { id: '1', isAdmin: false };
  await expect(deleteUser('2', user)).rejects.toThrow('Unauthorized');
});

// Test 3: Cover Branch 2
test('admin cannot delete themselves', async () => {
  const admin = { id: '1', isAdmin: true };
  await expect(deleteUser('1', admin)).rejects.toThrow('Cannot delete yourself');
});

// Coverage: 100% lines, 100% branches
```

---

### Technique 2: Boundary Value Analysis

**Identify Edge Cases from Coverage Gaps**:

```javascript
function getAgeCategory(age) {
  if (age < 0) {
    throw new Error('Invalid age');
  }
  if (age < 13) return 'child';
  if (age < 18) return 'teen';
  if (age < 65) return 'adult';
  return 'senior';
}

// Boundary test cases (all branches)
test('rejects negative age', () => {
  expect(() => getAgeCategory(-1)).toThrow('Invalid age');
});

test('categorizes 0 as child', () => {
  expect(getAgeCategory(0)).toBe('child');
});

test('categorizes 12 as child', () => {
  expect(getAgeCategory(12)).toBe('child');
});

test('categorizes 13 as teen', () => {
  expect(getAgeCategory(13)).toBe('teen');
});

test('categorizes 17 as teen', () => {
  expect(getAgeCategory(17)).toBe('teen');
});

test('categorizes 18 as adult', () => {
  expect(getAgeCategory(18)).toBe('adult');
});

test('categorizes 64 as adult', () => {
  expect(getAgeCategory(64)).toBe('adult');
});

test('categorizes 65 as senior', () => {
  expect(getAgeCategory(65)).toBe('senior');
});
```

**Boundary Values to Test**:
- Minimum valid value (0, empty array, null)
- Maximum valid value (MAX_INT, array length limit)
- Just below minimum (-1, null)
- Just above maximum (MAX_INT + 1, overflow)
- Typical valid value (middle of range)

---

## Coverage Anti-Patterns

### Anti-Pattern 1: Testing for Coverage, Not Quality

**Bad**:
```javascript
// 100% line coverage, but meaningless test
test('userService exists', () => {
  expect(userService).toBeDefined();
  userService.getUser('1');  // Execute code but no assertion
  userService.updateUser('1', {});
  userService.deleteUser('1');
  // No assertions, no verification - just executing code
});
```

**Good**:
```javascript
test('getUser returns user by ID', async () => {
  await db.users.insert({ id: '1', name: 'Alice' });
  const user = await userService.getUser('1');
  expect(user).toEqual({ id: '1', name: 'Alice' });
});

test('updateUser modifies user data', async () => {
  await db.users.insert({ id: '1', name: 'Alice' });
  await userService.updateUser('1', { name: 'Bob' });
  const user = await db.users.findById('1');
  expect(user.name).toBe('Bob');
});
```

**Why**: Coverage measures code execution, not correctness. Tests must verify behavior.

---

### Anti-Pattern 2: Over-Optimizing for 100% Coverage

**Problem**: Chasing 100% coverage wastes time on low-value code.

**Example**:
```javascript
// Auto-generated getter with no logic
class User {
  get fullName() {
    return `${this.firstName} ${this.lastName}`;  // Trivial, low value to test
  }
}

// Don't waste time testing this
test('fullName returns concatenated name', () => {
  const user = new User();
  user.firstName = 'Alice';
  user.lastName = 'Smith';
  expect(user.fullName).toBe('Alice Smith');
});
```

**Better**: Exclude trivial code from coverage or accept <100%.

```javascript
// jest.config.js
module.exports = {
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '.generated.js$',  // Exclude generated files
  ],
};
```

---

### Anti-Pattern 3: Ignoring Coverage on Legacy Code

**Problem**: "Legacy code has 20% coverage; we'll fix it someday."

**Solution**: Ratchet coverage for new code, incrementally improve legacy.

```javascript
// jest.config.js
module.exports = {
  coverageThresholds: {
    global: {
      lines: 60,  // Current overall coverage
    },
    './src/new-feature/': {  // New code must have high coverage
      lines: 85,
      branches: 80,
    },
  },
};
```

**Legacy Code Improvement Strategy**:
1. **Characterization Tests**: Write tests for current behavior (even if buggy)
2. **Refactor Safely**: With tests in place, refactor for testability
3. **Add Tests Incrementally**: Each bug fix adds regression test
4. **Track Progress**: Celebrate coverage improvements monthly

---

## Coverage in CI/CD

### Pull Request Coverage Checks

**Codecov GitHub Action**:
```yaml
name: Coverage Check

on: [pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          fail_ci_if_error: true
          # Fail PR if coverage drops by >2%
          flags: unittests
```

**Codecov PR Comments**:
```
Coverage: 78.5% (-1.2% compared to base)

Files with decreased coverage:
- src/userService.js: 85% → 78% (-7%)
- src/paymentService.js: 92% → 88% (-4%)

Files with increased coverage:
+ src/authService.js: 70% → 85% (+15%)
```

---

### Coverage Badges

**Add Badge to README.md**:
```markdown
[![codecov](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

**Display**:
![Coverage: 78%](https://img.shields.io/badge/coverage-78%25-yellow)

---

## Coverage vs Quality Trade-Off

**Coverage is Necessary But Not Sufficient**:

| Metric | What It Measures | What It Doesn't Measure |
|--------|-----------------|-------------------------|
| Line Coverage | Code was executed | Code was tested correctly |
| Branch Coverage | Conditional paths taken | Logical correctness |
| Function Coverage | Functions were called | Functions work as intended |
| Mutation Coverage | Tests catch code changes | Tests catch all bugs |

**High Coverage ≠ Bug-Free Code**:
```javascript
// 100% coverage, but wrong implementation
function sum(a, b) {
  return a - b;  // BUG: Should be +
}

test('sum adds numbers', () => {
  expect(sum(5, 3)).toBe(2);  // WRONG: Expects 2 instead of 8
  // 100% coverage, but test is incorrect
});
```

**Coverage + Code Review + Manual Testing = Confidence**

---

## Coverage Reporting Best Practices

### 1. Exclude Irrelevant Files

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',     // Exclude test files
    '!src/**/*.spec.{js,jsx,ts,tsx}',
    '!src/**/index.{js,jsx,ts,tsx}',      // Exclude barrel files
    '!src/**/*.d.ts',                     // Exclude type definitions
    '!src/generated/**',                  // Exclude generated code
    '!src/migrations/**',                 // Exclude DB migrations
  ],
};
```

---

### 2. Set Realistic Thresholds

**Don't Start with 90%**:
```javascript
// Bad: Set unrealistic threshold for existing project
coverageThresholds: {
  global: { lines: 90 }  // Current coverage: 45% - will fail
}

// Good: Set achievable threshold, ratchet up over time
coverageThresholds: {
  global: { lines: 50 }  // Slightly above current 45%
}
```

**Per-Module Thresholds**:
```javascript
coverageThresholds: {
  global: { lines: 70 },           // Overall target
  './src/auth/': { lines: 95 },    // Critical: high threshold
  './src/utils/': { lines: 85 },   // Important: medium threshold
  './src/ui/': { lines: 60 },      // UI: lower threshold (harder to test)
}
```

---

### 3. Automate Coverage Uploads

**Store Coverage History**:
```yaml
# .github/workflows/coverage.yml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3

- name: Store coverage artifact
  uses: actions/upload-artifact@v3
  with:
    name: coverage-report
    path: coverage/
    retention-days: 30
```

---

## Summary

**Coverage Analysis Workflow**:
1. **Run Tests with Coverage**: `npm test -- --coverage`
2. **Review HTML Report**: Identify files/branches with low coverage
3. **Prioritize Gaps**: Focus on critical code (auth, payments, core logic)
4. **Write Tests**: Use coverage-guided approach to cover uncovered branches
5. **Set Thresholds**: Enforce minimum coverage in CI/CD
6. **Ratchet Up**: Gradually increase thresholds as coverage improves
7. **Monitor Trends**: Track coverage over time, never let it decrease

**Key Metrics to Track**:
- **Line Coverage**: 70-80% baseline
- **Branch Coverage**: 80-90% for critical modules
- **Mutation Coverage**: 60-80% for highest-risk code

**Coverage Tools Quick Reference**:
- JavaScript: Jest (built-in), c8, nyc
- Python: pytest-cov, coverage.py
- Ruby: SimpleCov
- Go: go test -cover
- Java: JaCoCo
- Mutation Testing: Stryker (JS), Pitest (Java), mutmut (Python)

**Remember**: Coverage indicates what code is exercised, not whether it's correct. Combine with code review, manual testing, and user feedback for comprehensive quality assurance.

For test strategy selection, see `test-strategies.md`.
For E2E testing patterns, see `e2e-patterns.md`.

---

**Reference Version**: 1.0.0
**Last Updated**: 2025-12-04
