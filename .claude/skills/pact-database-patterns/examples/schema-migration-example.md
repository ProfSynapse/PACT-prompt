# Schema Migration Example: Adding Multi-Tenant Support to User Management System

## Context

**Existing System**: Single-tenant user authentication system
**New Requirement**: Support multiple organizations (tenants) with data isolation
**Database**: PostgreSQL 15.2
**Application**: Node.js REST API with Sequelize ORM
**Constraints**: Zero-downtime migration, existing users must continue working

---

## Current Schema (Before Migration)

```sql
-- Existing users table
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Existing user_sessions table
CREATE TABLE user_sessions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
```

**Current Data**: 15,000 users, 3,000 active sessions

---

## Target Schema (After Migration)

```sql
-- New organizations table (tenants)
CREATE TABLE organizations (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL, -- URL-friendly identifier
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_organizations_slug ON organizations(slug);

-- Modified users table with organization_id
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  -- Unique email per organization (not globally unique)
  CONSTRAINT uq_users_org_email UNIQUE (organization_id, email)
);

-- Composite index for tenant-scoped queries
CREATE INDEX idx_users_org_email ON users(organization_id, email);
CREATE INDEX idx_users_organization_id ON users(organization_id);

-- Modified user_sessions table
CREATE TABLE user_sessions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_organization_id ON user_sessions(organization_id);
```

---

## Migration Strategy: Zero-Downtime Approach

### Phase 1: Add New Tables and Columns (No Breaking Changes)

**Migration 001: Create organizations table**
```sql
-- migrations/001_create_organizations.sql
BEGIN;

CREATE TABLE organizations (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_organizations_slug ON organizations(slug);

COMMIT;
```

**Migration 002: Add organization_id to users (nullable initially)**
```sql
-- migrations/002_add_organization_to_users.sql
BEGIN;

-- Add organization_id column (NULL allowed for backward compatibility)
ALTER TABLE users
ADD COLUMN organization_id BIGINT REFERENCES organizations(id) ON DELETE RESTRICT;

-- Create index (partial, only non-NULL values for now)
CREATE INDEX idx_users_organization_id ON users(organization_id)
WHERE organization_id IS NOT NULL;

COMMIT;
```

**Why nullable?** Existing users don't have an organization yet. Application continues working while migration proceeds.

---

### Phase 2: Backfill Data

**Migration 003: Create default organization and assign existing users**
```sql
-- migrations/003_backfill_default_organization.sql
BEGIN;

-- Create default organization for existing users
INSERT INTO organizations (name, slug, created_at, updated_at)
VALUES ('Default Organization', 'default', NOW(), NOW())
RETURNING id;
-- Assume returned id is 1 (adjust based on actual return)

-- Backfill existing users to default organization
-- Do in batches to avoid long locks
UPDATE users
SET organization_id = 1
WHERE organization_id IS NULL
  AND id >= 0 AND id < 5000;

UPDATE users
SET organization_id = 1
WHERE organization_id IS NULL
  AND id >= 5000 AND id < 10000;

UPDATE users
SET organization_id = 1
WHERE organization_id IS NULL
  AND id >= 10000;

COMMIT;
```

**Production Note**: For large tables (millions of rows), use batched updates with monitoring:
```sql
-- Example batched approach
DO $$
DECLARE
  batch_size INT := 1000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET organization_id = 1
    WHERE organization_id IS NULL
      AND id IN (
        SELECT id FROM users
        WHERE organization_id IS NULL
        LIMIT batch_size
      );

    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;

    -- Sleep to avoid overwhelming the database
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

---

### Phase 3: Enforce Constraints

**Migration 004: Make organization_id NOT NULL**
```sql
-- migrations/004_enforce_organization_not_null.sql
BEGIN;

-- Verify all users have organization_id (safety check)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM users WHERE organization_id IS NULL) THEN
    RAISE EXCEPTION 'Found users with NULL organization_id. Backfill incomplete.';
  END IF;
