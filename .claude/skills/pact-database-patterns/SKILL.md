---
name: pact-database-patterns
description: |
  CODE PHASE (Database): Data layer implementation patterns and best practices.

  Provides schema design patterns, query optimization strategies, indexing guidelines,
  data integrity constraints, migration patterns, and database security practices.

  Use when: designing schemas, writing queries, optimizing performance, planning
  migrations, implementing data validation, ensuring data integrity.
allowed-tools:
  - Read
  - Bash
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Code"
  version: "1.0.0"
  primary-agent: "pact-database-engineer"
---

# Database Implementation Patterns Skill

Database implementation patterns and best practices for the CODE phase of PACT framework.

## Quick Reference

### Schema Design Decision Tree

```
Is this a new table?
├─ YES → Start with 3NF normalization
│   ├─ High read frequency (>80% reads)?
│   │   └─ Consider selective denormalization for hot paths
│   └─ High write frequency (>80% writes)?
│       └─ Keep normalized, optimize with indexes
└─ NO → Extending existing table?
    ├─ Adding columns → Check NULL handling strategy
    ├─ Changing columns → Plan migration strategy
    └─ Removing columns → Implement soft deprecation first

Data type selection:
├─ Identifiers → BIGINT (future-proof) or UUID (distributed)
├─ Timestamps → TIMESTAMP WITH TIME ZONE (always)
├─ Money → DECIMAL(19,4) (never FLOAT)
├─ Text → VARCHAR with explicit limits (avoid TEXT unless needed)
└─ Boolean → BOOLEAN (not TINYINT or CHAR)
```

### Normalization Guidelines

**First Normal Form (1NF)**
- Atomic values only (no arrays in columns)
- Each column contains single value type
- Unique column names
- Order doesn't matter

**Second Normal Form (2NF)**
- Already in 1NF
- No partial dependencies on composite keys
- All non-key attributes depend on entire primary key

**Third Normal Form (3NF)**
- Already in 2NF
- No transitive dependencies
- Non-key attributes depend only on primary key

**When to Denormalize**
- Read-heavy queries accessing multiple tables (proven by metrics)
- Aggregation calculations performed frequently (>1000x/day)
- Historical snapshots needed for audit/compliance
- **Always document the performance justification**

### Index Strategy Cheat Sheet

**Always Index**
- Primary keys (automatic in most RDBMS)
- Foreign keys (not automatic in all RDBMS)
- Columns in WHERE clauses (high selectivity)
- Columns in JOIN conditions
- Columns in ORDER BY (if used frequently)

**Consider Indexing**
- Columns in GROUP BY
- Columns with high cardinality (many unique values)
- Frequently filtered date ranges

**Never Index**
- Small tables (<1000 rows)
- Columns with low cardinality (gender, boolean)
- Frequently updated columns (index maintenance cost)
- Wide text columns (use full-text search instead)

**Composite Index Guidelines**
```sql
-- Order matters! Most selective first
CREATE INDEX idx_user_activity
ON user_events(user_id, event_type, created_at);

-- This query uses the index efficiently:
WHERE user_id = ? AND event_type = ? AND created_at > ?

-- This query only uses first part:
WHERE user_id = ?

-- This query CANNOT use the index:
WHERE event_type = ? AND created_at > ?
```

**Index Types Quick Guide**
- **B-Tree** (default): Equality, range queries, sorting
- **Hash**: Equality only, faster than B-Tree for exact matches
- **GIN/GiST**: Full-text search, JSON, arrays, geometric data
- **Partial**: Index subset of rows (e.g., WHERE deleted_at IS NULL)
- **Covering**: Include extra columns to avoid table lookup

### Query Optimization Checklist

**Before Writing Queries**
- [ ] Understand the access pattern (read/write ratio)
- [ ] Know the data volume (current and projected)
- [ ] Identify the most selective filter (start here)
- [ ] Plan JOIN order (smallest result set first)

**While Writing Queries**
- [ ] Use explicit JOIN syntax (not implicit comma joins)
- [ ] Filter early (WHERE before JOIN when possible)
- [ ] Avoid SELECT * (specify needed columns)
- [ ] Use appropriate JOIN type (INNER vs LEFT vs RIGHT)
- [ ] Consider EXISTS vs IN for subqueries
- [ ] Limit result sets with WHERE, not application code

