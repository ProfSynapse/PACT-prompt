# Test Suite Organization Example: E-Commerce Product Management Feature

## Context

**Feature**: Product management system for e-commerce admin dashboard
**Components**:
- Product CRUD API endpoints
- Product catalog service (business logic)
- Product repository (database layer)
- Product UI components (React)
- Inventory sync job (background worker)

**Testing Requirements**:
- Unit tests for business logic and utilities
- Integration tests for API and database
- E2E tests for critical user workflows
- Performance tests for catalog queries
- Target: 80% code coverage, <100ms API response time

---

## Test Suite Structure

```
tests/
├── unit/                           # 70% of tests - Fast, isolated
│   ├── services/
│   │   ├── product-service.test.js
│   │   └── pricing-calculator.test.js
│   ├── utils/
│   │   ├── validators.test.js
│   │   └── formatters.test.js
│   └── components/
│       ├── ProductCard.test.jsx
│       └── ProductForm.test.jsx
│
├── integration/                    # 20% of tests - Moderate speed
│   ├── api/
│   │   ├── product-api.test.js
│   │   └── inventory-api.test.js
│   ├── database/
│   │   └── product-repository.test.js
│   └── jobs/
│       └── inventory-sync.test.js
│
├── e2e/                            # 10% of tests - Slow, comprehensive
│   ├── product-creation.spec.js
│   └── product-search.spec.js
│
├── performance/                    # On-demand testing
│   └── catalog-load.test.js
│
└── fixtures/                       # Shared test data
    ├── products.json
    └── factories/
        └── productFactory.js
```

---

## Unit Tests: Business Logic

### Product Service Tests

**File**: `tests/unit/services/product-service.test.js`

```javascript
import { ProductService } from '@/services/product-service';
import { ValidationError } from '@/errors';

describe('ProductService', () => {
  let productService;
  let mockRepository;

  beforeEach(() => {
    // Mock repository to isolate service logic
    mockRepository = {
      findById: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    };
    productService = new ProductService(mockRepository);
  });

  describe('createProduct', () => {
    test('creates product with valid data', async () => {
      // Arrange
      const productData = {
        name: 'Wireless Mouse',
        sku: 'MOUSE-001',
        price: 29.99,
        inventory: 100,
      };

      mockRepository.create.mockResolvedValue({
        id: 1,
        ...productData,
      });

      // Act
      const result = await productService.createProduct(productData);

      // Assert
      expect(result).toMatchObject({
        id: expect.any(Number),
        name: 'Wireless Mouse',
        sku: 'MOUSE-001',
        price: 29.99,
      });
      expect(mockRepository.create).toHaveBeenCalledWith(productData);
    });

    test('throws ValidationError for negative price', async () => {
      // Arrange
      const invalidProduct = {
        name: 'Invalid Product',
        sku: 'INV-001',
        price: -10.00,
        inventory: 50,
      };

      // Act & Assert
      await expect(
        productService.createProduct(invalidProduct)
      ).rejects.toThrow(ValidationError);

      expect(mockRepository.create).not.toHaveBeenCalled();
    });

    test('throws ValidationError for duplicate SKU', async () => {
      // Arrange
      const duplicateProduct = {
        name: 'Duplicate Mouse',
        sku: 'MOUSE-001',
        price: 25.00,
        inventory: 50,
      };

      mockRepository.create.mockRejectedValue(
        new Error('Duplicate SKU')
      );

      // Act & Assert
      await expect(
        productService.createProduct(duplicateProduct)
      ).rejects.toThrow('Duplicate SKU');
    });

    test('applies default inventory value when not provided', async () => {
      // Arrange
      const productWithoutInventory = {
        name: 'Keyboard',
        sku: 'KEY-001',
        price: 79.99,
      };

      mockRepository.create.mockResolvedValue({
        id: 2,
        ...productWithoutInventory,
        inventory: 0, // Default value
      });

      // Act
      const result = await productService.createProduct(productWithoutInventory);

      // Assert
      expect(result.inventory).toBe(0);
      expect(mockRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({ inventory: 0 })
      );
    });
  });

  describe('calculateDiscountedPrice', () => {
    test('applies percentage discount correctly', () => {
      // Arrange
      const price = 100.00;
      const discountPercent = 20;

      // Act
      const result = productService.calculateDiscountedPrice(price, discountPercent);

      // Assert
      expect(result).toBe(80.00);
    });

    test('returns original price for 0% discount', () => {
      // Arrange
      const price = 50.00;

      // Act
      const result = productService.calculateDiscountedPrice(price, 0);

      // Assert
      expect(result).toBe(50.00);
    });

    test('handles floating point precision correctly', () => {
      // Arrange
      const price = 29.99;
      const discountPercent = 15;

      // Act
      const result = productService.calculateDiscountedPrice(price, discountPercent);

      // Assert
      expect(result).toBe(25.49); // Not 25.4915
    });

    test('throws error for discount > 100%', () => {
      // Arrange
      const price = 100.00;
      const invalidDiscount = 150;

      // Act & Assert
      expect(() => {
        productService.calculateDiscountedPrice(price, invalidDiscount);
      }).toThrow('Discount cannot exceed 100%');
    });
  });
});
```

