# End-to-End Testing Patterns Reference

**Location**: `skills/pact-testing-patterns/references/e2e-patterns.md`

**Purpose**: Comprehensive guide to E2E testing patterns, browser automation, visual testing, and E2E test infrastructure.

**Used by**: pact-test-engineer agent when designing and implementing end-to-end test suites

**Related files**:
- `../SKILL.md` - Quick reference and decision tree
- `test-strategies.md` - Overall testing approaches
- `test-coverage.md` - Coverage metrics and analysis

---

## E2E Testing Philosophy

### When to Write E2E Tests

**Critical User Workflows**:
- User registration and login
- Checkout and payment processing
- Data submission and validation
- Multi-step wizards or forms
- Critical business processes (order fulfillment, approvals)

**NOT for E2E Testing**:
- Individual UI components (use component tests)
- API endpoints (use integration tests)
- Business logic (use unit tests)
- Edge cases and error scenarios (too slow to test all combinations)

**E2E Test Distribution**: 10% of total test suite (test pyramid)

---

### E2E Test Characteristics

**Slow**: 10-60 seconds per test (browser startup, navigation, rendering)
**Brittle**: Sensitive to UI changes, timing issues, network variability
**Expensive**: Require browser automation infrastructure, cloud testing services
**High Value**: Catch integration issues that unit/integration tests miss

**Design Principles**:
- Test complete user journeys, not individual features
- Keep test count minimal (5-15 E2E tests for most apps)
- Focus on happy paths and critical failures
- Run in isolated environment (test database, test payment gateway)

---

## Browser Automation Tools

### Playwright (Recommended)

**Why Playwright**:
- Cross-browser support (Chrome, Firefox, Safari, Edge)
- Auto-wait for elements (no explicit waits needed)
- Fast execution (parallel browser contexts)
- Network interception (mock APIs, capture requests)
- Screenshots and videos on failure

**Installation**:
```bash
npm install -D @playwright/test
npx playwright install  # Download browsers
```

**Basic Example**:
```javascript
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  // Navigate to login page
  await page.goto('https://example.com/login');

  // Fill form
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');

  // Submit form
  await page.click('button[type="submit"]');

  // Wait for navigation
  await page.waitForURL('**/dashboard');

  // Verify logged in
  await expect(page.locator('h1')).toHaveText('Welcome, Test User');
});
```

---

### Cypress

**Why Cypress**:
- Developer-friendly API
- Time-travel debugging (see app state at each step)
- Automatic screenshots and videos
- Built-in retry logic for flaky tests

**Installation**:
```bash
npm install -D cypress
npx cypress open
```

**Example**:
```javascript
describe('Login Flow', () => {
  it('allows user to login', () => {
    cy.visit('/login');
    cy.get('[name="email"]').type('test@example.com');
    cy.get('[name="password"]').type('SecurePass123!');
    cy.get('button[type="submit"]').click();

    // Assertions
    cy.url().should('include', '/dashboard');
    cy.get('h1').should('contain', 'Welcome, Test User');
  });
});
```

**Limitations**:
- No cross-browser support (Chromium only in free version)
- Runs in browser context (different from Selenium/Playwright)

---

### Selenium WebDriver (Legacy)

**When to Use**: Legacy projects, specific browser requirements

**Example**:
```javascript
const { Builder, By, until } = require('selenium-webdriver');

(async function example() {
  const driver = await new Builder().forBrowser('chrome').build();

  try {
    await driver.get('https://example.com/login');
    await driver.findElement(By.name('email')).sendKeys('test@example.com');
    await driver.findElement(By.name('password')).sendKeys('SecurePass123!');
    await driver.findElement(By.css('button[type="submit"]')).click();

    await driver.wait(until.urlContains('/dashboard'), 5000);

    const heading = await driver.findElement(By.css('h1')).getText();
    console.assert(heading === 'Welcome, Test User');
  } finally {
    await driver.quit();
  }
})();
```

**Note**: Playwright is recommended over Selenium for new projects (better API, faster).

---

## E2E Test Patterns

### Page Object Model (POM)

**Problem**: Duplicated locators across tests, brittle selectors

**Solution**: Encapsulate page interactions in Page Objects

**Bad (No POM)**:
```javascript
test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');  // Duplicated selector
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
});

test('login validates email format', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'invalid-email');  // Same selector duplicated
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
});
```

