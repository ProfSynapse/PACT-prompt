# Schema Design Patterns Reference

Comprehensive guide to database schema design patterns, normalization strategies, and relationship modeling.

## Table of Contents

1. [Normalization Forms](#normalization-forms)
2. [Denormalization Strategies](#denormalization-strategies)
3. [Relationship Patterns](#relationship-patterns)
4. [Data Type Selection](#data-type-selection)
5. [Common Design Patterns](#common-design-patterns)
6. [Anti-Patterns](#anti-patterns)

## Normalization Forms

### First Normal Form (1NF)

**Requirements**
- Each column contains atomic (indivisible) values
- Each column contains values of a single type
- Each column has a unique name
- Order of rows doesn't matter

**Example Violation**
```sql
-- ❌ Violates 1NF: phone_numbers is a comma-separated list
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  phone_numbers VARCHAR(255)  -- "555-1234,555-5678,555-9012"
);
```

**Corrected Design**
```sql
-- ✅ Complies with 1NF: atomic values only
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE user_phones (
  id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  phone_number VARCHAR(20) NOT NULL,
  phone_type VARCHAR(20)  -- 'mobile', 'home', 'work'
);
```

### Second Normal Form (2NF)

**Requirements**
- Must be in 1NF
- All non-key attributes depend on the entire primary key
- Only applies to tables with composite primary keys

**Example Violation**
```sql
-- ❌ Violates 2NF: course_name depends only on course_id, not on (student_id, course_id)
CREATE TABLE enrollments (
  student_id BIGINT,
  course_id BIGINT,
  course_name VARCHAR(100),  -- Partial dependency!
  enrollment_date DATE,
  PRIMARY KEY (student_id, course_id)
);
```

**Corrected Design**
```sql
-- ✅ Complies with 2NF: separated into proper tables
CREATE TABLE students (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE courses (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE enrollments (
  student_id BIGINT REFERENCES students(id),
  course_id BIGINT REFERENCES courses(id),
  enrollment_date DATE,
  PRIMARY KEY (student_id, course_id)
);
```

### Third Normal Form (3NF)

**Requirements**
- Must be in 2NF
- No transitive dependencies (non-key attributes depend only on primary key)

**Example Violation**
```sql
-- ❌ Violates 3NF: city and state depend on zip_code, not directly on id
CREATE TABLE customers (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  zip_code VARCHAR(10),
  city VARCHAR(50),      -- Depends on zip_code
  state VARCHAR(2)       -- Depends on zip_code
);
```

**Corrected Design**
```sql
-- ✅ Complies with 3NF: removed transitive dependency
CREATE TABLE customers (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  zip_code VARCHAR(10) REFERENCES zip_codes(code)
);

CREATE TABLE zip_codes (
  code VARCHAR(10) PRIMARY KEY,
  city VARCHAR(50) NOT NULL,
  state VARCHAR(2) NOT NULL
);
```

### Boyce-Codd Normal Form (BCNF)

**Requirements**
- Must be in 3NF
- Every determinant must be a candidate key
- Stricter than 3NF, handles certain edge cases

**Example Violation**
```sql
-- ❌ Violates BCNF: professor determines department, but professor is not a candidate key
CREATE TABLE teaching_assignments (
  student_id BIGINT,
  course_id BIGINT,
  professor VARCHAR(100),
  department VARCHAR(100),  -- Determined by professor
  PRIMARY KEY (student_id, course_id)
);
```

**Corrected Design**
```sql
-- ✅ Complies with BCNF
CREATE TABLE professors (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  department_id BIGINT REFERENCES departments(id)
);

CREATE TABLE teaching_assignments (
  student_id BIGINT REFERENCES students(id),
  course_id BIGINT REFERENCES courses(id),
  professor_id BIGINT REFERENCES professors(id),
  PRIMARY KEY (student_id, course_id)
);
```

## Denormalization Strategies

### When to Denormalize

Denormalize only when you have:
1. **Proven performance problems** with normalized schema
2. **Metrics showing** read frequency >> write frequency (e.g., 1000:1)
3. **Measured JOIN cost** that impacts user experience
4. **Clear maintenance plan** for keeping denormalized data in sync

### Common Denormalization Patterns

#### 1. Storing Computed Values

**Use Case**: Expensive aggregations performed frequently

```sql
-- Normalized (requires aggregation every time)
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  customer_id BIGINT REFERENCES customers(id),
  order_date DATE
);

CREATE TABLE order_items (
  id BIGINT PRIMARY KEY,
  order_id BIGINT REFERENCES orders(id),
  product_id BIGINT REFERENCES products(id),
  quantity INT,
  unit_price DECIMAL(10,2)
);

-- Query requires aggregation:
-- SELECT SUM(quantity * unit_price) FROM order_items WHERE order_id = ?

-- Denormalized: store computed total
ALTER TABLE orders ADD COLUMN total_amount DECIMAL(10,2);

-- Maintain with trigger
CREATE TRIGGER update_order_total
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW EXECUTE FUNCTION recalculate_order_total();
```

#### 2. Duplicating Reference Data

**Use Case**: Frequently accessed lookup values

```sql
-- Option 1: Normalized (requires JOIN)
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200),
  category_id BIGINT REFERENCES categories(id)
);

CREATE TABLE categories (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

-- Option 2: Denormalized (duplicates category name)
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200),
  category_id BIGINT REFERENCES categories(id),
  category_name VARCHAR(100)  -- Denormalized for faster reads
);

-- Trade-off: Faster reads, but must update all products when category renamed
```

#### 3. Historical Snapshots

**Use Case**: Audit requirements, point-in-time queries

```sql
-- Store denormalized snapshot of related data at transaction time
CREATE TABLE invoices (
  id BIGINT PRIMARY KEY,
  customer_id BIGINT REFERENCES customers(id),

  -- Snapshot of customer data at invoice time
  customer_name VARCHAR(100),
  customer_address TEXT,
  customer_tax_id VARCHAR(50),

  invoice_date DATE,
  total_amount DECIMAL(10,2)
);

-- Even if customer changes their name/address later,
-- invoice shows what it was when invoice was created
```

#### 4. Materialized Aggregations

**Use Case**: Dashboard metrics, reporting tables

```sql
-- Real-time aggregation is expensive
CREATE TABLE daily_sales_summary (
  summary_date DATE PRIMARY KEY,
  total_orders INT,
  total_revenue DECIMAL(12,2),
  total_items_sold INT,
  unique_customers INT,

  -- Metadata
  last_updated TIMESTAMP DEFAULT NOW()
);

-- Populated by scheduled job (not real-time)
-- Much faster to query than aggregating millions of order records
```

### Denormalization Best Practices

1. **Document the decision**: Explain why, what metrics justified it
2. **Maintain data integrity**: Use triggers, application logic, or batch jobs
3. **Monitor data drift**: Alert if denormalized data gets out of sync
4. **Plan for updates**: How will you keep duplicated data consistent?
5. **Consider alternatives first**: Caching, read replicas, materialized views

## Relationship Patterns

### One-to-Many (1:N)

**Most Common Pattern**: Foreign key in the "many" table

```sql
CREATE TABLE authors (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE books (
  id BIGINT PRIMARY KEY,
  title VARCHAR(200),
  author_id BIGINT NOT NULL REFERENCES authors(id),
  published_date DATE
);

-- One author can have many books
-- Each book has exactly one author (in this simplified model)
```

### Many-to-Many (M:N)

**Pattern**: Junction table with foreign keys to both entities

```sql
CREATE TABLE students (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE courses (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100)
);

-- Junction table
CREATE TABLE enrollments (
  student_id BIGINT REFERENCES students(id),
  course_id BIGINT REFERENCES courses(id),
  enrollment_date DATE,
  grade VARCHAR(2),
  PRIMARY KEY (student_id, course_id)
);

-- One student can enroll in many courses
-- One course can have many students
```

### One-to-One (1:1)

**Pattern**: Foreign key with UNIQUE constraint, or shared primary key

```sql
-- Approach 1: Foreign key with UNIQUE
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(100)
);

CREATE TABLE user_profiles (
  id BIGINT PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL REFERENCES users(id),
  bio TEXT,
  avatar_url VARCHAR(255)
);

-- Approach 2: Shared primary key
CREATE TABLE user_profiles (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  bio TEXT,
  avatar_url VARCHAR(255)
);
```

**When to Use 1:1**
- Vertical partitioning (separate frequently vs rarely accessed columns)
- Security isolation (PII in separate table with stricter access)
- Optional data (not all users have profiles)

### Self-Referencing Relationships

**Pattern**: Foreign key references same table

```sql
-- Employee hierarchy
CREATE TABLE employees (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  manager_id BIGINT REFERENCES employees(id),  -- Self-reference
  department VARCHAR(100)
);

-- Category tree
CREATE TABLE categories (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100),
  parent_id BIGINT REFERENCES categories(id),  -- Self-reference
  level INT,  -- Denormalized for easier queries
  path VARCHAR(500)  -- E.g., "1/5/23" for breadcrumb
);
```

### Polymorphic Relationships

**Anti-Pattern**: Avoid when possible

```sql
-- ❌ Polymorphic foreign key (can't enforce referential integrity)
CREATE TABLE comments (
  id BIGINT PRIMARY KEY,
  commentable_type VARCHAR(50),  -- 'Post' or 'Photo'
  commentable_id BIGINT,         -- ID in posts or photos table
  body TEXT
);

-- ✅ Better: Separate foreign keys with constraints
CREATE TABLE comments (
  id BIGINT PRIMARY KEY,
  post_id BIGINT REFERENCES posts(id),
  photo_id BIGINT REFERENCES photos(id),
  body TEXT,

  -- Ensure exactly one is set
  CONSTRAINT check_one_parent CHECK (
    (post_id IS NOT NULL AND photo_id IS NULL) OR
    (post_id IS NULL AND photo_id IS NOT NULL)
  )
);

-- ✅ Best: Separate tables if behavior differs significantly
CREATE TABLE post_comments (
  id BIGINT PRIMARY KEY,
  post_id BIGINT REFERENCES posts(id),
  body TEXT
);

CREATE TABLE photo_comments (
  id BIGINT PRIMARY KEY,
  photo_id BIGINT REFERENCES photos(id),
  body TEXT
);
```

## Data Type Selection

### Identifiers

```sql
-- Auto-incrementing integers
id BIGSERIAL PRIMARY KEY  -- PostgreSQL: 1 to 9,223,372,036,854,775,807
id BIGINT AUTO_INCREMENT PRIMARY KEY  -- MySQL

-- UUIDs (for distributed systems, no central coordination needed)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()  -- PostgreSQL
id CHAR(36) PRIMARY KEY  -- MySQL (store as string)

-- When to use each:
-- BIGINT: Single database, sequential IDs acceptable, slightly faster
-- UUID: Distributed systems, merging databases, hide record counts
```

### Timestamps

```sql
-- ✅ Always use timezone-aware timestamps
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

-- ❌ Avoid timezone-naive timestamps
created_at TIMESTAMP  -- Ambiguous! What timezone?

-- Date only (no time component)
birth_date DATE

-- Time only (no date component)
meeting_time TIME
```

### Money and Decimals

```sql
-- ✅ Use DECIMAL for money (exact precision)
price DECIMAL(10,2)  -- 10 digits total, 2 after decimal
-- Stores: 12345678.90

-- ❌ Never use FLOAT/REAL for money (rounding errors)
price FLOAT  -- BAD! 0.1 + 0.2 != 0.3

-- For currencies, consider:
amount DECIMAL(19,4)  -- Supports crypto micro-transactions
currency_code CHAR(3)  -- ISO 4217: 'USD', 'EUR', 'JPY'
```

### Text

```sql
-- Variable length with limit (most common)
username VARCHAR(50)
email VARCHAR(255)
title VARCHAR(200)

-- Fixed length (padded with spaces, only use if truly fixed)
country_code CHAR(2)  -- 'US', 'GB', 'JP'
state_code CHAR(2)    -- 'CA', 'NY', 'TX'

-- Unlimited text (use sparingly)
description TEXT
blog_post_body TEXT

-- When to use each:
-- VARCHAR: Known maximum length, indexed columns
-- TEXT: Unknown length, rarely indexed, large content
```

### Boolean

```sql
-- ✅ Use native BOOLEAN type
is_active BOOLEAN DEFAULT TRUE
is_verified BOOLEAN DEFAULT FALSE

-- ❌ Avoid integer flags (less clear, more error-prone)
is_active TINYINT  -- 0 = false, 1 = true? What about 2?

-- Three-state logic (true/false/unknown)
email_verified BOOLEAN  -- TRUE, FALSE, or NULL
```

### JSON

```sql
-- JSON (text storage, reparsed on each access)
metadata JSON

-- JSONB (binary storage, faster, indexable, PostgreSQL only)
metadata JSONB

-- When to use JSON:
-- - Flexible schema (user preferences, API responses)
-- - Nested structures
-- - Rarely queried fields
-- - When you need to store entire documents

-- Example with indexing:
CREATE INDEX idx_metadata_tags ON products USING GIN ((metadata->'tags'));

-- Query:
SELECT * FROM products WHERE metadata->'tags' ? 'electronics';
```

## Common Design Patterns

### Soft Delete

```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- Filter in all queries
SELECT * FROM users WHERE deleted_at IS NULL;

-- Partial index for active records
CREATE INDEX idx_active_users ON users(email) WHERE deleted_at IS NULL;

-- "Delete" operation
UPDATE users SET deleted_at = NOW() WHERE id = ?;
```

### Audit Trails

```sql
-- Option 1: Audit columns on every table
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN created_by BIGINT REFERENCES users(id);
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN updated_by BIGINT REFERENCES users(id);

-- Option 2: Separate audit table (full history)
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  table_name VARCHAR(50),
  record_id BIGINT,
  operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
  changed_at TIMESTAMP DEFAULT NOW(),
  changed_by BIGINT,
  old_values JSONB,
  new_values JSONB
);
```

### Multi-Tenancy

```sql
-- Option 1: Shared schema with tenant_id
CREATE TABLE documents (
  id BIGINT PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  title VARCHAR(200),
  content TEXT,

  -- Always filter by tenant_id
  -- CRITICAL: Index on tenant_id
  INDEX idx_tenant_docs (tenant_id, id)
);

-- Row-level security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON documents
  USING (tenant_id = current_tenant_id());

-- Option 2: Separate schema per tenant (PostgreSQL)
CREATE SCHEMA tenant_123;
CREATE TABLE tenant_123.documents (...);

-- Option 3: Separate database per tenant (extreme isolation)
-- CREATE DATABASE tenant_123;
```

### Versioning

```sql
CREATE TABLE documents (
  id BIGINT PRIMARY KEY,
  current_version_id BIGINT,
  title VARCHAR(200)
);

CREATE TABLE document_versions (
  id BIGINT PRIMARY KEY,
  document_id BIGINT REFERENCES documents(id),
  version_number INT,
  title VARCHAR(200),
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  created_by BIGINT,

  UNIQUE (document_id, version_number)
);

-- Point current version
ALTER TABLE documents ADD FOREIGN KEY (current_version_id)
  REFERENCES document_versions(id);
```

## Anti-Patterns

### 1. God Table

```sql
-- ❌ Single table with too many columns
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  username VARCHAR(50),
  email VARCHAR(100),
  -- ... 100 more columns ...
  profile_bio TEXT,
  profile_avatar VARCHAR(255),
  settings_theme VARCHAR(20),
  settings_notifications BOOLEAN
);

-- ✅ Split into logical tables
CREATE TABLE users (id, username, email, ...);
CREATE TABLE user_profiles (user_id, bio, avatar, ...);
CREATE TABLE user_settings (user_id, theme, notifications, ...);
```

### 2. Entity-Attribute-Value (EAV)

```sql
-- ❌ EAV anti-pattern (hard to query, no type safety)
CREATE TABLE object_attributes (
  object_id BIGINT,
  attribute_name VARCHAR(50),
  attribute_value TEXT  -- Everything stored as text!
);

-- ✅ Use JSON or proper columns
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200),
  metadata JSONB  -- Flexible attributes
);
```

### 3. Storing Files in Database

```sql
-- ❌ Storing binary files in database (poor performance)
CREATE TABLE attachments (
  id BIGINT PRIMARY KEY,
  file_data BYTEA  -- Multi-megabyte BLOBs
);

-- ✅ Store file paths/URLs, keep files in object storage
CREATE TABLE attachments (
  id BIGINT PRIMARY KEY,
  file_url VARCHAR(255),  -- S3, CloudFlare, etc.
  file_size_bytes BIGINT,
  mime_type VARCHAR(100)
);
```

---

*Reference file for pact-database-patterns skill*
