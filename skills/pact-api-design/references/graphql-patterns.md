# GraphQL API Design Patterns

Comprehensive guide to GraphQL schema design, resolver patterns, mutation design, and best practices.

## Table of Contents

1. [Schema Design Principles](#schema-design-principles)
2. [Type System](#type-system)
3. [Query Design](#query-design)
4. [Mutation Design](#mutation-design)
5. [Resolver Patterns](#resolver-patterns)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Common Patterns](#common-patterns)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Schema Design Principles

### 1. Design for the Client

GraphQL schemas should be designed around client needs, not database structure:

```graphql
# Bad: Mirrors database structure
type User {
  user_id: Int!
  first_name: String
  last_name: String
  email_address: String
}

# Good: Designed for client consumption
type User {
  id: ID!
  fullName: String!
  email: String!
  displayName: String
}
```

### 2. Use Descriptive Names

Choose clear, unambiguous names for types and fields:

```graphql
# Bad: Abbreviations and unclear names
type Usr {
  fn: String
  ln: String
  addr: Addr
}

# Good: Descriptive, complete names
type User {
  firstName: String!
  lastName: String!
  billingAddress: Address
  shippingAddress: Address
}
```

### 3. Nullable vs Non-Nullable Fields

Use non-null (`!`) sparingly to maintain schema flexibility:

```graphql
# Overly strict: Hard to evolve without breaking clients
type Product {
  id: ID!
  name: String!
  description: String!  # What if description is optional later?
  price: Float!
  discountPrice: Float! # What if no discount?
}

# Better: Non-null only for truly required fields
type Product {
  id: ID!
  name: String!
  description: String   # Optional, can be null
  price: Money!
  discountPrice: Money  # Null when no discount
}
```

### 4. Schema Modularity

Break large schemas into logical modules:

```graphql
# user.graphql
type User {
  id: ID!
  email: String!
  profile: UserProfile
  orders: [Order!]!
}

type UserProfile {
  displayName: String
  avatar: URL
  bio: String
}

# order.graphql
type Order {
  id: ID!
  customer: User!
  items: [OrderItem!]!
  total: Money!
}

type OrderItem {
  product: Product!
  quantity: Int!
  price: Money!
}

# product.graphql
type Product {
  id: ID!
  name: String!
  description: String
  images: [Image!]!
  price: Money!
}
```

## Type System

### Scalar Types

Built-in scalars:
- `Int`: 32-bit integer
- `Float`: Double-precision floating-point
- `String`: UTF-8 character sequence
- `Boolean`: true or false
- `ID`: Unique identifier (serialized as String)

Custom scalars for domain types:
```graphql
scalar DateTime
scalar Email
scalar URL
scalar Money
scalar JSON
scalar Upload

type User {
  id: ID!
  email: Email!
  avatar: URL
  createdAt: DateTime!
  metadata: JSON
}
```

### Object Types

Define domain entities:
```graphql
type User {
  id: ID!
  email: String!
  name: String!
  role: UserRole!
  posts: [Post!]!
  friends: [User!]!
}

enum UserRole {
  ADMIN
  MODERATOR
  USER
  GUEST
}
```

### Interface Types

Share fields across multiple types:
```graphql
interface Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
}

interface Searchable {
  searchRank: Float
  snippet: String
}

type Article implements Node & Searchable {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  searchRank: Float
  snippet: String
  title: String!
  content: String!
  author: User!
}

type Product implements Node & Searchable {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  searchRank: Float
  snippet: String
  name: String!
  price: Money!
}
```

### Union Types

Return one of several types:
```graphql
union SearchResult = Article | Product | User

type Query {
  search(query: String!): [SearchResult!]!
}

# Client query with inline fragments
query {
  search(query: "graphql") {
    ... on Article {
      title
      author { name }
    }
    ... on Product {
      name
      price
    }
    ... on User {
      name
      email
    }
  }
}
```

### Input Types

Define mutation input structures:
```graphql
input CreateUserInput {
  email: String!
  name: String!
  password: String!
  role: UserRole
}

input UpdateUserInput {
  email: String
  name: String
  role: UserRole
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}
```

## Query Design

### Root Query Organization

Organize queries by domain entity:
```graphql
type Query {
  # Single entity queries
  user(id: ID!): User
  product(id: ID!): Product
  order(id: ID!): Order

  # Collection queries
  users(
    first: Int
    after: String
    filter: UserFilter
    sort: UserSort
  ): UserConnection!

  products(
    first: Int
    after: String
    filter: ProductFilter
  ): ProductConnection!

  # Search queries
  search(query: String!, type: SearchType): [SearchResult!]!

  # Current user/context
  me: User!
  viewer: Viewer!
}
```

### Filtering

Design flexible filter inputs:
```graphql
input UserFilter {
  role: UserRole
  status: UserStatus
  createdAfter: DateTime
  createdBefore: DateTime
  search: String
}

input ProductFilter {
  category: String
  priceMin: Float
  priceMax: Float
  inStock: Boolean
  tags: [String!]
}

type Query {
  users(filter: UserFilter): [User!]!
  products(filter: ProductFilter): [Product!]!
}
```

### Sorting

Define sort options clearly:
```graphql
enum UserSortField {
  CREATED_AT
  UPDATED_AT
  NAME
  EMAIL
}

enum SortDirection {
  ASC
  DESC
}

input UserSort {
  field: UserSortField!
  direction: SortDirection!
}

type Query {
  users(sort: UserSort): [User!]!
}
```

### Pagination

Use Relay-style cursor pagination for consistency:

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  users(
    first: Int      # Forward pagination
    after: String
    last: Int       # Backward pagination
    before: String
  ): UserConnection!
}
```

Client usage:
```graphql
# First page
query {
  users(first: 10) {
    edges {
      node { id, name }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# Next page
query {
  users(first: 10, after: "cursor_from_previous_page") {
    edges {
      node { id, name }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Mutation Design

### Input/Payload Pattern

Use consistent input/payload structure:

```graphql
input CreateArticleInput {
  title: String!
  content: String!
  authorId: ID!
  tags: [String!]
  publishedAt: DateTime
}

type CreateArticlePayload {
  article: Article
  errors: [UserError!]!
  success: Boolean!
}

type UserError {
  field: String
  message: String!
  code: String!
}

type Mutation {
  createArticle(input: CreateArticleInput!): CreateArticlePayload!
}
```

Client usage:
```graphql
mutation {
  createArticle(input: {
    title: "GraphQL Best Practices"
    content: "..."
    authorId: "123"
  }) {
    article {
      id
      title
      createdAt
    }
    errors {
      field
      message
      code
    }
    success
  }
}
```

### Mutation Naming

Use clear, action-oriented names:

```graphql
type Mutation {
  # CRUD operations
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!

  # Domain actions
  publishArticle(id: ID!): PublishArticlePayload!
  approveOrder(id: ID!): ApproveOrderPayload!
  cancelSubscription(id: ID!): CancelSubscriptionPayload!

  # Bulk operations
  createUsers(inputs: [CreateUserInput!]!): CreateUsersPayload!
  updateUsers(updates: [UserUpdate!]!): UpdateUsersPayload!
}
```

### Idempotency

Design mutations to be idempotent when possible:

```graphql
input CreateUserInput {
  email: String!
  name: String!
  idempotencyKey: String!  # Client-provided unique key
}

type CreateUserPayload {
  user: User
  alreadyExists: Boolean!  # True if idempotency key matched existing user
  errors: [UserError!]!
}
```

## Resolver Patterns

### Basic Resolver Structure

```javascript
const resolvers = {
  Query: {
    user: async (parent, { id }, context, info) => {
      return context.dataSources.userAPI.getUserById(id);
    },
    users: async (parent, { filter, sort, first, after }, context) => {
      return context.dataSources.userAPI.getUsers({ filter, sort, first, after });
    }
  },

  Mutation: {
    createUser: async (parent, { input }, context) => {
      // Authorization check
      if (!context.user?.isAdmin) {
        throw new ForbiddenError('Admin access required');
      }

      // Validation
      const errors = validateUserInput(input);
      if (errors.length > 0) {
        return { user: null, errors, success: false };
      }

      // Execute mutation
      try {
        const user = await context.dataSources.userAPI.createUser(input);
        return { user, errors: [], success: true };
      } catch (error) {
        return {
          user: null,
          errors: [{ message: error.message, code: 'CREATE_FAILED' }],
          success: false
        };
      }
    }
  },

  User: {
    // Field resolver: Resolve computed or related fields
    fullName: (user) => {
      return `${user.firstName} ${user.lastName}`;
    },

    orders: async (user, args, context) => {
      // DataLoader for N+1 prevention
      return context.loaders.ordersByUserId.load(user.id);
    }
  }
};
```

### DataLoader Pattern

Prevent N+1 queries with batching:

```javascript
const DataLoader = require('dataloader');

// Create loaders in context
const createLoaders = () => ({
  userById: new DataLoader(async (ids) => {
    const users = await db.users.findByIds(ids);
    // Return users in same order as ids
    return ids.map(id => users.find(u => u.id === id));
  }),

  ordersByUserId: new DataLoader(async (userIds) => {
    const orders = await db.orders.findByUserIds(userIds);
    // Group orders by userId
    return userIds.map(userId =>
      orders.filter(order => order.userId === userId)
    );
  })
});

// Usage in resolver
const resolvers = {
  User: {
    orders: (user, args, context) => {
      return context.loaders.ordersByUserId.load(user.id);
    }
  },
  Order: {
    customer: (order, args, context) => {
      return context.loaders.userById.load(order.userId);
    }
  }
};
```

### Field-Level Authorization

```javascript
const { ForbiddenError } = require('apollo-server');

const resolvers = {
  User: {
    email: (user, args, context) => {
      // Only return email if viewing own profile or admin
      if (context.user?.id === user.id || context.user?.isAdmin) {
        return user.email;
      }
      throw new ForbiddenError('Cannot access email');
    },

    ssn: (user, args, context) => {
      // Only admins can see SSN
      if (!context.user?.isAdmin) {
        throw new ForbiddenError('Admin access required');
      }
      return user.ssn;
    }
  }
};
```

## Error Handling

### GraphQL Error Response

GraphQL returns partial data with errors:

```json
{
  "data": {
    "user": {
      "id": "123",
      "name": "John Doe",
      "email": null
    }
  },
  "errors": [
    {
      "message": "Cannot access email",
      "locations": [{ "line": 4, "column": 5 }],
      "path": ["user", "email"],
      "extensions": {
        "code": "FORBIDDEN",
        "userId": "123"
      }
    }
  ]
}
```

### Custom Error Codes

```javascript
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.extensions = {
      code: 'VALIDATION_ERROR',
      field
    };
  }
}

class NotFoundError extends Error {
  constructor(resourceType, id) {
    super(`${resourceType} not found`);
    this.extensions = {
      code: 'NOT_FOUND',
      resourceType,
      id
    };
  }
}

// Usage
if (!user) {
  throw new NotFoundError('User', userId);
}

if (!isValidEmail(input.email)) {
  throw new ValidationError('Invalid email format', 'email');
}
```

### User-Facing Errors in Payload

Return errors in mutation payload for better UX:

```graphql
type CreateUserPayload {
  user: User
  errors: [UserError!]!
  success: Boolean!
}

type UserError {
  field: String      # Which field has error
  message: String!   # User-friendly message
  code: String!      # Machine-readable code
}
```

```javascript
const createUser = async (parent, { input }, context) => {
  const errors = [];

  if (!isValidEmail(input.email)) {
    errors.push({
      field: 'email',
      message: 'Please provide a valid email address',
      code: 'INVALID_EMAIL'
    });
  }

  if (await emailExists(input.email)) {
    errors.push({
      field: 'email',
      message: 'This email is already registered',
      code: 'EMAIL_EXISTS'
    });
  }

  if (errors.length > 0) {
    return { user: null, errors, success: false };
  }

  const user = await db.users.create(input);
  return { user, errors: [], success: true };
};
```

## Performance Optimization

### Query Complexity Analysis

Limit expensive queries:

```javascript
const { createComplexityLimitRule } = require('graphql-validation-complexity');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    createComplexityLimitRule(1000, {
      onCost: (cost) => console.log('Query cost:', cost),
      formatErrorMessage: (cost) => `Query too complex: ${cost} exceeds limit of 1000`
    })
  ]
});
```

### Query Depth Limiting

Prevent deeply nested queries:

```javascript
const depthLimit = require('graphql-depth-limit');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(5)]  // Max depth of 5
});
```

### Field Cost Analysis

Assign costs to expensive fields:

```graphql
type Query {
  users: [User!]! @cost(complexity: 1, multipliers: ["first"])
  search(query: String!): [SearchResult!]! @cost(complexity: 10)
}

type User {
  orders: [Order!]! @cost(complexity: 5, multipliers: ["first"])
}
```

## Common Patterns

### Viewer Pattern

Provide current user context:

```graphql
type Viewer {
  id: ID!
  user: User
  permissions: [Permission!]!
  preferences: UserPreferences
}

type Query {
  viewer: Viewer!
}
```

### Node Interface (Global ID)

Implement globally unique IDs:

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!  # Global ID like "User:123"
  email: String!
}

type Query {
  node(id: ID!): Node  # Fetch any type by global ID
}
```

### Subscription Design

Real-time updates:

```graphql
type Subscription {
  orderUpdated(userId: ID!): Order!
  messageReceived(chatId: ID!): Message!
  notificationReceived: Notification!
}

# Client usage
subscription {
  orderUpdated(userId: "123") {
    id
    status
    total
  }
}
```

## Anti-Patterns to Avoid

### 1. Overly Generic Types

```graphql
# Bad: Generic, unclear types
type GenericResponse {
  data: JSON
  success: Boolean
}

# Good: Specific, typed responses
type CreateUserPayload {
  user: User
  errors: [UserError!]!
}
```

### 2. Nullable ID Fields

```graphql
# Bad: ID should never be null
type User {
  id: ID
}

# Good: ID is always non-null
type User {
  id: ID!
}
```

### 3. Boolean Arguments

```graphql
# Bad: Hard to understand from query alone
type Query {
  users(includeDeleted: Boolean): [User!]!
}

# Good: Explicit enum
enum UserStatus {
  ACTIVE
  DELETED
  ALL
}

type Query {
  users(status: UserStatus): [User!]!
}
```

### 4. REST-ful Field Names

```graphql
# Bad: REST-style naming
type Query {
  getUser(id: ID!): User
  listUsers: [User!]!
}

# Good: GraphQL naming
type Query {
  user(id: ID!): User
  users: [User!]!
}
```

### 5. Array Arguments

```graphql
# Bad: Hard to extend
type Query {
  user(roles: [String!]): User
}

# Good: Use input type for extensibility
input UserFilter {
  roles: [UserRole!]
  status: UserStatus
}

type Query {
  users(filter: UserFilter): [User!]!
}
```

### 6. Ignoring N+1 Problem

Always use DataLoader for related fields to prevent N+1 queries.

### 7. Exposing Internal Implementation

```graphql
# Bad: Exposes database structure
type User {
  user_id: Int
  fk_department_id: Int
}

# Good: Client-focused design
type User {
  id: ID!
  department: Department
}
```

### 8. Mutation Side Effects

Mutations should be explicit about all side effects:

```graphql
# Bad: Unclear side effects
type Mutation {
  updateUser(id: ID!, name: String!): User!
}

# Good: Clear return type showing all changes
type UpdateUserPayload {
  user: User!
  updatedDependencies: [Resource!]!
  notifications: [Notification!]!
}
```