**Good (With POM)**:
```javascript
// pages/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('[name="email"]');
    this.passwordInput = page.locator('[name="password"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}

// login.spec.js
import { LoginPage } from './pages/LoginPage';

test('user can login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('test@example.com', 'SecurePass123!');
  await expect(page).toHaveURL(/.*dashboard/);
});

test('login validates email format', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('invalid-email', 'SecurePass123!');
  const error = await loginPage.getErrorMessage();
  expect(error).toContain('valid email');
});
```

**Benefits**:
- **DRY**: Selectors defined once, reused across tests
- **Maintainability**: UI changes require updating one file
- **Readability**: Tests read like user actions, not technical details

---

### Test Data Builders

**Problem**: Test setup is verbose and repetitive

**Solution**: Builder pattern for test data

```javascript
// builders/UserBuilder.js
export class UserBuilder {
  constructor() {
    this.data = {
      email: 'test@example.com',
      password: 'SecurePass123!',
      name: 'Test User',
      role: 'user',
    };
  }

  withEmail(email) {
    this.data.email = email;
    return this;
  }

  withRole(role) {
    this.data.role = role;
    return this;
  }

  asAdmin() {
    this.data.role = 'admin';
    return this;
  }

  build() {
    return this.data;
  }

  async create(api) {
    const response = await api.post('/api/users', this.data);
    return response.data;
  }
}

// Usage in tests
test('admin can access admin panel', async ({ page, request }) => {
  const admin = await new UserBuilder()
    .asAdmin()
    .withEmail('admin@example.com')
    .create(request);

  // Login and verify admin access
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login(admin.email, admin.password);
  await expect(page.locator('.admin-panel')).toBeVisible();
});
```

---

### Test Hooks for Setup/Teardown

**beforeEach/afterEach Pattern**:
```javascript
import { test, expect } from '@playwright/test';

test.describe('User Dashboard', () => {
  let loginPage, dashboardPage;

  test.beforeEach(async ({ page, request }) => {
    // Create test user
    const user = await new UserBuilder().create(request);

    // Login
    loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);

    // Navigate to dashboard
    dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
  });

  test.afterEach(async ({ request }) => {
    // Cleanup: Delete test user (optional, if database persists)
    await request.delete('/api/users/test@example.com');
  });

  test('displays user profile', async () => {
    await expect(dashboardPage.userName).toHaveText('Test User');
  });

  test('allows editing profile', async () => {
    await dashboardPage.editProfile({ name: 'Updated Name' });
    await expect(dashboardPage.userName).toHaveText('Updated Name');
  });
});
```

---

## Handling Common E2E Challenges

### Waiting for Elements

**Auto-Wait (Playwright)**:
```javascript
// Playwright automatically waits for element to be visible, enabled, stable
await page.click('button');  // Waits up to 30s for button to be clickable
```

**Explicit Waits**:
```javascript
// Wait for specific element
await page.waitForSelector('.loading-spinner', { state: 'hidden' });

// Wait for URL change
await page.waitForURL('**/dashboard');

// Wait for network request
await page.waitForResponse((response) =>
  response.url().includes('/api/users') && response.status() === 200
);

// Wait for timeout (last resort, avoid if possible)
await page.waitForTimeout(1000);  // Wait 1 second (brittle!)
```

---

### Flaky Test Prevention

**Common Causes of Flakiness**:
1. **Race Conditions**: Click before element is ready
2. **Network Variability**: API response times fluctuate
3. **Animation Delays**: Element moves during click
4. **Non-Deterministic Data**: Random IDs, timestamps

**Solutions**:

#### 1. Use Robust Selectors

**Bad**:
```javascript
await page.click('button:nth-child(3)');  // Breaks if button order changes
await page.click('.btn.btn-primary');     // Non-unique selector
```

**Good**:
```javascript
await page.click('[data-testid="submit-button"]');  // Stable test ID
await page.click('button:has-text("Submit")');      // Text-based (resilient to styling)
await page.getByRole('button', { name: 'Submit' }).click();  // Accessibility-based (best)
```

---

#### 2. Wait for Specific Conditions

**Bad**:
```javascript
await page.click('button');
await page.waitForTimeout(2000);  // Arbitrary wait
expect(await page.textContent('.message')).toBe('Success');
```

**Good**:
```javascript
await page.click('button');
await page.waitForSelector('.message', { state: 'visible' });
await expect(page.locator('.message')).toHaveText('Success');
```

---

#### 3. Mock Network Requests

**Reduce Variability by Mocking APIs**:
```javascript
test('displays user data', async ({ page }) => {
  // Mock API response
  await page.route('**/api/users/123', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: '123', name: 'Alice' }),
    });
  });

  await page.goto('/users/123');
  await expect(page.locator('.user-name')).toHaveText('Alice');
});
```

