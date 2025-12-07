---
name: pact-frontend-patterns
description: |
  CODE PHASE (Frontend): Client-side implementation patterns and best practices.

  Provides component architecture patterns, state management strategies, accessibility
  guidelines, performance optimization, and responsive design approaches.

  Use when: building UI components, managing state, implementing forms, optimizing
  performance, ensuring accessibility, creating responsive layouts.
allowed-tools:
  - Read
  - Bash
  - mcp__sequential-thinking__sequentialthinking
metadata:
  phase: "Code"
  version: "1.0.0"
  primary-agent: "pact-frontend-coder"
---

# PACT Frontend Patterns

This skill provides comprehensive frontend implementation patterns aligned with the PACT framework's Code phase principles. Use this skill when building client-side interfaces that require clean architecture, accessibility, and optimal user experience.

## Quick Reference

### Component Architecture Decision Tree

```
Is component reusable across features?
├─ YES: Create in shared/components/
│   ├─ Purely presentational? → Use functional component with props
│   ├─ Complex internal logic? → Split into container + presentation
│   └─ Compound interactions? → Use compound component pattern
└─ NO: Create in feature/components/
    ├─ Simple display? → Inline or local component
    ├─ Form handling? → Use controlled components with validation
    └─ Data fetching? → Use container pattern with hooks
```

### State Management Decision Matrix

| State Type | Scope | Solution | When to Use |
|------------|-------|----------|-------------|
| UI State | Local | `useState`, `useReducer` | Toggles, form inputs, local flags |
| Computed | Local | `useMemo`, `useCallback` | Derived values, memoized functions |
| Shared UI | Multiple components | Context API | Theme, modals, notifications |
| Server | Global | React Query, SWR | API data, caching, synchronization |
| Global App | Application-wide | Redux, Zustand | Complex workflows, undo/redo |

### Accessibility Quick Checklist

**Critical (WCAG 2.1 Level A)**
- [ ] All images have alt text (or alt="" for decorative)
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] All form inputs have associated labels
- [ ] Keyboard navigation works for all interactive elements
- [ ] No keyboard traps in modal dialogs

**Important (WCAG 2.1 Level AA)**
- [ ] Focus indicators visible and sufficient contrast (3:1)
- [ ] Headings used in correct hierarchical order
- [ ] ARIA labels for icon-only buttons
- [ ] Error messages associated with form fields
- [ ] Skip navigation links for main content

**Enhanced (WCAG 2.1 Level AAA)**
- [ ] Color contrast ratio ≥ 7:1 for normal text
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Live regions announce dynamic content changes
- [ ] Comprehensive ARIA landmarks for navigation

### Performance Optimization Priorities

**Priority 1: Critical Rendering Path**
1. Minimize render-blocking resources
2. Inline critical CSS
3. Defer non-critical JavaScript
4. Optimize Web Fonts with `font-display: swap`

**Priority 2: Runtime Performance**
1. Implement code splitting at route boundaries
2. Lazy load images with Intersection Observer
3. Virtualize long lists (react-window, react-virtuoso)
4. Memoize expensive computations

**Priority 3: Bundle Optimization**
1. Tree-shake unused code
2. Analyze bundle size (webpack-bundle-analyzer)
3. Use dynamic imports for heavy dependencies
4. Implement proper cache headers

## Core Patterns

### 1. Component Organization

```
feature/
├── components/
│   ├── FeatureContainer.tsx      # Container: data + logic
│   ├── FeatureView.tsx           # Presentation: UI only
│   ├── FeatureForm.tsx           # Form: validation + submission
│   └── __tests__/
│       └── Feature.test.tsx
├── hooks/
│   ├── useFeatureData.ts         # Custom hook: data fetching
│   └── useFeatureValidation.ts   # Custom hook: business logic
└── types/
    └── feature.types.ts          # TypeScript definitions
```

**Naming Conventions:**
- Containers: `*Container.tsx` (logic-heavy)
- Views: `*View.tsx` (presentation-only)
- Forms: `*Form.tsx` (user input)
- Hooks: `use*.ts` (reusable logic)

### 2. Component Patterns

**Presentational Component** (Pure UI)
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  variant,
  size = 'md',
  disabled = false,
  children,
  onClick
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
};
```

**Container Component** (Logic + Data)
```typescript
export const UserProfileContainer: React.FC = () => {
  const { data, isLoading, error } = useUserProfile();
  const { updateProfile } = useUpdateProfile();

  if (isLoading) return <ProfileSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return <EmptyState />;

  return (
    <UserProfileView
      user={data}
      onUpdate={updateProfile}
    />
  );
};
```

**Compound Component** (Flexible composition)
```typescript
const Card = ({ children }: { children: React.ReactNode }) => (
  <div className="card">{children}</div>
);

