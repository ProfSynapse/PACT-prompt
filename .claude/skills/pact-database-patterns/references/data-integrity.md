# Data Integrity Reference

Comprehensive guide to database constraints, transactions, validation patterns, and data integrity enforcement.

## Table of Contents

1. [Constraints](#constraints)
2. [Transaction Management](#transaction-management)
3. [Validation Patterns](#validation-patterns)
4. [Concurrency Control](#concurrency-control)
5. [Data Quality](#data-quality)
6. [Audit and Compliance](#audit-and-compliance)

## Constraints

### Primary Key Constraints

**Purpose**: Uniquely identify each row

```sql
-- Auto-incrementing integer
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,  -- PostgreSQL
  -- id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- MySQL
  username VARCHAR(50) NOT NULL
);

-- UUID
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) NOT NULL
);

-- Composite primary key
CREATE TABLE enrollments (
  student_id BIGINT,
  course_id BIGINT,
  PRIMARY KEY (student_id, course_id)
);

-- Named constraint
CREATE TABLE users (
  id BIGINT,
  username VARCHAR(50),
  CONSTRAINT pk_users PRIMARY KEY (id)
);
```

**Best Practices**
- Always have a primary key
- Use BIGINT for auto-increment (future-proof)
- Keep primary keys immutable (never update)
- Use surrogate keys (id) instead of natural keys for most tables
- Use composite keys for junction tables only

### Foreign Key Constraints

**Purpose**: Enforce referential integrity

```sql
-- Basic foreign key
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Named constraint with actions
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT    -- Prevent deletion if orders exist
    ON UPDATE CASCADE     -- Update order.user_id if user.id changes
);
```

**Referential Actions**

```sql
-- RESTRICT: Prevent parent deletion if children exist (default, safest)
ON DELETE RESTRICT

-- CASCADE: Delete children when parent deleted (use carefully!)
ON DELETE CASCADE
-- Example: Delete all order_items when order is deleted

-- SET NULL: Set child FK to NULL when parent deleted
ON DELETE SET NULL
-- Example: Set user_id to NULL when user deleted (must allow NULL)

-- NO ACTION: Similar to RESTRICT (check at end of transaction)
ON DELETE NO ACTION

-- SET DEFAULT: Set to default value when parent deleted
ON DELETE SET DEFAULT
```

**When to Use Each Action**

```sql
-- CASCADE: Parent-child ownership
CREATE TABLE order_items (
  order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE
);
-- If order deleted, all its items should be deleted

-- RESTRICT: Prevent orphaning (most common)
CREATE TABLE orders (
  user_id BIGINT REFERENCES users(id) ON DELETE RESTRICT
);
-- Can't delete user who has orders

-- SET NULL: Optional relationship
CREATE TABLE posts (
  author_id BIGINT REFERENCES users(id) ON DELETE SET NULL
);
-- If user deleted, posts remain but author is unknown
```

### Unique Constraints

**Purpose**: Ensure column values are unique

```sql
-- Single column
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL
);

-- Multiple unique constraints
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  email VARCHAR(255),
  username VARCHAR(50),
  CONSTRAINT uq_users_email UNIQUE (email),
  CONSTRAINT uq_users_username UNIQUE (username)
);

-- Composite unique constraint
CREATE TABLE user_favorites (
  user_id BIGINT REFERENCES users(id),
  product_id BIGINT REFERENCES products(id),
  UNIQUE (user_id, product_id)  -- User can favorite product once
);

-- Partial unique constraint (PostgreSQL)
CREATE UNIQUE INDEX uq_active_usernames
ON users(username)
WHERE deleted_at IS NULL;
-- Unique only among non-deleted users
```

**Unique vs Primary Key**
- Primary key: NOT NULL + UNIQUE (only one per table)
- Unique: Can be NULL (unless NOT NULL specified), multiple allowed

### Check Constraints

**Purpose**: Enforce business rules

```sql
-- Simple check
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  CONSTRAINT check_positive_price CHECK (price > 0)
);

-- Multiple conditions
CREATE TABLE employees (
  id BIGINT PRIMARY KEY,
  birth_date DATE NOT NULL,
  hire_date DATE NOT NULL,
  salary DECIMAL(10,2) NOT NULL,
  CONSTRAINT check_hire_after_birth CHECK (hire_date > birth_date),
  CONSTRAINT check_reasonable_salary CHECK (salary > 0 AND salary < 10000000)
);

-- Enum-like check
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  status VARCHAR(20) NOT NULL,
  CONSTRAINT check_valid_status
    CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
);

-- Complex business rule
CREATE TABLE reservations (
  id BIGINT PRIMARY KEY,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  guest_count INT NOT NULL,
  CONSTRAINT check_valid_dates CHECK (end_date > start_date),
  CONSTRAINT check_guest_count CHECK (guest_count > 0 AND guest_count <= 10)
);
```

**Best Practices**
- Use CHECK for simple validation (ranges, enums)
- Document why the constraint exists
- Test constraint violations in your application code
- Consider performance impact (checked on every INSERT/UPDATE)

### NOT NULL Constraints

**Purpose**: Ensure column has a value

```sql
-- Required fields
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  email VARCHAR(255) NOT NULL,     -- Always required
  username VARCHAR(50) NOT NULL,   -- Always required
  bio TEXT                         -- Optional (NULL allowed)
);

-- Add NOT NULL to existing column (after checking no NULLs exist)
-- Step 1: Update existing NULLs
UPDATE users SET email = 'unknown@example.com' WHERE email IS NULL;

-- Step 2: Add constraint
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Remove NOT NULL
ALTER TABLE users ALTER COLUMN bio DROP NOT NULL;
```

**Three-State Logic**
```sql
-- Boolean with NULL = three states: TRUE, FALSE, UNKNOWN
email_verified BOOLEAN  -- TRUE, FALSE, or NULL

-- Queries with NULL
WHERE email_verified = TRUE   -- Only TRUE rows
WHERE email_verified = FALSE  -- Only FALSE rows
WHERE email_verified IS NULL  -- Only NULL rows
WHERE email_verified IS NOT NULL  -- TRUE or FALSE rows
```

## Transaction Management

### ACID Properties Review

**Atomicity**: All operations succeed or all fail
**Consistency**: Data moves from one valid state to another
**Isolation**: Concurrent transactions don't interfere
**Durability**: Committed data survives crashes

### Transaction Basics

```sql
-- Explicit transaction
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Rollback on error
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  -- Error occurs
ROLLBACK;

-- Savepoints (partial rollback)
BEGIN;
  UPDATE table1 SET ...;

  SAVEPOINT sp1;
  UPDATE table2 SET ...;  -- This might fail

  -- If table2 update fails, rollback to savepoint
  ROLLBACK TO SAVEPOINT sp1;

  -- Continue with transaction
  UPDATE table3 SET ...;
COMMIT;
```

### Isolation Levels

**From Weakest to Strongest**

#### Read Uncommitted

**Allows**: Dirty reads (reading uncommitted changes)
**Use case**: Almost never (only for very specific analytics)

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Transaction A:
BEGIN;
UPDATE products SET price = 100 WHERE id = 1;
-- Not committed yet

-- Transaction B can see uncommitted price = 100
SELECT price FROM products WHERE id = 1;  -- Returns 100

-- Transaction A:
ROLLBACK;  -- Price never actually changed

-- Transaction B saw data that never existed!
```

#### Read Committed (Most Common Default)

**Prevents**: Dirty reads
**Allows**: Non-repeatable reads, phantom reads
**Use case**: Most applications

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Transaction A:
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- Returns 500

-- Transaction B:
BEGIN;
UPDATE accounts SET balance = 1000 WHERE id = 1;
COMMIT;

-- Transaction A:
SELECT balance FROM accounts WHERE id = 1;  -- Returns 1000 (changed!)
COMMIT;

-- Same query returned different results (non-repeatable read)
```

#### Repeatable Read

**Prevents**: Dirty reads, non-repeatable reads
**Allows**: Phantom reads
**Use case**: When you need consistent reads within a transaction

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Transaction A:
BEGIN;
SELECT * FROM users WHERE age > 18;  -- Returns 100 rows

-- Transaction B:
BEGIN;
INSERT INTO users (age) VALUES (25);
COMMIT;

-- Transaction A:
SELECT * FROM users WHERE age > 18;  -- Still returns 100 rows
-- Doesn't see new row inserted by Transaction B
COMMIT;
```

#### Serializable (Strictest)

**Prevents**: All anomalies (serialized execution)
**Use case**: Financial transactions, critical data

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Transactions execute as if run serially
-- May cause more deadlocks and performance impact
-- Use only when necessary
```

**Choosing Isolation Level**

```sql
-- General web application
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Financial transaction (transfer money)
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Reporting/analytics (consistent snapshot)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Monitoring (don't care about perfect accuracy)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
```

### Transaction Best Practices

**1. Keep Transactions Short**
```sql
-- ❌ Long transaction holding locks
BEGIN;
  SELECT * FROM users;  -- Acquire locks
  -- ... process data in application code for 30 seconds ...
  UPDATE users SET ...;
COMMIT;

-- ✅ Short transaction
-- Process data OUTSIDE transaction
BEGIN;
  UPDATE users SET ...;  -- Quick update
COMMIT;
```

**2. Acquire Locks in Consistent Order**
```sql
-- ❌ Can deadlock
-- Process A:
UPDATE accounts SET ... WHERE id = 1;
UPDATE accounts SET ... WHERE id = 2;

-- Process B:
UPDATE accounts SET ... WHERE id = 2;  -- Waits for Process A
UPDATE accounts SET ... WHERE id = 1;  -- Deadlock!

-- ✅ Always lock in same order
-- Both processes:
UPDATE accounts SET ...
WHERE id IN (1, 2)
ORDER BY id;  -- Consistent order
```

**3. Handle Deadlocks with Retry**
```python
# Pseudocode
def transfer_money(from_id, to_id, amount):
  max_retries = 3
  for attempt in range(max_retries):
    try:
      begin_transaction()
      update_account(from_id, -amount)
      update_account(to_id, amount)
      commit_transaction()
      return True
    except DeadlockError:
      rollback_transaction()
      if attempt == max_retries - 1:
        raise
      sleep(random.uniform(0.1, 0.5))  # Random backoff
  return False
```

## Validation Patterns

### Database-Level Validation

**Constraints** (already covered)
```sql
-- Data type validation (automatic)
CREATE TABLE users (
  age INT  -- Must be integer
);

-- Range validation
CHECK (age >= 0 AND age <= 150)

-- Format validation (regex, PostgreSQL)
CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

-- Enum validation
CHECK (status IN ('active', 'inactive', 'suspended'))
```

### Application-Level Validation

**Layered Validation Strategy**
1. **Client-side**: UX (instant feedback, can be bypassed)
2. **Application**: Business rules (definitive validation)
3. **Database**: Last line of defense (data integrity)

```python
# Pseudocode: Application validation
def create_user(email, age):
  # Validation layer
  if not email or '@' not in email:
    raise ValidationError("Invalid email")

  if age < 18:
    raise ValidationError("Must be 18 or older")

  if user_exists(email):
    raise ValidationError("Email already registered")

  # Database will also enforce:
  # - NOT NULL on email
  # - UNIQUE on email
  # - CHECK on age range
  db.insert(users, email=email, age=age)
```

### Triggers for Complex Validation

```sql
-- Prevent invalid state transitions
CREATE OR REPLACE FUNCTION check_order_status_transition()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status = 'delivered' AND NEW.status != 'delivered' THEN
    RAISE EXCEPTION 'Cannot change status of delivered order';
  END IF;

  IF OLD.status = 'cancelled' THEN
    RAISE EXCEPTION 'Cannot modify cancelled order';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_order_status
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION check_order_status_transition();
```

## Concurrency Control

### Optimistic Locking

**Pattern**: Version column, check before update

```sql
-- Add version column
ALTER TABLE products ADD COLUMN version INT DEFAULT 0;

-- Read with version
SELECT id, name, price, version FROM products WHERE id = 123;
-- Returns: version = 5

-- Update with version check
UPDATE products
SET name = 'New Name', price = 99.99, version = version + 1
WHERE id = 123 AND version = 5;  -- Only update if version still 5

-- Check rows affected
-- If 0 rows updated → someone else modified it → retry or error
```

**Application Code**
```python
# Pseudocode
def update_product(product_id, new_data, expected_version):
  result = db.execute(
    "UPDATE products SET name = ?, price = ?, version = version + 1 "
    "WHERE id = ? AND version = ?",
    [new_data['name'], new_data['price'], product_id, expected_version]
  )

  if result.rows_affected == 0:
    raise ConcurrentModificationError("Product was modified by another user")
```

### Pessimistic Locking

**Pattern**: Lock rows during read

```sql
-- FOR UPDATE: Lock rows for writing
BEGIN;
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
  -- Row is locked, other transactions wait
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR UPDATE NOWAIT: Fail immediately if locked
BEGIN;
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
  -- Raises error if already locked
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR UPDATE SKIP LOCKED: Skip locked rows
SELECT * FROM queue WHERE processed = false
LIMIT 10
FOR UPDATE SKIP LOCKED;
-- Returns only unlocked rows (useful for job queues)
```

### Select for Update Pattern

```sql
-- Job queue processing
BEGIN;
  -- Lock and get next job
  SELECT * FROM jobs
  WHERE status = 'pending'
  ORDER BY created_at
  LIMIT 1
  FOR UPDATE SKIP LOCKED;

  -- Process job (in application)

  -- Mark complete
  UPDATE jobs SET status = 'completed' WHERE id = ?;
COMMIT;
```

## Data Quality

### Handling NULL Values

**NULL represents unknown, not zero or empty string**

```sql
-- Three-valued logic: TRUE, FALSE, UNKNOWN
WHERE age > 18           -- NULL age → UNKNOWN → excluded from results
WHERE age > 18 OR age IS NULL  -- Include unknown ages

-- NULL in aggregations
SELECT
  COUNT(*) as total_rows,           -- Counts all rows
  COUNT(email) as rows_with_email,  -- Counts non-NULL emails
  AVG(age) as average_age           -- Ignores NULL ages
FROM users;

-- NULL in comparisons
WHERE value = NULL    -- ❌ Always false! NULL is not equal to anything
WHERE value IS NULL   -- ✅ Correct way

-- COALESCE: Provide default for NULL
SELECT COALESCE(phone_number, 'Not provided') FROM users;
SELECT COALESCE(discount, 0) FROM products;  -- Treat NULL as 0
```

### Data Normalization

**Normalize text for comparison**
```sql
-- Case-insensitive email
CREATE UNIQUE INDEX idx_users_email_lower
ON users(LOWER(email));

-- Always query with LOWER
SELECT * FROM users WHERE LOWER(email) = LOWER(?);

-- Or store normalized
CREATE TABLE users (
  email VARCHAR(255) NOT NULL,
  email_normalized VARCHAR(255) GENERATED ALWAYS AS (LOWER(email)) STORED,
  UNIQUE (email_normalized)
);
```

### Data Consistency

**Maintaining Consistency Across Tables**
```sql
-- Use transactions for multi-table changes
BEGIN;
  INSERT INTO orders (user_id, total) VALUES (1, 100.00);
  UPDATE users SET total_spent = total_spent + 100.00 WHERE id = 1;
COMMIT;

-- Use triggers for automatic consistency
CREATE TRIGGER update_user_total
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION update_user_total_spent();
```

## Audit and Compliance

### Audit Columns Pattern

```sql
-- Basic audit columns
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  -- ... business columns ...

  created_at TIMESTAMP DEFAULT NOW() NOT NULL,
  created_by BIGINT REFERENCES users(id),
  updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
  updated_by BIGINT REFERENCES users(id)
);

-- Update trigger for updated_at
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Audit Trail Pattern

```sql
-- Complete history of all changes
CREATE TABLE users_audit (
  audit_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  operation CHAR(1) NOT NULL,  -- I, U, D
  changed_at TIMESTAMP DEFAULT NOW() NOT NULL,
  changed_by BIGINT,

  -- Store old and new values
  old_values JSONB,
  new_values JSONB,

  -- Or store complete row snapshots
  old_row JSONB,
  new_row JSONB
);

-- Trigger to populate audit table
CREATE TRIGGER users_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION audit_users();

CREATE OR REPLACE FUNCTION audit_users()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    INSERT INTO users_audit (user_id, operation, old_values)
    VALUES (OLD.id, 'D', row_to_json(OLD));
    RETURN OLD;
  ELSIF (TG_OP = 'UPDATE') THEN
    INSERT INTO users_audit (user_id, operation, old_values, new_values)
    VALUES (NEW.id, 'U', row_to_json(OLD), row_to_json(NEW));
    RETURN NEW;
  ELSIF (TG_OP = 'INSERT') THEN
    INSERT INTO users_audit (user_id, operation, new_values)
    VALUES (NEW.id, 'I', row_to_json(NEW));
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;
```

### Temporal Tables (System Versioning)

```sql
-- PostgreSQL: Temporal tables with periods
CREATE TABLE employees (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  department VARCHAR(100),

  -- Temporal columns
  valid_from TIMESTAMP DEFAULT NOW() NOT NULL,
  valid_to TIMESTAMP DEFAULT 'infinity' NOT NULL,

  CONSTRAINT valid_period CHECK (valid_to > valid_from)
);

-- Query current state
SELECT * FROM employees WHERE valid_to = 'infinity';

-- Query historical state (as of date)
SELECT * FROM employees
WHERE '2024-01-15' BETWEEN valid_from AND valid_to;

-- Query all history
SELECT * FROM employees ORDER BY id, valid_from;
```

### GDPR Compliance Patterns

**Right to be Forgotten**
```sql
-- Soft delete with anonymization
UPDATE users
SET
  email = CONCAT('deleted_', id, '@example.com'),
  name = 'Deleted User',
  phone = NULL,
  address = NULL,
  deleted_at = NOW()
WHERE id = ?;

-- Or: Hard delete with audit retention
BEGIN;
  -- Archive to audit table
  INSERT INTO deleted_users_audit
  SELECT *, NOW() as deleted_at FROM users WHERE id = ?;

  -- Delete from main table
  DELETE FROM users WHERE id = ?;
COMMIT;
```

**Data Encryption**
```sql
-- Encrypt PII at rest (PostgreSQL pgcrypto)
CREATE EXTENSION pgcrypto;

-- Encrypt on insert
INSERT INTO users (email, ssn_encrypted)
VALUES (
  'user@example.com',
  pgp_sym_encrypt('123-45-6789', 'encryption_key')
);

-- Decrypt on select
SELECT
  email,
  pgp_sym_decrypt(ssn_encrypted, 'encryption_key') as ssn
FROM users WHERE id = 1;
```

---

*Reference file for pact-database-patterns skill*