END $$;

-- Make organization_id NOT NULL
ALTER TABLE users
ALTER COLUMN organization_id SET NOT NULL;

COMMIT;
```

**Migration 005: Update unique constraint for email per organization**
```sql
-- migrations/005_update_email_uniqueness.sql
BEGIN;

-- Drop global unique constraint on email
ALTER TABLE users DROP CONSTRAINT users_email_key;

-- Add composite unique constraint (organization_id, email)
ALTER TABLE users
ADD CONSTRAINT uq_users_org_email UNIQUE (organization_id, email);

-- Update index to composite (organization_id, email)
DROP INDEX IF EXISTS idx_users_email;
CREATE INDEX idx_users_org_email ON users(organization_id, email);

COMMIT;
```

---

### Phase 4: Add organization_id to user_sessions

**Migration 006: Add organization_id to sessions (nullable initially)**
```sql
-- migrations/006_add_organization_to_sessions.sql
BEGIN;

-- Add organization_id column
ALTER TABLE user_sessions
ADD COLUMN organization_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE;

-- Create index
CREATE INDEX idx_sessions_organization_id ON user_sessions(organization_id)
WHERE organization_id IS NOT NULL;

COMMIT;
```

**Migration 007: Backfill sessions with organization_id from user**
```sql
-- migrations/007_backfill_sessions_organization.sql
BEGIN;

-- Update sessions to inherit organization_id from user
UPDATE user_sessions us
SET organization_id = u.organization_id
FROM users u
WHERE us.user_id = u.id
  AND us.organization_id IS NULL;

-- Make organization_id NOT NULL after backfill
ALTER TABLE user_sessions
ALTER COLUMN organization_id SET NOT NULL;

COMMIT;
```

---

## Application Code Changes

### Before Migration: Single-Tenant Queries

```javascript
// Before: Global user lookup by email
async function getUserByEmail(email) {
  return await User.findOne({
    where: { email }
  });
}

// Before: Global session lookup
async function getSessionByToken(token) {
  return await Session.findOne({
    where: { token },
    include: [User]
  });
}
```

### After Migration: Multi-Tenant Queries

```javascript
// After: Scoped user lookup by email within organization
async function getUserByEmail(organizationId, email) {
  return await User.findOne({
    where: {
      organization_id: organizationId,
      email
    }
  });
}

// After: Scoped session lookup
async function getSessionByToken(token) {
  const session = await Session.findOne({
    where: { token },
    include: [
      {
        model: User,
        include: [Organization]
      }
    ]
  });

  // Verify session organization matches user organization
  if (session && session.organization_id !== session.User.organization_id) {
    throw new Error('Session organization mismatch');
  }

  return session;
}

// New: Middleware to extract organization from request
async function tenantMiddleware(req, res, next) {
  // Extract organization from subdomain: acme.app.com
  const subdomain = req.hostname.split('.')[0];

  const organization = await Organization.findOne({
    where: { slug: subdomain }
  });

  if (!organization) {
    return res.status(404).json({ error: 'Organization not found' });
  }

  req.organization = organization;
  next();
}
```

---

## Rollback Plan

Each migration includes a rollback script in case of issues:

**Rollback 007: Remove NOT NULL constraint from sessions**
```sql
BEGIN;
ALTER TABLE user_sessions ALTER COLUMN organization_id DROP NOT NULL;
COMMIT;
```

**Rollback 006: Drop organization_id from sessions**
```sql
BEGIN;
DROP INDEX IF EXISTS idx_sessions_organization_id;
ALTER TABLE user_sessions DROP COLUMN organization_id;
COMMIT;
```

**Rollback 005: Restore global email uniqueness**
```sql
BEGIN;
ALTER TABLE users DROP CONSTRAINT uq_users_org_email;
ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
DROP INDEX IF EXISTS idx_users_org_email;
CREATE INDEX idx_users_email ON users(email);
COMMIT;
```

*(Continue for each migration in reverse order)*

---

## Testing Strategy

### 1. Pre-Migration Tests
```javascript
// Verify current behavior before migration
test('users have unique emails globally', async () => {
  const user1 = await createUser({ email: 'test@example.com' });
  await expect(
    createUser({ email: 'test@example.com' })
  ).rejects.toThrow('email already exists');
});
```

### 2. During Migration Tests (Each Phase)
```javascript
// After migration 002: organization_id added but nullable
test('new users can be created without organization', async () => {
  const user = await createUser({ email: 'new@example.com' });
  expect(user.organization_id).toBeNull();
});

