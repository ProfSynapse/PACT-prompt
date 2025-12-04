# Component Patterns Reference

Comprehensive guide to component architecture patterns for building scalable, maintainable React applications.

## Table of Contents

1. [Presentational vs Container Components](#presentational-vs-container-components)
2. [Compound Components](#compound-components)
3. [Render Props Pattern](#render-props-pattern)
4. [Higher-Order Components](#higher-order-components)
5. [Custom Hooks Pattern](#custom-hooks-pattern)
6. [Provider Pattern](#provider-pattern)
7. [Controlled vs Uncontrolled Components](#controlled-vs-uncontrolled-components)
8. [Component Composition](#component-composition)

---

## Presentational vs Container Components

### Presentational Components

**Purpose**: Pure UI rendering without business logic or side effects.

**Characteristics:**
- Receive data and callbacks via props
- Have no dependencies on the rest of the app (Redux, API calls, etc.)
- Highly reusable across different contexts
- Easy to test in isolation
- Often stateless (but may have UI state)

**Example:**

```typescript
// ProductCard.tsx - Presentational
interface ProductCardProps {
  name: string;
  price: number;
  imageUrl: string;
  onAddToCart: (productId: string) => void;
  productId: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  name,
  price,
  imageUrl,
  onAddToCart,
  productId
}) => {
  return (
    <article className="product-card">
      <img src={imageUrl} alt={name} loading="lazy" />
      <h3>{name}</h3>
      <p className="price">${price.toFixed(2)}</p>
      <button onClick={() => onAddToCart(productId)}>
        Add to Cart
      </button>
    </article>
  );
};
```

### Container Components

**Purpose**: Handle data fetching, state management, and business logic.

**Characteristics:**
- Fetch data from APIs or global state
- Manage local component state
- Pass data and callbacks to presentational components
- Often specific to a feature or page
- Coordinate multiple presentational components

**Example:**

```typescript
// ProductListContainer.tsx - Container
export const ProductListContainer: React.FC = () => {
  const { data: products, isLoading, error } = useProducts();
  const { addToCart } = useCart();
  const [filter, setFilter] = useState<'all' | 'sale'>('all');

  const handleAddToCart = (productId: string) => {
    addToCart(productId);
    toast.success('Added to cart');
  };

  if (isLoading) return <ProductListSkeleton />;
  if (error) return <ErrorMessage error={error} />;

  const filteredProducts = products?.filter(p =>
    filter === 'all' || p.onSale
  );

  return (
    <ProductListView
      products={filteredProducts}
      filter={filter}
      onFilterChange={setFilter}
      onAddToCart={handleAddToCart}
    />
  );
};

// ProductListView.tsx - Presentational
interface ProductListViewProps {
  products: Product[];
  filter: 'all' | 'sale';
  onFilterChange: (filter: 'all' | 'sale') => void;
  onAddToCart: (productId: string) => void;
}

export const ProductListView: React.FC<ProductListViewProps> = ({
  products,
  filter,
  onFilterChange,
  onAddToCart
}) => {
  return (
    <section>
      <FilterBar value={filter} onChange={onFilterChange} />
      <div className="product-grid">
        {products.map(product => (
          <ProductCard
            key={product.id}
            {...product}
            onAddToCart={onAddToCart}
          />
        ))}
      </div>
    </section>
  );
};
```

**When to Use:**
- Large features with complex data requirements
- Pages that coordinate multiple UI sections
- When you want to test business logic separately from UI

---

## Compound Components

**Purpose**: Create flexible, composable components that work together while sharing implicit state.

**Characteristics:**
- Components designed to be used together
- Internal state shared via Context
- Flexible composition without prop drilling
- Enforces correct usage patterns

**Example:**

```typescript
// Tabs.tsx - Compound Component
interface TabsContextValue {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined);

const useTabs = () => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within Tabs');
  }
  return context;
};

// Root component
interface TabsProps {
  defaultTab: string;
  children: React.ReactNode;
}

export const Tabs: React.FC<TabsProps> & {
  List: typeof TabList;
  Tab: typeof Tab;
  Panel: typeof TabPanel;
} = ({ defaultTab, children }) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
};

// TabList component
const TabList: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div role="tablist" className="tab-list">
    {children}
  </div>
);

// Tab component
interface TabProps {
  id: string;
  children: React.ReactNode;
}

const Tab: React.FC<TabProps> = ({ id, children }) => {
  const { activeTab, setActiveTab } = useTabs();
  const isActive = activeTab === id;

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`panel-${id}`}
      id={`tab-${id}`}
      onClick={() => setActiveTab(id)}
      className={isActive ? 'active' : ''}
    >
      {children}
    </button>
  );
};

// TabPanel component
interface TabPanelProps {
  id: string;
  children: React.ReactNode;
}

const TabPanel: React.FC<TabPanelProps> = ({ id, children }) => {
  const { activeTab } = useTabs();
  const isActive = activeTab === id;

  if (!isActive) return null;

  return (
    <div
      role="tabpanel"
      id={`panel-${id}`}
      aria-labelledby={`tab-${id}`}
      className="tab-panel"
    >
      {children}
    </div>
  );
};

// Attach subcomponents
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage:
<Tabs defaultTab="overview">
  <Tabs.List>
    <Tabs.Tab id="overview">Overview</Tabs.Tab>
    <Tabs.Tab id="features">Features</Tabs.Tab>
    <Tabs.Tab id="pricing">Pricing</Tabs.Tab>
  </Tabs.List>

  <Tabs.Panel id="overview">
    <h2>Overview Content</h2>
  </Tabs.Panel>
  <Tabs.Panel id="features">
    <h2>Features Content</h2>
  </Tabs.Panel>
  <Tabs.Panel id="pricing">
    <h2>Pricing Content</h2>
  </Tabs.Panel>
</Tabs>
```

**When to Use:**
- Complex UI components like Tabs, Accordion, Dropdown
- When you want flexible composition without prop drilling
- Libraries and design systems

---

## Render Props Pattern

**Purpose**: Share code between components using a prop whose value is a function.

**Characteristics:**
- Inversion of control for rendering
- Highly flexible and composable
- Can pass arguments to render function
- Modern alternative: custom hooks

**Example:**

```typescript
// MouseTracker.tsx - Render Props
interface MousePosition {
  x: number;
  y: number;
}

interface MouseTrackerProps {
  render: (position: MousePosition) => React.ReactNode;
}

export const MouseTracker: React.FC<MouseTrackerProps> = ({ render }) => {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 });

  const handleMouseMove = (event: React.MouseEvent) => {
    setPosition({
      x: event.clientX,
      y: event.clientY
    });
  };

  return (
    <div onMouseMove={handleMouseMove} style={{ height: '100vh' }}>
      {render(position)}
    </div>
  );
};

// Usage:
<MouseTracker
  render={({ x, y }) => (
    <div>
      Mouse position: ({x}, {y})
    </div>
  )}
/>

// Or with children as function:
interface MouseTrackerChildrenProps {
  children: (position: MousePosition) => React.ReactNode;
}

export const MouseTrackerChildren: React.FC<MouseTrackerChildrenProps> = ({ children }) => {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 });

  const handleMouseMove = (event: React.MouseEvent) => {
    setPosition({ x: event.clientX, y: event.clientY });
  };

  return (
    <div onMouseMove={handleMouseMove} style={{ height: '100vh' }}>
      {children(position)}
    </div>
  );
};

// Usage:
<MouseTrackerChildren>
  {({ x, y }) => (
    <div>Mouse position: ({x}, {y})</div>
  )}
</MouseTrackerChildren>
```

**When to Use:**
- Sharing stateful logic before hooks existed (less common now)
- When you need fine-grained control over rendering
- Building highly customizable component libraries

---

## Higher-Order Components

**Purpose**: Function that takes a component and returns a new enhanced component.

**Characteristics:**
- Component composition at the function level
- Add props, behavior, or styling to components
- Cross-cutting concerns (auth, logging, tracking)
- Modern alternative: custom hooks + composition

**Example:**

```typescript
// withAuth.tsx - HOC
interface WithAuthProps {
  user: User | null;
  isAuthenticated: boolean;
}

export function withAuth<P extends object>(
  Component: React.ComponentType<P & WithAuthProps>
) {
  return function WithAuthComponent(props: P) {
    const { user, isAuthenticated } = useAuth();

    if (!isAuthenticated) {
      return <Navigate to="/login" />;
    }

    return (
      <Component
        {...props}
        user={user}
        isAuthenticated={isAuthenticated}
      />
    );
  };
}

// Usage:
interface DashboardProps extends WithAuthProps {
  title: string;
}

const Dashboard: React.FC<DashboardProps> = ({ user, title }) => {
  return (
    <div>
      <h1>{title}</h1>
      <p>Welcome, {user?.name}</p>
    </div>
  );
};

export default withAuth(Dashboard);
```

**Modern Alternative with Hooks:**

```typescript
// useRequireAuth.ts - Custom Hook (preferred)
export const useRequireAuth = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return { user, isAuthenticated };
};

// Usage:
const Dashboard: React.FC<{ title: string }> = ({ title }) => {
  const { user } = useRequireAuth();

  return (
    <div>
      <h1>{title}</h1>
      <p>Welcome, {user?.name}</p>
    </div>
  );
};
```

**When to Use:**
- Legacy codebases (prefer hooks in new code)
- Third-party libraries that use HOC pattern
- Very specific cases where component wrapping is clearer

---

## Custom Hooks Pattern

**Purpose**: Extract and reuse stateful logic across components.

**Characteristics:**
- Use React hooks inside custom functions
- Start with "use" prefix
- Can call other hooks
- Return any values or functions needed

**Example:**

```typescript
// useForm.ts - Custom Hook
interface UseFormOptions<T> {
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit: (values: T) => Promise<void>;
}

export const useForm = <T extends Record<string, any>>({
  initialValues,
  validate,
  onSubmit
}: UseFormOptions<T>) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const handleChange = (field: keyof T) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setValues(prev => ({ ...prev, [field]: event.target.value }));
    if (touched[field]) {
      // Clear error when user starts typing
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleBlur = (field: keyof T) => () => {
    setTouched(prev => ({ ...prev, [field]: true }));
    if (validate) {
      const validationErrors = validate(values);
      setErrors(prev => ({ ...prev, [field]: validationErrors[field] }));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce(
      (acc, key) => ({ ...acc, [key]: true }),
      {}
    );
    setTouched(allTouched);

    // Validate all fields
    const validationErrors = validate ? validate(values) : {};
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  };

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset
  };
};

// Usage:
const LoginForm: React.FC = () => {
  const { values, errors, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues: { email: '', password: '' },
    validate: (values) => {
      const errors: any = {};
      if (!values.email) errors.email = 'Required';
      if (!values.password) errors.password = 'Required';
      return errors;
    },
    onSubmit: async (values) => {
      await login(values);
    }
  });

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={values.email}
        onChange={handleChange('email')}
        onBlur={handleBlur('email')}
      />
      {errors.email && <span>{errors.email}</span>}
      {/* ... */}
    </form>
  );
};
```

**When to Use:**
- Extracting stateful logic from components
- Sharing logic across multiple components
- Composing behavior from multiple hooks
- Simplifying complex component logic

---

## Provider Pattern

**Purpose**: Share data/state across component tree without prop drilling.

**Example:**

```typescript
// ThemeProvider.tsx
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

**When to Use:**
- Theme management
- User authentication state
- Localization/i18n
- Feature flags

---

## Controlled vs Uncontrolled Components

### Controlled Components

**State managed by React:**

```typescript
const ControlledInput: React.FC = () => {
  const [value, setValue] = useState('');

  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
};
```

### Uncontrolled Components

**State managed by DOM:**

```typescript
const UncontrolledInput: React.FC = () => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    console.log(inputRef.current?.value);
  };

  return <input ref={inputRef} defaultValue="Initial" />;
};
```

**When to Use:**
- Controlled: Forms with validation, complex state
- Uncontrolled: Simple forms, file inputs, integration with non-React code

---

## Component Composition

**Prefer composition over complex props:**

```typescript
// Bad: Prop-based configuration
<Button variant="primary" icon="check" iconPosition="left" />

// Good: Composition
<Button>
  <Icon name="check" />
  Save Changes
</Button>
```

**Slot pattern:**

```typescript
interface CardProps {
  header?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ header, children, footer }) => (
  <div className="card">
    {header && <div className="card-header">{header}</div>}
    <div className="card-body">{children}</div>
    {footer && <div className="card-footer">{footer}</div>}
  </div>
);
```