**Key Points**:
- ✅ Each test is isolated with `beforeEach()` setup
- ✅ Mocked repository prevents database calls
- ✅ Tests follow AAA pattern (Arrange, Act, Assert)
- ✅ Edge cases covered (negative values, missing data, boundaries)
- ✅ Test names describe expected behavior clearly

---

## Integration Tests: API Endpoints

### Product API Integration Tests

**File**: `tests/integration/api/product-api.test.js`

```javascript
import request from 'supertest';
import { app } from '@/app';
import { db } from '@/database';
import { seedTestData, clearDatabase } from '@/tests/helpers';

describe('Product API', () => {
  let authToken;

  beforeAll(async () => {
    // Connect to test database
    await db.connect();
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    // Clear database and seed initial data
    await clearDatabase();
    await seedTestData();

    // Get authentication token for API calls
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({ email: 'admin@test.com', password: 'testpass' });

    authToken = loginResponse.body.token;
  });

  describe('POST /api/products', () => {
    test('creates product with valid data and returns 201', async () => {
      // Arrange
      const newProduct = {
        name: 'Wireless Keyboard',
        sku: 'KEY-WIRELESS-001',
        price: 89.99,
        inventory: 50,
        description: 'Ergonomic wireless keyboard',
      };

      // Act
      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${authToken}`)
        .send(newProduct)
        .expect(201);

      // Assert
      expect(response.body).toMatchObject({
        id: expect.any(Number),
        name: 'Wireless Keyboard',
        sku: 'KEY-WIRELESS-001',
        price: 89.99,
        inventory: 50,
      });

      // Verify product exists in database
      const productInDb = await db.products.findOne({
        where: { sku: 'KEY-WIRELESS-001' },
      });
      expect(productInDb).toBeDefined();
      expect(productInDb.name).toBe('Wireless Keyboard');
    });

    test('returns 400 for missing required fields', async () => {
      // Arrange
      const invalidProduct = {
        name: 'Incomplete Product',
        // Missing sku and price
      };

      // Act
      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${authToken}`)
        .send(invalidProduct)
        .expect(400);

      // Assert
      expect(response.body.error).toContain('sku');
      expect(response.body.error).toContain('price');
    });

    test('returns 409 for duplicate SKU', async () => {
      // Arrange
      const duplicateProduct = {
        name: 'Duplicate Product',
        sku: 'EXISTING-SKU-001', // Already seeded in test data
        price: 50.00,
        inventory: 10,
      };

      // Act
      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${authToken}`)
        .send(duplicateProduct)
        .expect(409);

      // Assert
      expect(response.body.error).toContain('SKU already exists');
    });

    test('returns 401 for missing authentication', async () => {
      // Arrange
      const product = {
        name: 'Test Product',
        sku: 'TEST-001',
        price: 25.00,
      };

      // Act
      await request(app)
        .post('/api/products')
        .send(product)
        .expect(401);
    });
  });

  describe('GET /api/products/:id', () => {
    test('retrieves product by ID', async () => {
      // Act
      const response = await request(app)
        .get('/api/products/1') // ID 1 seeded in test data
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      // Assert
      expect(response.body).toMatchObject({
        id: 1,
        name: expect.any(String),
        sku: expect.any(String),
        price: expect.any(Number),
      });
    });

    test('returns 404 for non-existent product', async () => {
      // Act
      await request(app)
        .get('/api/products/99999')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });
  });

  describe('PATCH /api/products/:id', () => {
    test('updates product price', async () => {
      // Arrange
      const updates = { price: 99.99 };

      // Act
      const response = await request(app)
        .patch('/api/products/1')
        .set('Authorization', `Bearer ${authToken}`)
        .send(updates)
        .expect(200);

      // Assert
      expect(response.body.price).toBe(99.99);

      // Verify database updated
      const productInDb = await db.products.findByPk(1);
      expect(productInDb.price).toBe(99.99);
    });

    test('prevents updating SKU to duplicate value', async () => {
      // Arrange
      const updates = { sku: 'EXISTING-SKU-002' }; // Duplicate

      // Act
      await request(app)
        .patch('/api/products/1')
        .set('Authorization', `Bearer ${authToken}`)
        .send(updates)
        .expect(409);
    });
  });
});
```

**Key Points**:
- ✅ Uses test database (not production)
- ✅ Clears and seeds data before each test for isolation
- ✅ Tests HTTP status codes, response bodies, and database state
- ✅ Covers authentication and authorization
- ✅ Tests error scenarios (400, 401, 404, 409)

---

## E2E Tests: User Workflows

### Product Creation Workflow

**File**: `tests/e2e/product-creation.spec.js`

```javascript
import { test, expect } from '@playwright/test';