**After Writing Queries**
- [ ] Run EXPLAIN/EXPLAIN ANALYZE
- [ ] Check for sequential scans on large tables
- [ ] Verify index usage on JOIN conditions
- [ ] Look for nested loops on large datasets
- [ ] Ensure cardinality estimates are accurate
- [ ] Test with production-like data volume

**Common Anti-Patterns to Avoid**
```sql
-- ❌ N+1 Query Problem
SELECT * FROM users;
-- Then for each user:
SELECT * FROM orders WHERE user_id = ?;

-- ✅ Use JOIN instead
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- ❌ Function on indexed column prevents index use
WHERE YEAR(created_at) = 2024

-- ✅ Rewrite to preserve index
WHERE created_at >= '2024-01-01'
  AND created_at < '2025-01-01'

-- ❌ OR on different columns prevents index use
WHERE email = ? OR username = ?

-- ✅ Use UNION if both columns are indexed
SELECT * FROM users WHERE email = ?
UNION
SELECT * FROM users WHERE username = ?

-- ❌ Implicit type conversion
WHERE user_id = '123'  -- user_id is INT

-- ✅ Use correct type
WHERE user_id = 123
```

### Data Integrity Patterns

**Constraint Hierarchy**
1. **NOT NULL**: Required fields
2. **UNIQUE**: Enforce uniqueness at DB level
3. **CHECK**: Business rule validation
4. **FOREIGN KEY**: Referential integrity
5. **PRIMARY KEY**: Combines NOT NULL + UNIQUE

**Referential Integrity Actions**
```sql
-- Prevent deletion if referenced
ON DELETE RESTRICT  -- Default, explicit is better

-- Delete dependent rows automatically
ON DELETE CASCADE  -- Use carefully, can cascade widely

-- Set FK to NULL when parent deleted
ON DELETE SET NULL  -- Parent must allow NULL

-- Prevent orphans without cascade
ON DELETE NO ACTION  -- Similar to RESTRICT
```

**Soft Delete Pattern**
```sql
-- Add columns
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE users ADD COLUMN deleted_by BIGINT;

-- Create partial index for active records only
CREATE INDEX idx_active_users
ON users(email)
WHERE deleted_at IS NULL;

-- Queries always filter
SELECT * FROM users WHERE deleted_at IS NULL;

-- Instead of DELETE
UPDATE users
SET deleted_at = NOW(), deleted_by = ?
WHERE id = ?;
```

**Audit Trail Pattern**
```sql
-- Audit table captures all changes
CREATE TABLE user_audit (
  audit_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  operation CHAR(1) NOT NULL,  -- I, U, D
  changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_by BIGINT,
  old_values JSONB,
  new_values JSONB
);

-- Trigger to populate audit table
CREATE TRIGGER user_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_user_changes();
```

### Migration Patterns

**Zero-Downtime Migration Strategy**
1. **Additive changes first**: Add new columns/tables
2. **Dual write**: Write to both old and new schema
3. **Backfill data**: Populate new schema from old
4. **Dual read**: Read from new schema with fallback
5. **Remove old schema**: After validation period

**Safe Column Addition**
```sql
-- Step 1: Add column with default (fast, no rewrite)
ALTER TABLE users
ADD COLUMN status VARCHAR(20) DEFAULT 'active' NOT NULL;

-- Step 2: Update existing rows if needed (in batches)
UPDATE users
SET status = CASE
  WHEN email_verified THEN 'active'
  ELSE 'pending'
END
WHERE id >= ? AND id < ?;

-- Step 3: Remove default after backfill (allows NULLs for new rows)
ALTER TABLE users ALTER COLUMN status DROP DEFAULT;
```

**Safe Column Removal**
```sql
-- Step 1: Stop writing to column (code deploy)
-- Step 2: Wait 1+ deployment cycles
-- Step 3: Drop column (can cause table rewrite in some RDBMS)
ALTER TABLE users DROP COLUMN old_field;
```

**Renaming Strategy**
```sql
-- Don't rename! Instead:
-- 1. Add new column
-- 2. Dual write to both
-- 3. Backfill
-- 4. Switch reads
-- 5. Remove old column

-- If you must rename immediately (small table):
BEGIN;
ALTER TABLE users RENAME COLUMN old_name TO new_name;
-- Update all application code simultaneously
COMMIT;
```

### Transaction Management