---

### Testing Authentication

**Strategy 1: Login Before Each Test**:
```javascript
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
});
```

**Problem**: Slow (login every test)

---

**Strategy 2: Reuse Authentication State**:
```javascript
// global-setup.js (run once before all tests)
import { chromium } from '@playwright/test';

async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Login
  await page.goto('https://example.com/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');

  // Save authentication state (cookies, localStorage)
  await page.context().storageState({ path: 'auth.json' });

  await browser.close();
}

export default globalSetup;

// playwright.config.js
module.exports = {
  globalSetup: './global-setup.js',
  use: {
    storageState: 'auth.json',  // Reuse login state
  },
};

// Tests now start logged in
test('dashboard loads', async ({ page }) => {
  await page.goto('/dashboard');  // Already authenticated!
  await expect(page.locator('h1')).toHaveText('Welcome');
});
```

**Benefits**: Faster (login once, reuse across tests)

---

### Testing File Uploads

```javascript
test('user can upload profile picture', async ({ page }) => {
  await page.goto('/profile');

  // Select file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('./fixtures/avatar.png');

  // Submit
  await page.click('button:has-text("Upload")');

  // Verify upload
  await expect(page.locator('.success-message')).toHaveText('Upload successful');
  await expect(page.locator('.profile-picture')).toHaveAttribute(
    'src',
    /avatar\.png$/
  );
});
```

---

### Testing Forms with Validation

```javascript
test('form validates required fields', async ({ page }) => {
  await page.goto('/register');

  // Try to submit empty form
  await page.click('button[type="submit"]');

  // Verify validation errors
  await expect(page.locator('.error-message')).toHaveCount(3);  // Name, email, password
  await expect(page.locator('[name="email"] + .error')).toHaveText(
    'Email is required'
  );

  // Fill valid data
  await page.fill('[name="name"]', 'Alice');
  await page.fill('[name="email"]', 'alice@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');

  // Errors should disappear
  await expect(page.locator('.error-message')).toHaveCount(0);

  // Submit succeeds
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
});
```

---

## Visual Regression Testing

### Screenshot Comparison

**Playwright Visual Testing**:
```javascript
test('homepage looks correct', async ({ page }) => {
  await page.goto('/');

  // Take screenshot and compare to baseline
  await expect(page).toHaveScreenshot('homepage.png');
  // First run: Creates baseline (homepage.png)
  // Subsequent runs: Compares to baseline, fails if different
});

test('modal appears correctly', async ({ page }) => {
  await page.goto('/');
  await page.click('button:has-text("Open Modal")');

  // Screenshot specific element
  const modal = page.locator('.modal');
  await expect(modal).toHaveScreenshot('modal.png');
});
```

**Updating Baselines**:
```bash
# Regenerate baselines (after intentional UI changes)
npx playwright test --update-snapshots
```

---

### Pixel Diff Tools

**Percy (Cloud Service)**:
```javascript
import percySnapshot from '@percy/playwright';

test('homepage visual test', async ({ page }) => {
  await page.goto('/');
  await percySnapshot(page, 'Homepage');
  // Percy compares against previous snapshots in cloud
});
```

**Benefits**: Cross-browser visual testing, automatic baseline management

---

## Mobile and Responsive Testing

### Emulate Mobile Devices

**Playwright**:
```javascript
import { test, devices } from '@playwright/test';

test.use(devices['iPhone 12']);  // Emulate iPhone 12

test('mobile navigation works', async ({ page }) => {
  await page.goto('/');

  // Hamburger menu should be visible on mobile
  await expect(page.locator('.hamburger-menu')).toBeVisible();

  // Desktop navigation should be hidden
  await expect(page.locator('.desktop-nav')).not.toBeVisible();
});
```

**Test Multiple Devices**:
```javascript
const devices = ['iPhone 12', 'Pixel 5', 'iPad Pro'];

devices.forEach((deviceName) => {
  test.describe(deviceName, () => {
    test.use(devices[deviceName]);

    test('layout is responsive', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveScreenshot(`${deviceName}-layout.png`);
    });
  });
});
```

---

## E2E Test Infrastructure

### Running Tests in CI/CD

**GitHub Actions Example**:
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

---

### Parallel Test Execution

**Playwright (Built-In)**:
```javascript
// playwright.config.js
module.exports = {
  workers: 4,  // Run 4 tests in parallel
  use: {
    trace: 'retain-on-failure',  // Debug traces only on failure
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
};
```

