# Query Optimization Reference

Comprehensive guide to database query optimization, indexing strategies, and performance tuning.

## Table of Contents

1. [Index Fundamentals](#index-fundamentals)
2. [Query Execution Plans](#query-execution-plans)
3. [JOIN Optimization](#join-optimization)
4. [Subquery Optimization](#subquery-optimization)
5. [Aggregation Performance](#aggregation-performance)
6. [Caching Strategies](#caching-strategies)

## Index Fundamentals

### Index Types

#### B-Tree Indexes (Default)

**Best For**
- Equality comparisons (`=`)
- Range queries (`<`, `>`, `BETWEEN`)
- Sorting (`ORDER BY`)
- Pattern matching with prefix (`LIKE 'prefix%'`)

**Structure**
```
Balanced tree with sorted keys
Root → Internal Nodes → Leaf Nodes (contain actual data pointers)
Height typically 3-4 levels even for millions of rows
```

**Example**
```sql
-- B-Tree index (default type)
CREATE INDEX idx_users_email ON users(email);

-- Efficient queries:
SELECT * FROM users WHERE email = 'user@example.com';  -- Equality
SELECT * FROM users WHERE email > 'a@example.com';     -- Range
SELECT * FROM users ORDER BY email LIMIT 10;           -- Sorting
SELECT * FROM users WHERE email LIKE 'admin%';         -- Prefix match

-- NOT efficient with this index:
SELECT * FROM users WHERE email LIKE '%@gmail.com';    -- Suffix match
```

#### Hash Indexes

**Best For**
- Equality comparisons only (`=`)
- Faster than B-Tree for exact matches
- Not available in all RDBMS (PostgreSQL has them, MySQL doesn't use them much)

**Limitations**
- Cannot handle range queries
- Cannot be used for sorting
- Cannot be used for partial matches

**Example**
```sql
-- PostgreSQL hash index
CREATE INDEX idx_users_username_hash ON users USING HASH (username);

-- Efficient:
SELECT * FROM users WHERE username = 'john_doe';

-- NOT efficient (can't use hash index):
SELECT * FROM users WHERE username > 'john_doe';
SELECT * FROM users ORDER BY username;
```

#### GIN (Generalized Inverted Index)

**Best For**
- Full-text search
- Array containment queries
- JSONB queries
- PostgreSQL specific

**Example**
```sql
-- Full-text search
CREATE INDEX idx_articles_search ON articles USING GIN (to_tsvector('english', body));

SELECT * FROM articles
WHERE to_tsvector('english', body) @@ to_tsquery('database & optimization');

-- JSONB queries
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);

SELECT * FROM products WHERE metadata @> '{"category": "electronics"}';
SELECT * FROM products WHERE metadata ? 'tags';  -- Key exists
```

#### Partial Indexes

**Best For**
- Indexing subset of rows
- Smaller index size
- Faster index maintenance

**Example**
```sql
-- Only index active users (where deleted_at IS NULL)
CREATE INDEX idx_active_users_email
ON users(email)
WHERE deleted_at IS NULL;

-- Index only recent orders
CREATE INDEX idx_recent_orders
ON orders(customer_id, created_at)
WHERE created_at > NOW() - INTERVAL '90 days';

-- Smaller index, faster queries for common case
```

#### Covering Indexes (Index-Only Scans)

**Best For**
- Queries that can be satisfied entirely from index
- Avoiding table lookups

**Example**
```sql
-- Query needs: user_id, email, created_at
CREATE INDEX idx_users_covering
ON users(email) INCLUDE (created_at);

-- This query can be satisfied entirely from index (no table access)
SELECT user_id, email, created_at
FROM users
WHERE email = 'user@example.com';

-- PostgreSQL version:
CREATE INDEX idx_users_covering
ON users(email) INCLUDE (created_at);

-- MySQL version (include columns in index):
CREATE INDEX idx_users_covering
ON users(email, created_at);
```

### Composite Index Design

**Column Order Matters!**

```sql
-- Index on (A, B, C)
CREATE INDEX idx_abc ON table(a, b, c);

-- Can efficiently support:
WHERE a = ?
WHERE a = ? AND b = ?
WHERE a = ? AND b = ? AND c = ?
WHERE a = ? AND b > ?
WHERE a = ? ORDER BY b

-- CANNOT efficiently support:
WHERE b = ?                    -- Doesn't start with 'a'
WHERE b = ? AND c = ?          -- Doesn't start with 'a'
WHERE a = ? AND c = ?          -- Skips 'b', can use 'a' but not 'c'
```

**Designing Composite Indexes**

1. **Equality first, range second**
```sql
-- Query: WHERE status = ? AND created_at > ?
CREATE INDEX idx_status_date ON orders(status, created_at);
-- NOT: (created_at, status) -- less efficient
```

2. **Most selective first (when all equality)**
```sql
-- If user_id is very selective (few orders per user)
-- But status is not selective (only 5 possible values)
CREATE INDEX idx_user_status ON orders(user_id, status);
```

3. **Match your query patterns**
```sql
-- Frequent query: WHERE tenant_id = ? ORDER BY created_at DESC
CREATE INDEX idx_tenant_created ON documents(tenant_id, created_at DESC);
```

### Index Maintenance

```sql
-- PostgreSQL: Check index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS scans,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;  -- Indexes with low scans might be unused

-- Find unused indexes (0 scans)
SELECT
  schemaname || '.' || tablename AS table,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_toast%';

-- MySQL: Check index usage
SELECT
  OBJECT_SCHEMA,
  OBJECT_NAME,
  INDEX_NAME,
  COUNT_STAR AS queries_using_index
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE INDEX_NAME IS NOT NULL
ORDER BY COUNT_STAR ASC;

-- Rebuild fragmented indexes (PostgreSQL)
REINDEX INDEX idx_users_email;
REINDEX TABLE users;  -- All indexes on table

-- MySQL
ALTER TABLE users ENGINE=InnoDB;  -- Rebuilds table and indexes
```

## Query Execution Plans

### Reading EXPLAIN Output

#### PostgreSQL EXPLAIN

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name;
```

**Key Metrics to Check**
- **Seq Scan**: Full table scan (bad for large tables)
- **Index Scan**: Using index (good)
- **Index Only Scan**: Satisfied from index alone (best)
- **Nested Loop**: Good for small result sets
- **Hash Join**: Good for large result sets
- **Merge Join**: Good when both inputs are sorted
- **Cost**: Estimated cost (not time, relative units)
- **Rows**: Estimated rows (compare to actual)
- **Actual Time**: Real execution time (EXPLAIN ANALYZE only)

**Example Output**
```
Hash Join  (cost=234.56..1234.78 rows=100 width=64) (actual time=12.34..56.78 rows=95 loops=1)
  Hash Cond: (o.user_id = u.id)
  ->  Seq Scan on orders o  (cost=0.00..1000.00 rows=50000 width=16)
  ->  Hash  (cost=200.00..200.00 rows=100 width=52)
        ->  Index Scan using idx_users_created on users u  (cost=0.29..200.00 rows=100 width=52)
              Index Cond: (created_at > '2024-01-01')

Planning Time: 0.5 ms
Execution Time: 57.0 ms
```

**Red Flags**
- Seq Scan on large tables (>10k rows)
- Actual rows >> estimated rows (statistics out of date)
- High execution time on simple queries (>100ms)
- Nested Loop with large row counts (>1000)

#### MySQL EXPLAIN

```sql
EXPLAIN
SELECT u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;
```

**Key Columns**
- **type**: Join type (const > eq_ref > ref > range > index > ALL)
  - `const`: Single row (primary key lookup)
  - `eq_ref`: One row per join (best for joins)
  - `ref`: Multiple rows matching index
  - `range`: Index range scan
  - `index`: Full index scan
  - `ALL`: Full table scan (avoid for large tables)
- **possible_keys**: Indexes that could be used
- **key**: Index actually used
- **rows**: Estimated rows examined
- **Extra**: Important additional info
  - `Using index`: Covering index (good)
  - `Using where`: Filtering after retrieval (okay)
  - `Using filesort`: Sort not using index (can be expensive)
  - `Using temporary`: Temporary table created (can be expensive)

### Optimizing Based on EXPLAIN

**Problem: Sequential Scan**
```sql
-- Query
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- Output shows: Seq Scan on users

-- Solution: Add index
CREATE INDEX idx_users_email ON users(email);
```

**Problem: Index Not Used**
```sql
-- Query
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- Output shows: Seq Scan (index on email not used due to function)

-- Solution: Create functional index
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Or rewrite query to avoid function
CREATE INDEX idx_users_email ON users(email);
-- Query: SELECT * FROM users WHERE email = LOWER('user@example.com');
```

**Problem: Wrong Index Chosen**
```sql
-- Sometimes optimizer chooses wrong index
EXPLAIN SELECT * FROM orders
WHERE customer_id = 123 AND status = 'pending';

-- Force specific index (use sparingly)
SELECT * FROM orders USE INDEX (idx_customer_status)
WHERE customer_id = 123 AND status = 'pending';

-- PostgreSQL: Disable specific scan types to test
SET enable_seqscan = OFF;  -- Force index usage for testing
-- Remember to turn back on!
SET enable_seqscan = ON;
```

## JOIN Optimization

### JOIN Type Selection

```sql
-- INNER JOIN: Only matching rows
SELECT o.id, u.name
FROM orders o
INNER JOIN users u ON o.user_id = u.id;

-- LEFT JOIN: All rows from left table
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- RIGHT JOIN: Rarely used (rewrite as LEFT JOIN)
-- FULL OUTER JOIN: All rows from both tables (rare)
```

### JOIN Order Optimization

**Principle**: Join smallest result sets first

```sql
-- ❌ Inefficient: Large table first
SELECT *
FROM orders o
INNER JOIN order_items oi ON o.id = oi.order_id
WHERE o.created_at > '2024-01-01';

-- ✅ Better: Filter first, then join
SELECT *
FROM (
  SELECT * FROM orders WHERE created_at > '2024-01-01'
) o
INNER JOIN order_items oi ON o.id = oi.order_id;

-- ✅ Even better: Let optimizer handle it with proper indexes
CREATE INDEX idx_orders_created ON orders(created_at);
-- Query optimizer will filter before joining
```

### JOIN Algorithm Selection

**Nested Loop Join**
- Good for small result sets
- Efficient when inner table has index on join column
- O(N * M) without index, O(N * log M) with index

**Hash Join**
- Good for large result sets
- Builds hash table of smaller table
- O(N + M) complexity
- Requires memory for hash table

**Merge Join**
- Good when both inputs are already sorted
- O(N + M) complexity
- Requires sorted inputs

**Example**
```sql
-- Small result set: Nested Loop is efficient
SELECT * FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.id = 123;  -- Returns 1 user

-- Large result set: Hash Join is efficient
SELECT * FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01';  -- Returns 100k users
```

### Multiple JOIN Optimization

```sql
-- ❌ Inefficient: Multiple separate queries (N+1 problem)
SELECT * FROM users;
-- Then for each user:
SELECT * FROM orders WHERE user_id = ?;
-- Then for each order:
SELECT * FROM order_items WHERE order_id = ?;

-- ✅ Efficient: Single query with JOINs
SELECT
  u.id, u.name,
  o.id as order_id, o.total,
  oi.id as item_id, oi.product_name, oi.quantity
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE u.created_at > '2024-01-01';
```

## Subquery Optimization

### EXISTS vs IN

```sql
-- EXISTS: Stops at first match (efficient for large subqueries)
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- IN: Evaluates entire subquery (efficient for small subqueries)
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders);

-- NOT EXISTS: Usually faster than NOT IN
SELECT * FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- NOT IN: Can give wrong results with NULL values!
SELECT * FROM users
WHERE id NOT IN (SELECT user_id FROM orders);
-- If any user_id in orders is NULL, returns no rows!
```

### Correlated vs Non-Correlated Subqueries

```sql
-- ❌ Correlated subquery: Executes for each outer row
SELECT
  u.name,
  (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u;
-- Executes orders subquery once per user

-- ✅ Better: Non-correlated with JOIN
SELECT
  u.name,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- ✅ Or: Lateral join (PostgreSQL, MySQL 8.0+)
SELECT u.name, o.order_count
FROM users u
LEFT JOIN LATERAL (
  SELECT COUNT(*) as order_count
  FROM orders
  WHERE user_id = u.id
) o ON true;
```

### Common Table Expressions (CTEs)

```sql
-- CTEs make complex queries more readable
WITH recent_orders AS (
  SELECT user_id, COUNT(*) as order_count
  FROM orders
  WHERE created_at > NOW() - INTERVAL '30 days'
  GROUP BY user_id
),
high_value_users AS (
  SELECT user_id
  FROM recent_orders
  WHERE order_count > 10
)
SELECT u.name, ro.order_count
FROM users u
JOIN high_value_users hvu ON u.id = hvu.user_id
JOIN recent_orders ro ON u.id = ro.user_id;

-- Materialized CTEs (PostgreSQL): Computed once
WITH materialized_cte AS MATERIALIZED (
  SELECT expensive_calculation()
)
SELECT * FROM materialized_cte;
```

## Aggregation Performance

### GROUP BY Optimization

```sql
-- ✅ Group by indexed columns
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

SELECT user_id, status, COUNT(*)
FROM orders
GROUP BY user_id, status;  -- Uses index efficiently

-- ❌ Avoid grouping by expressions
SELECT DATE(created_at), COUNT(*)
FROM orders
GROUP BY DATE(created_at);  -- Function prevents index use

-- ✅ Better: Create computed column or index on expression
CREATE INDEX idx_orders_date ON orders((DATE(created_at)));
-- Or: Add a date column updated by trigger
```

### HAVING vs WHERE

```sql
-- ❌ HAVING filters after aggregation (processes more rows)
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING user_id > 1000;

-- ✅ WHERE filters before aggregation (more efficient)
SELECT user_id, COUNT(*) as order_count
FROM orders
WHERE user_id > 1000
GROUP BY user_id;

-- HAVING is correct for filtering aggregated results
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 10;  -- Can't move to WHERE
```

### Window Functions

```sql
-- Efficient for running totals, rankings
SELECT
  id,
  user_id,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at) as running_total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) as rank
FROM orders;

-- More efficient than correlated subqueries for this use case
```

## Caching Strategies

### Query Result Caching

**Application-Level Cache**
```python
# Pseudocode
def get_user_orders(user_id):
  cache_key = f"user_orders:{user_id}"
  cached = redis.get(cache_key)
  if cached:
    return cached

  result = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
  redis.setex(cache_key, 3600, result)  # Cache for 1 hour
  return result
```

**Database Query Cache** (MySQL)
```sql
-- MySQL query cache (deprecated in 8.0, use alternative caching)
-- Caches identical queries
SELECT SQL_CACHE * FROM users WHERE id = 123;
```

### Materialized Views

```sql
-- PostgreSQL: Materialized view (pre-computed query)
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
  DATE(created_at) as sale_date,
  COUNT(*) as order_count,
  SUM(total_amount) as total_revenue
FROM orders
GROUP BY DATE(created_at);

-- Create index on materialized view
CREATE INDEX idx_daily_sales_date ON daily_sales_summary(sale_date);

-- Refresh periodically (not real-time)
REFRESH MATERIALIZED VIEW daily_sales_summary;

-- Concurrent refresh (doesn't lock view)
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales_summary;
```

### Read Replicas

```
Primary DB (writes) → Replication → Read Replicas (reads)

Application:
- Send all writes to primary
- Send all reads to replicas
- Handle replication lag (eventual consistency)
```

**When to Use**
- Read-heavy workloads (>80% reads)
- Reporting queries that don't need real-time data
- Geographical distribution

### Connection Pooling

```sql
-- Without pooling: New connection for every query (slow)
-- Connect (TCP handshake, auth, etc.) → Query → Disconnect

-- With pooling: Reuse connections (fast)
-- Pool maintains N open connections
-- Application borrows → Query → Returns to pool

-- Configuration example (pgBouncer, HikariCP, etc.):
pool_size = 20  -- Number of connections
max_overflow = 10  -- Extra connections if pool exhausted
timeout = 30  -- Wait time for connection from pool
```

---

*Reference file for pact-database-patterns skill*