// After migration 003: backfill complete
test('all users have organization_id', async () => {
  const usersWithoutOrg = await User.count({
    where: { organization_id: null }
  });
  expect(usersWithoutOrg).toBe(0);
});
```

### 3. Post-Migration Tests
```javascript
// Verify multi-tenant behavior
test('users in different orgs can have same email', async () => {
  const org1 = await createOrg({ slug: 'acme' });
  const org2 = await createOrg({ slug: 'widgetco' });

  const user1 = await createUser({
    organization_id: org1.id,
    email: 'john@company.com'
  });

  const user2 = await createUser({
    organization_id: org2.id,
    email: 'john@company.com'
  });

  expect(user1.id).not.toBe(user2.id);
});

test('users in same org cannot have duplicate email', async () => {
  const org = await createOrg({ slug: 'acme' });

  await createUser({
    organization_id: org.id,
    email: 'john@acme.com'
  });

  await expect(
    createUser({
      organization_id: org.id,
      email: 'john@acme.com'
    })
  ).rejects.toThrow('email already exists');
});
```

---

## Key Decisions

### 1. Organization Identifier: Slug vs ID in URL
**Decision**: Use slug (e.g., `acme.app.com` or `/acme/dashboard`)
**Rationale**: User-friendly, memorable URLs; slug lookup performance is acceptable with index
**Trade-off**: Slug uniqueness constraint adds complexity for renames (handle via redirect table if needed)

### 2. Email Uniqueness: Global vs Per-Organization
**Decision**: Per-organization (composite unique constraint)
**Rationale**: Users may exist in multiple organizations with same email (e.g., consultant working with multiple clients)
**Trade-off**: More complex user lookup (must include organization_id), but aligns with SaaS model

### 3. Foreign Key Cascade: RESTRICT vs CASCADE
**Decision**: Organizations use `ON DELETE RESTRICT`
**Rationale**: Prevent accidental deletion of organization with active users; requires explicit cleanup process
**Trade-off**: Cannot delete organization without first deleting users (intentional safety measure)

---

## Performance Considerations

### Index Strategy
```sql
-- Composite index for most common query pattern
CREATE INDEX idx_users_org_email ON users(organization_id, email);

-- Covers query:
SELECT * FROM users WHERE organization_id = ? AND email = ?;
```

### Query Optimization
```javascript
// GOOD: Filter by organization_id first (most selective)
SELECT * FROM users
WHERE organization_id = 123
  AND role = 'admin'
  AND created_at > '2024-01-01';

// BAD: Filter without organization_id (scans all organizations)
SELECT * FROM users
WHERE email = 'user@example.com'; -- Missing organization_id context
```

---

## Common Pitfalls Avoided

1. **Not making organization_id nullable initially**: Would break existing application during deployment
2. **Forgetting to update indexes**: Composite indexes on (organization_id, ...) are critical for performance
3. **Orphaned sessions after backfill**: Ensured sessions inherit organization_id from user
4. **No rollback plan**: Each migration has tested rollback script
5. **Application code updated before schema**: Schema supports both old and new code during transition

---

*Example from pact-database-patterns skill - Zero-downtime schema migration workflow*
