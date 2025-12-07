# Database Schema Design Template

## Schema: [Schema/Domain Name]

### Overview
- **Database**: [PostgreSQL | MySQL | MongoDB | etc.]
- **Purpose**: [What this schema stores]
- **Owner**: [Team responsible]

---

## Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│     [Entity1]    │       │     [Entity2]    │
├──────────────────┤       ├──────────────────┤
│ id (PK)          │───┐   │ id (PK)          │
│ name             │   │   │ entity1_id (FK)  │◄──┘
│ created_at       │   └──►│ name             │
│ updated_at       │       │ created_at       │
└──────────────────┘       └──────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐
│     [Entity3]    │
├──────────────────┤
│ id (PK)          │
│ entity1_id (FK)  │
│ value            │
│ created_at       │
└──────────────────┘
```

---

## Table Definitions

### [table_name]

```sql
CREATE TABLE [table_name] (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    [related]_id UUID NOT NULL REFERENCES [related_table](id),

    -- Business Fields
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',

    -- JSON Fields (if needed)
    metadata JSONB DEFAULT '{}',

    -- Audit Fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ, -- Soft delete

    -- Constraints
    CONSTRAINT [table]_email_unique UNIQUE (email),
    CONSTRAINT [table]_status_check CHECK (status IN ('active', 'inactive', 'pending'))
);

-- Indexes
CREATE INDEX idx_[table]_[field] ON [table_name]([field]);
CREATE INDEX idx_[table]_created_at ON [table_name](created_at DESC);
CREATE INDEX idx_[table]_status ON [table_name](status) WHERE deleted_at IS NULL;

-- Partial index for soft delete
CREATE INDEX idx_[table]_active ON [table_name](id) WHERE deleted_at IS NULL;

-- Trigger for updated_at
CREATE TRIGGER update_[table]_updated_at
    BEFORE UPDATE ON [table_name]
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Indexes Strategy

| Table | Index Name | Columns | Type | Purpose |
|-------|-----------|---------|------|---------|
| [table] | idx_[table]_[field] | [field] | BTREE | [Query pattern] |
| [table] | idx_[table]_composite | [field1, field2] | BTREE | [Query pattern] |
| [table] | idx_[table]_search | [field] | GIN | Full-text search |

---

## Migrations Checklist

### Pre-Migration
- [ ] Backup database
- [ ] Test migration on staging
- [ ] Estimate downtime (if any)
- [ ] Notify stakeholders

### Migration Safety
- [ ] Migration is reversible (has down migration)
- [ ] No data loss in rollback
- [ ] Handles existing data
- [ ] Concurrent-safe (no locks on hot tables)

### Post-Migration
- [ ] Verify data integrity
- [ ] Check query performance
- [ ] Monitor for errors
- [ ] Update documentation

---

## Data Integrity Rules

| Rule | Implementation | Enforcement |
|------|---------------|-------------|
| [Entity] must have [related] | Foreign key constraint | Database |
| [Field] must be unique | UNIQUE constraint | Database |
| [Field] must be positive | CHECK constraint | Database |
| [Business rule] | Application validation | Application |

---
*Generated from pact-database-patterns skill template*