Card.Header = ({ children }: { children: React.ReactNode }) => (
  <div className="card-header">{children}</div>
);

Card.Body = ({ children }: { children: React.ReactNode }) => (
  <div className="card-body">{children}</div>
);

Card.Footer = ({ children }: { children: React.ReactNode }) => (
  <div className="card-footer">{children}</div>
);

// Usage:
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer>Actions</Card.Footer>
</Card>
```

### 3. Form Handling Pattern

```typescript
interface FormValues {
  email: string;
  password: string;
}

export const LoginForm: React.FC = () => {
  const [values, setValues] = useState<FormValues>({ email: '', password: '' });
  const [errors, setErrors] = useState<Partial<FormValues>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (values: FormValues): Partial<FormValues> => {
    const errors: Partial<FormValues> = {};
    if (!values.email) errors.email = 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
      errors.email = 'Invalid email format';
    }
    if (values.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    return errors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationErrors = validate(values);

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      await submitLogin(values);
      // Handle success
    } catch (error) {
      setErrors({ email: 'Login failed. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <input
        type="email"
        value={values.email}
        onChange={(e) => setValues({ ...values, email: e.target.value })}
        aria-invalid={!!errors.email}
        aria-describedby={errors.email ? 'email-error' : undefined}
      />
      {errors.email && <span id="email-error" role="alert">{errors.email}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Log In'}
      </button>
    </form>
  );
};
```

### 4. Custom Hooks Pattern

```typescript
// Data fetching hook
export const useUserProfile = (userId: string) => {
  const [data, setData] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchProfile = async () => {
      try {
        setIsLoading(true);
        const profile = await api.getUser(userId);
        if (!cancelled) {
          setData(profile);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchProfile();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { data, isLoading, error };
};
```

## Responsive Design Approach

### Mobile-First Breakpoints

```css
/* Mobile: 320px - 767px (default, no media query) */
.container {
  padding: 1rem;
  width: 100%;
}

/* Tablet: 768px+ */
@media (min-width: 768px) {
  .container {
    padding: 1.5rem;
    max-width: 720px;
    margin: 0 auto;
  }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .container {
    padding: 2rem;
    max-width: 960px;
  }
}

/* Large Desktop: 1280px+ */
@media (min-width: 1280px) {
  .container {
    max-width: 1200px;
  }
}
```

### Responsive Patterns

**Fluid Typography**
```css
:root {
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --font-size-lg: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
  --font-size-xl: clamp(1.5rem, 1.25rem + 1.25vw, 2rem);
}
```

**Container Queries** (Modern approach)
```css
.card-container {
  container-type: inline-size;
}

.card {
  display: block;
}

@container (min-width: 400px) {
  .card {
    display: flex;
    gap: 1rem;
  }
}
```

## Error Handling

### Error Boundary Pattern

```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error }>;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  { hasError: boolean; error: Error | null }
> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const Fallback = this.props.fallback || DefaultErrorFallback;
      return <Fallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

## When to Use Sequential Thinking

Invoke the `mcp__sequential-thinking__sequentialthinking` tool when:

1. **Complex State Logic**: Designing state machines or reducer logic with multiple transitions
2. **Accessibility Implementation**: Planning keyboard navigation flows and ARIA relationships
3. **Performance Optimization**: Analyzing render cycles and identifying optimization opportunities
4. **Form Validation**: Designing multi-step validation with complex business rules
5. **Component Architecture**: Planning compound components or render prop patterns

**Example invocation:**
```
When should I use Context API vs prop drilling for this theme system?
Should I implement virtual scrolling for a list with 500 items?
How do I ensure this modal dialog is fully keyboard accessible?
```

## Testing Considerations

### Component Testing Strategy

**Unit Tests** (Component logic in isolation)
- Hook behavior with `@testing-library/react-hooks`
- Utility functions
- Validation logic

**Integration Tests** (Component interactions)
- User workflows with `@testing-library/react`
- Form submissions
- Navigation flows

**Visual Tests** (UI appearance)
- Storybook stories for component variants
- Visual regression with Chromatic/Percy

### Test Data Attributes

Always add test identifiers for reliable test automation:

```typescript
<button data-testid="submit-button" onClick={handleSubmit}>
  Submit
</button>

<input
  data-testid="email-input"
  type="email"
  name="email"
/>
```

## Related Skills

- **pact-backend-patterns**: API integration and data fetching strategies
- **pact-database-engineer**: Data modeling for client-side state
- **pact-architect**: Component architecture and system design

## Reference Documentation

Detailed implementation patterns and guidelines:
- `references/component-patterns.md` - Comprehensive component architecture patterns
- `references/state-management.md` - State management strategies and trade-offs
- `references/accessibility.md` - Complete accessibility implementation guide

## Version History

- **1.0.0** (2025-12-04): Initial release with core frontend patterns