test.describe('Product Creation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('http://localhost:3000/login');
    await page.fill('#email', 'admin@test.com');
    await page.fill('#password', 'testpass');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('admin can create a new product', async ({ page }) => {
    // Navigate to product creation page
    await page.click('text=Products');
    await page.click('button:has-text("Add Product")');
    await expect(page).toHaveURL(/.*\/products\/new/);

    // Fill out product form
    await page.fill('#name', 'Ergonomic Mouse Pad');
    await page.fill('#sku', 'PAD-ERGO-001');
    await page.fill('#price', '24.99');
    await page.fill('#inventory', '200');
    await page.fill('#description', 'Comfortable wrist support mouse pad');

    // Select category
    await page.selectOption('#category', 'Accessories');

    // Upload product image
    await page.setInputFiles('#image', 'tests/fixtures/mouse-pad.jpg');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify redirect to product list
    await page.waitForURL(/.*\/products$/);

    // Verify success message
    await expect(page.locator('.success-message')).toContainText(
      'Product created successfully'
    );

    // Verify product appears in list
    await expect(page.locator('table')).toContainText('Ergonomic Mouse Pad');
    await expect(page.locator('table')).toContainText('PAD-ERGO-001');
    await expect(page.locator('table')).toContainText('$24.99');
  });

  test('shows validation errors for invalid input', async ({ page }) => {
    // Navigate to product creation
    await page.click('text=Products');
    await page.click('button:has-text("Add Product")');

    // Submit form without filling required fields
    await page.click('button[type="submit"]');

    // Verify validation errors appear
    await expect(page.locator('#name-error')).toContainText('Name is required');
    await expect(page.locator('#sku-error')).toContainText('SKU is required');
    await expect(page.locator('#price-error')).toContainText('Price is required');

    // Fill name field
    await page.fill('#name', 'Test Product');

    // Verify name error disappears
    await expect(page.locator('#name-error')).toBeHidden();
  });

  test('prevents duplicate SKU submission', async ({ page }) => {
    // Navigate to product creation
    await page.click('text=Products');
    await page.click('button:has-text("Add Product")');

    // Fill form with existing SKU
    await page.fill('#name', 'Duplicate Product');
    await page.fill('#sku', 'EXISTING-SKU-001'); // Already exists
    await page.fill('#price', '50.00');
    await page.fill('#inventory', '10');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('.error-message')).toContainText(
      'SKU already exists'
    );

    // Verify still on creation page
    await expect(page).toHaveURL(/.*\/products\/new/);
  });
});
```

**Key Points**:
- ✅ Tests complete user journey from login to product creation
- ✅ Verifies UI interactions (clicks, form fills, navigation)
- ✅ Checks success and error messages
- ✅ Validates client-side and server-side error handling
- ✅ Uses page object pattern for maintainability (could be extracted)

---

## Test Data Management

### Fixtures

**File**: `tests/fixtures/products.json`

```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "sku": "EXISTING-SKU-001",
    "price": 29.99,
    "inventory": 100,
    "category": "Accessories"
  },
  {
    "id": 2,
    "name": "Mechanical Keyboard",
    "sku": "EXISTING-SKU-002",
    "price": 129.99,
    "inventory": 50,
    "category": "Keyboards"
  }
]
```

### Factory Pattern

**File**: `tests/fixtures/factories/productFactory.js`

```javascript
import { faker } from '@faker-js/faker';