**ACID Review**
- **Atomicity**: All or nothing
- **Consistency**: Valid state transitions
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data survives crashes

**Isolation Levels** (from weakest to strongest)
```sql
-- Read Uncommitted: Dirty reads possible
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Read Committed: Most common default
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Repeatable Read: Prevents non-repeatable reads
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Serializable: Strongest, can cause deadlocks
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

**Transaction Best Practices**
- Keep transactions as short as possible
- Acquire locks in consistent order (prevent deadlocks)
- Don't perform I/O inside transactions
- Use appropriate isolation level (not always serializable)
- Handle deadlocks with retry logic

**Deadlock Prevention**
```sql
-- ❌ Can deadlock if two processes reverse order
-- Process A:
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Process B:
UPDATE accounts SET balance = balance - 50 WHERE id = 2;
UPDATE accounts SET balance = balance + 50 WHERE id = 1;

-- ✅ Always lock in same order (by ID)
UPDATE accounts SET balance = balance + CASE
  WHEN id = 1 THEN -100
  WHEN id = 2 THEN 100
END
WHERE id IN (1, 2)
ORDER BY id;  -- Consistent lock order
```

### Security Best Practices

**Access Control**
```sql
-- Principle of least privilege
CREATE ROLE app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

CREATE ROLE app_readwrite;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;

-- Never grant DELETE to application roles
-- Deletions should go through admin processes or soft delete
```

**Row-Level Security (RLS)**
```sql
-- Enable RLS on table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: users see only their own documents
CREATE POLICY user_documents ON documents
FOR SELECT
USING (user_id = current_user_id());

-- Policy: admins see everything
CREATE POLICY admin_documents ON documents
FOR ALL
USING (is_admin());
```

**Data Encryption**
- Encrypt sensitive data at rest (database level)
- Encrypt in transit (SSL/TLS connections)
- Never store passwords in plain text (use bcrypt, argon2)
- Store API keys in encrypted columns
- Consider field-level encryption for PII

**SQL Injection Prevention**
```sql
-- ❌ NEVER construct queries with string concatenation
query = "SELECT * FROM users WHERE email = '" + user_input + "'"

-- ✅ ALWAYS use parameterized queries
query = "SELECT * FROM users WHERE email = ?"
params = [user_input]
```

### Performance Monitoring

**Key Metrics to Track**
- Query execution time (p50, p95, p99)
- Slow query log (queries >100ms)
- Connection pool utilization
- Cache hit ratio (>90% ideal)
- Index usage statistics
- Table bloat (vacuum effectiveness)
- Lock wait times
- Deadlock frequency

**Query Analysis**
```sql
-- PostgreSQL: Find slow queries
SELECT
  calls,
  total_time,
  mean_time,
  query
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;  -- 100ms

-- Check index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,  -- Number of index scans
  idx_tup_read  -- Number of index entries returned
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

## When to Use Sequential Thinking

Database design often requires deep reasoning about trade-offs. Use the `mcp__sequential-thinking__sequentialthinking` tool when:

**Schema Design Decisions**
- Evaluating normalization vs denormalization trade-offs
- Choosing between different data modeling approaches
- Deciding on partitioning strategies for large tables
- Planning complex migration paths

**Performance Optimization**
- Analyzing query execution plans with multiple optimization options
- Designing composite indexes with multiple column orderings
- Evaluating caching strategies vs query optimization
- Balancing read performance vs write performance

**Data Integrity Design**
- Designing constraint strategies that balance integrity and flexibility
- Planning soft delete vs hard delete implications
- Evaluating cascade delete vs manual cleanup approaches

**Transaction Design**
- Choosing appropriate isolation levels for complex business logic
- Designing retry strategies for deadlock scenarios
- Planning distributed transaction patterns

**Example Sequential Thinking Prompt**
```
I need to design a schema for a multi-tenant SaaS application with these requirements:
- 1000+ tenants, average 10k records per tenant
- Strong data isolation between tenants required for compliance
- 90% of queries filter by tenant_id
- Need to support per-tenant schema customization in the future

Should I use:
1. Shared schema with tenant_id column
2. Separate schema per tenant
3. Separate database per tenant

Walk through the trade-offs of each approach considering:
- Query performance and indexing
- Data isolation and security
- Operational complexity
- Future extensibility
- Cost at scale
```

## MCP Tools for Database Design