**Sharding (Distribute Across Machines)**:
```bash
# Run on 3 machines, this is shard 1 of 3
npx playwright test --shard=1/3

# Run on 3 machines, this is shard 2 of 3
npx playwright test --shard=2/3

# Run on 3 machines, this is shard 3 of 3
npx playwright test --shard=3/3
```

---

### Test Environment Isolation

**Dockerized Test Environment**:
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://test:test@db:5432/test
      NODE_ENV: test

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test

  e2e-tests:
    image: mcr.microsoft.com/playwright:latest
    depends_on:
      - app
    volumes:
      - ./tests:/tests
    command: npx playwright test
    environment:
      BASE_URL: http://app:3000
```

**Run Tests**:
```bash
docker-compose -f docker-compose.test.yml up --exit-code-from e2e-tests
```

---

## E2E Testing Best Practices

### 1. Keep Tests Independent

**Each Test Should**:
- Set up own data (don't rely on previous tests)
- Clean up after itself (delete created data)
- Run successfully in any order

**Bad**:
```javascript
test('create user', async ({ page }) => {
  // Creates user 'alice@example.com'
});

test('login as user', async ({ page }) => {
  // Assumes 'alice@example.com' exists from previous test
});
```

**Good**:
```javascript
test('create and login as user', async ({ page, request }) => {
  // Create user
  await request.post('/api/users', {
    data: { email: 'alice@example.com', password: 'pass' },
  });

  // Login
  // ...

  // Cleanup
  await request.delete('/api/users/alice@example.com');
});
```

---

### 2. Use Test IDs, Not Brittle Selectors

**Bad**:
```javascript
await page.click('.container > div:nth-child(2) > button.primary');
```

**Good**:
```javascript
await page.click('[data-testid="submit-button"]');

// Or accessibility-based
await page.getByRole('button', { name: 'Submit' }).click();
```

---

### 3. Test User Journeys, Not Individual Features

**Bad (Too Granular)**:
```javascript
test('login button exists', async ({ page }) => { /* ... */ });
test('login form validates email', async ({ page }) => { /* ... */ });
test('login form validates password', async ({ page }) => { /* ... */ });
test('login submits to API', async ({ page }) => { /* ... */ });
test('login redirects to dashboard', async ({ page }) => { /* ... */ });
```

**Good (Complete Journey)**:
```javascript
test('user can register, verify email, and login', async ({ page, request }) => {
  // 1. Register
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');

  // 2. Verify email (simulate)
  const token = await getVerificationToken('test@example.com');
  await page.goto(`/verify?token=${token}`);

  // 3. Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');

  // 4. Verify logged in
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.locator('h1')).toHaveText('Welcome');
});
```

---

### 4. Mock External Services

**Don't Depend on**:
- Third-party APIs (Stripe, SendGrid, Twilio)
- Email servers
- Payment gateways

**Mock Instead**:
```javascript
test('user can checkout with credit card', async ({ page }) => {
  // Mock Stripe API
  await page.route('**/api.stripe.com/**', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ id: 'ch_test_123', status: 'succeeded' }),
    });
  });

  // Test checkout flow
  await page.goto('/checkout');
  await page.fill('[name="cardNumber"]', '4242 4242 4242 4242');
  await page.click('button:has-text("Pay Now")');

  // Verify success
  await expect(page.locator('.success-message')).toHaveText('Payment successful');
});
```

---

## Summary

**E2E Testing Checklist**:
- [ ] Test critical user workflows (registration, login, checkout)
- [ ] Keep E2E tests minimal (10% of test suite)
- [ ] Use Page Object Model for maintainability
- [ ] Use robust selectors (test IDs, accessibility roles)
- [ ] Mock external services (APIs, payment gateways)
- [ ] Reuse authentication state (avoid logging in every test)
- [ ] Run tests in isolated environment (test database)
- [ ] Parallelize tests for faster execution
- [ ] Take screenshots/videos on failure for debugging
- [ ] Monitor and fix flaky tests immediately

**Recommended Tool**: Playwright (cross-browser, auto-wait, fast, modern API)

**E2E Test Example Structure**:
```
tests/
├── pages/
│   ├── LoginPage.js
│   ├── DashboardPage.js
│   └── CheckoutPage.js
├── builders/
│   ├── UserBuilder.js
│   └── ProductBuilder.js
├── fixtures/
│   ├── avatar.png
│   └── sample-product.json
└── e2e/
    ├── auth.spec.js
    ├── checkout.spec.js
    └── profile.spec.js
```

For unit and integration testing strategies, see `test-strategies.md`.
For coverage analysis, see `test-coverage.md`.

---

**Reference Version**: 1.0.0
**Last Updated**: 2025-12-04