export const productFactory = {
  build: (overrides = {}) => ({
    name: faker.commerce.productName(),
    sku: faker.string.alphanumeric(10).toUpperCase(),
    price: parseFloat(faker.commerce.price()),
    inventory: faker.number.int({ min: 0, max: 500 }),
    description: faker.commerce.productDescription(),
    category: faker.helpers.arrayElement(['Accessories', 'Keyboards', 'Mice', 'Monitors']),
    ...overrides,
  }),

  buildMany: (count, overrides = {}) => {
    return Array.from({ length: count }, () => productFactory.build(overrides));
  },
};

// Usage in tests:
// const product = productFactory.build({ price: 99.99 });
// const products = productFactory.buildMany(10);
```

---

## Test Organization Best Practices

### 1. Test Naming Convention
```javascript
// ✅ GOOD: Descriptive test names
test('creates product with valid data and returns 201', ...);
test('returns 400 for missing required fields', ...);
test('prevents duplicate SKU submission', ...);

// ❌ BAD: Vague test names
test('test product creation', ...);
test('should work', ...);
test('validates input', ...);
```

### 2. Test Isolation
```javascript
// ✅ GOOD: Each test is independent
beforeEach(async () => {
  await clearDatabase();
  await seedTestData();
});

// ❌ BAD: Tests depend on execution order
test('create product', ...);
test('update product created in previous test', ...); // FRAGILE
```

### 3. Assertion Clarity
```javascript
// ✅ GOOD: Specific assertions
expect(response.body.price).toBe(29.99);
expect(response.body).toMatchObject({
  name: 'Wireless Mouse',
  sku: 'MOUSE-001',
});

// ❌ BAD: Vague assertions
expect(response.body).toBeTruthy();
expect(response.status).toBeGreaterThan(199);
```

---

## Running the Tests

### NPM Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:unit": "jest tests/unit",
    "test:integration": "jest tests/integration",
    "test:e2e": "playwright test",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  }
}
```

### Coverage Report

```bash
$ npm run test:coverage

-----------------|---------|----------|---------|---------|-------------------
File             | % Stmts | % Branch | % Funcs | % Lines | Uncovered Lines
-----------------|---------|----------|---------|---------|-------------------
All files        |   87.34 |    82.14 |   90.47 |   87.51 |
 services        |   92.10 |    88.23 |   95.00 |   92.30 |
  product-service|   94.50 |    91.20 |   96.00 |   94.60 | 45-48,102
 repositories    |   85.20 |    78.00 |   88.00 |   85.40 |
 controllers     |   83.00 |    75.50 |   85.00 |   83.20 |
-----------------|---------|----------|---------|---------|-------------------
```

---

## Key Decisions

### 1. Test Pyramid Distribution
**Decision**: 70% unit, 20% integration, 10% E2E
**Rationale**: Maximize fast, reliable tests; minimize slow, brittle E2E tests
**Trade-off**: E2E tests catch integration issues but are expensive to maintain

### 2. Test Database Strategy
**Decision**: Separate test database with before/after cleanup
**Rationale**: Ensures test isolation, prevents production data corruption
**Trade-off**: Slower than in-memory DB, but more realistic

### 3. Factory vs Fixtures
**Decision**: Use factories for dynamic data, fixtures for reference data
**Rationale**: Factories prevent test conflicts (unique SKUs), fixtures for stable data
**Trade-off**: Factories add complexity but improve test isolation

---

## Common Pitfalls Avoided

1. **Test pollution**: Each test clears database to avoid state leakage
2. **Hard-coded IDs**: Use factories to generate unique test data
3. **Timing issues**: Use `waitFor` in E2E tests instead of arbitrary `sleep()`
4. **Missing edge cases**: Tests cover happy path, error cases, and boundaries
5. **Non-deterministic tests**: Mock time, random data, external APIs

---

*Example from pact-testing-patterns skill - Test suite organization for a complete feature*