This section provides guidance on WHEN and WHY to use MCP tools during database implementation. See agent documentation for invocation syntax.

### Available MCP Tools

The following MCP tool enhances database design decisions:
- **sequential-thinking**: Complex schema design and data modeling trade-offs

---

### sequential-thinking

**Purpose**: Extended reasoning capability for complex database design decisions

**When to use**:
- Evaluating normalization vs denormalization trade-offs for specific access patterns (e.g., balancing query performance vs data consistency for reporting tables)
- Choosing between different data modeling approaches for complex domains (e.g., multi-tenant SaaS schema: shared table with tenant_id vs schema-per-tenant vs database-per-tenant)
- Designing partitioning strategies for large tables with competing access patterns (e.g., time-based vs hash-based partitioning for logs with both time-range and user-based queries)
- Planning complex migration paths with zero-downtime requirements (e.g., column rename across distributed services with gradual rollout)
- Designing composite index strategies with multiple column orderings (e.g., optimizing for conflicting query patterns on same table)
- Evaluating transaction isolation levels for complex business workflows (e.g., balancing consistency vs performance for inventory management)
- Planning distributed transaction patterns across microservices

**When NOT to use**:
- Standard normalized schema design following well-known domain patterns
- Adding straightforward indexes based on query analysis
- Simple data type selection with clear requirements
- Routine database maintenance tasks (vacuuming, reindexing)
- Well-documented migration patterns (adding nullable column)

**Value for database coding**: Transparent reasoning about schema trade-offs creates documentation for future optimization decisions. Prevents costly migrations from poorly considered initial design. Reduces production incidents from transaction isolation issues.

**Integration approach**: Review data model from architecture phase → Identify complex schema or performance decision → Use sequential-thinking to evaluate query patterns, consistency requirements, and scaling implications → Implement with documented rationale → Create performance baselines for reasoned optimizations.

**See pact-database-engineer agent for invocation syntax and workflow integration.**

---

## Reference Files

Detailed patterns and examples available in:

- **schema-design.md**: Normalization, denormalization, relationships, data types
- **query-optimization.md**: Indexes, query plans, performance tuning, caching
- **data-integrity.md**: Constraints, transactions, validation, audit trails

## Integration with PACT Workflow

This skill supports the **CODE phase** for database implementation:

**Input from ARCHITECT Phase**
- Entity-relationship diagrams
- Data model specifications
- Access pattern requirements
- Performance SLAs
- Security requirements

**Output for TEST Phase**
- Database schema DDL scripts
- Sample data DML scripts
- Query examples for common access patterns
- Index definitions with justification
- Migration scripts
- Performance baseline metrics

**Quality Gates**
- All tables have primary keys
- All foreign keys have indexes
- All queries have EXPLAIN plans reviewed
- All migrations tested on copy of production data
- All sensitive data has encryption plan
- All access patterns have appropriate indexes

## Common Pitfalls

**Design Pitfalls**
- Over-normalization causing excessive JOINs
- Under-normalization causing data anomalies
- Using wrong data types (especially for money, dates)
- Not planning for NULL handling
- Forgetting time zone handling

**Implementation Pitfalls**
- Adding indexes without measuring impact
- Not testing migrations on production-size data
- Using SELECT * in application code
- Not handling transaction deadlocks
- Performing I/O operations inside transactions

**Security Pitfalls**
- Granting excessive permissions to application users
- Not encrypting sensitive data at rest
- Using string concatenation for queries (SQL injection)
- Logging sensitive data in plain text
- Not implementing row-level security for multi-tenant apps

**Performance Pitfalls**
- Not analyzing query execution plans
- Creating too many indexes (write performance suffers)
- Using functions on indexed columns in WHERE clauses
- Not batching large updates
- Not monitoring connection pool exhaustion

## Success Criteria

A well-implemented database solution demonstrates:

1. **Data Integrity**: Constraints enforce business rules at DB level
2. **Performance**: Query response times meet SLAs (usually <100ms)
3. **Security**: Least privilege access, encryption for sensitive data
4. **Maintainability**: Clear schema documentation, standard patterns
5. **Scalability**: Design handles 10x current data volume
6. **Reliability**: Backup/recovery tested, transaction handling robust
7. **Observability**: Query performance monitored, slow queries identified

---

*This skill is part of the PACT Framework for principled AI-assisted development.*
