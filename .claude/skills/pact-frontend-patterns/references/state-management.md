# State Management Reference

Comprehensive guide to state management strategies in modern React applications.

## Table of Contents

1. [State Categories](#state-categories)
2. [Local State](#local-state)
3. [Server State](#server-state)
4. [Global State](#global-state)
5. [URL State](#url-state)
6. [Form State](#form-state)
7. [Choosing the Right Solution](#choosing-the-right-solution)

---

## State Categories

Understanding state categories helps you choose the right management strategy.

### 1. UI State
**Examples**: Modal open/closed, dropdown expanded, theme preference, sidebar collapsed

**Characteristics:**
- Affects visual presentation
- Usually local to component or shared across few components
- Doesn't need to persist beyond session (usually)
- Can be derived from user interactions

**Solutions:** `useState`, `useReducer`, Context API

### 2. Server State
**Examples**: User data, product listings, API responses, cached data

**Characteristics:**
- Owned by the server, cached on client
- Asynchronous by nature
- Needs synchronization and invalidation
- Requires loading and error states
- Often shared across many components

**Solutions:** React Query, SWR, Apollo Client, RTK Query

### 3. Form State
**Examples**: Input values, validation errors, touched fields, submission status

**Characteristics:**
- Temporary until submission
- Needs validation logic
- Requires error handling
- Often complex with multi-step flows

**Solutions:** React Hook Form, Formik, `useReducer`

### 4. URL State
**Examples**: Current page, filters, sort order, search query

**Characteristics:**
- Should be shareable via URL
- Enables deep linking
- Syncs with browser history
- Affects what user sees

**Solutions:** React Router, Next.js router, query string libraries

### 5. Global Application State
**Examples**: Current user, auth status, app-wide preferences, feature flags

**Characteristics:**
- Needed across entire application
- Changes infrequently
- Shared by many components
- May need persistence

**Solutions:** Context API, Redux, Zustand, Jotai, Recoil

---

## Local State

### When to Use

- State needed only within a single component
- Simple UI interactions (toggle, counter, input)
- Component-specific derived state
- State that doesn't need to be shared

### useState

**Best for:** Simple values, primitive types, small objects

```typescript
const [count, setCount] = useState(0);
const [isOpen, setIsOpen] = useState(false);
const [user, setUser] = useState<User | null>(null);

// Functional updates for state based on previous value
setCount(prev => prev + 1);

// Object updates (replace entire object)
setUser({ name: 'John', email: 'john@example.com' });
```

**Common Patterns:**

```typescript
// Toggle boolean
const [isVisible, setIsVisible] = useState(false);
const toggle = () => setIsVisible(prev => !prev);

// Manage form input
const [email, setEmail] = useState('');
<input value={email} onChange={(e) => setEmail(e.target.value)} />

// Lazy initialization (expensive computation)
const [data, setData] = useState(() => {
  return computeExpensiveValue();
});
```

### useReducer

**Best for:** Complex state logic, multiple related state values, state transitions

```typescript
interface State {
  count: number;
  step: number;
  history: number[];
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'setStep'; payload: number }
  | { type: 'reset' };

const initialState: State = {
  count: 0,
  step: 1,
  history: []
};

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'increment':
      return {
        ...state,
        count: state.count + state.step,
        history: [...state.history, state.count + state.step]
      };
    case 'decrement':
      return {
        ...state,
        count: state.count - state.step,
        history: [...state.history, state.count - state.step]
      };
    case 'setStep':
      return { ...state, step: action.payload };
    case 'reset':
      return initialState;
    default:
      return state;
  }
};

// Usage
const [state, dispatch] = useReducer(reducer, initialState);

<button onClick={() => dispatch({ type: 'increment' })}>+</button>
<button onClick={() => dispatch({ type: 'setStep', payload: 5 })}>
  Set step to 5
</button>
```

**When to prefer useReducer over useState:**
- State updates involve complex logic
- Next state depends on previous state
- State has multiple sub-values
- You want to test state logic independently

---

## Server State

### Why Server State is Different

Server state is fundamentally different from client state:
- **Source of truth is remote** - Client has a cache
- **Asynchronous** - Requires loading states
- **Can become stale** - Needs synchronization
- **Shared ownership** - Other users can modify

### React Query (TanStack Query)

**Best for:** REST APIs, data fetching, caching, synchronization

**Installation:**
```bash
npm install @tanstack/react-query
```

**Setup:**

```typescript
// App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false
    }
  }
});

export const App = () => (
  <QueryClientProvider client={queryClient}>
    <YourApp />
  </QueryClientProvider>
);
```

**Basic Usage:**

```typescript
// hooks/useProducts.ts
import { useQuery } from '@tanstack/react-query';

export const useProducts = () => {
  return useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await fetch('/api/products');
      if (!response.ok) throw new Error('Failed to fetch products');
      return response.json();
    }
  });
};

// Component
const ProductList = () => {
  const { data, isLoading, error, refetch } = useProducts();

  if (isLoading) return <Spinner />;
  if (error) return <Error error={error} />;

  return (
    <div>
      {data.map(product => (
        <ProductCard key={product.id} {...product} />
      ))}
      <button onClick={() => refetch()}>Refresh</button>
    </div>
  );
};
```

**Mutations:**

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useCreateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newProduct: NewProduct) => {
      const response = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProduct)
      });
      if (!response.ok) throw new Error('Failed to create product');
      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch products list
      queryClient.invalidateQueries({ queryKey: ['products'] });
    }
  });
};

// Usage
const CreateProductForm = () => {
  const { mutate, isPending } = useCreateProduct();

  const handleSubmit = (product: NewProduct) => {
    mutate(product, {
      onSuccess: () => {
        toast.success('Product created!');
      },
      onError: (error) => {
        toast.error(`Error: ${error.message}`);
      }
    });
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleSubmit(formData);
    }}>
      {/* form fields */}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Product'}
      </button>
    </form>
  );
};
```

**Advanced Patterns:**

```typescript
// Dependent queries
const useUserPosts = (userId: string) => {
  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId)
  });

  return useQuery({
    queryKey: ['posts', user?.id],
    queryFn: () => fetchPosts(user!.id),
    enabled: !!user // Only run when user is loaded
  });
};

// Pagination
const useProducts = (page: number) => {
  return useQuery({
    queryKey: ['products', page],
    queryFn: () => fetchProducts(page),
    keepPreviousData: true // Show old data while fetching new
  });
};

// Optimistic updates
const useUpdateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateProduct,
    onMutate: async (updatedProduct) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['products'] });

      // Snapshot previous value
      const previousProducts = queryClient.getQueryData(['products']);

      // Optimistically update
      queryClient.setQueryData(['products'], (old: Product[]) =>
        old.map(p => p.id === updatedProduct.id ? updatedProduct : p)
      );

      return { previousProducts };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(['products'], context?.previousProducts);
    },
    onSettled: () => {
      // Refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['products'] });
    }
  });
};
```

### SWR (Alternative to React Query)

**Installation:**
```bash
npm install swr
```

**Basic Usage:**

```typescript
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

const useProducts = () => {
  const { data, error, isLoading, mutate } = useSWR('/api/products', fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 60000
  });

  return {
    products: data,
    isLoading,
    error,
    refresh: mutate
  };
};
```

---

## Global State

### Context API

**Best for:** Infrequent updates, theme, auth, small-to-medium apps

**Pros:**
- Built into React
- No external dependencies
- Good for infrequent updates

**Cons:**
- All consumers re-render on any context change
- Can lead to performance issues with frequent updates
- Requires provider nesting for multiple contexts

**Example:**

```typescript
// contexts/AuthContext.tsx
interface AuthContextValue {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    checkAuth().then(user => {
      setUser(user);
      setIsLoading(false);
    });
  }, []);

  const login = async (email: string, password: string) => {
    const user = await api.login(email, password);
    setUser(user);
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, login, logout, isLoading }),
    [user, isLoading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

**Optimization: Split contexts to reduce re-renders**

```typescript
// Bad: Single context with all user data
const UserContext = React.createContext({ user, settings, preferences });

// Good: Split by update frequency
const UserContext = React.createContext({ user }); // Changes rarely
const SettingsContext = React.createContext({ settings }); // Changes occasionally
const PreferencesContext = React.createContext({ preferences }); // Changes frequently
```

### Zustand

**Best for:** Simple global state, minimal boilerplate, performance

**Installation:**
```bash
npm install zustand
```

**Example:**

```typescript
// stores/useCartStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clear: () => void;
  total: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) =>
        set((state) => {
          const existing = state.items.find(i => i.id === item.id);
          if (existing) {
            return {
              items: state.items.map(i =>
                i.id === item.id
                  ? { ...i, quantity: i.quantity + item.quantity }
                  : i
              )
            };
          }
          return { items: [...state.items, item] };
        }),

      removeItem: (id) =>
        set((state) => ({
          items: state.items.filter(i => i.id !== id)
        })),

      updateQuantity: (id, quantity) =>
        set((state) => ({
          items: state.items.map(i =>
            i.id === id ? { ...i, quantity } : i
          )
        })),

      clear: () => set({ items: [] }),

      total: () => {
        const { items } = get();
        return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
      }
    }),
    {
      name: 'cart-storage' // LocalStorage key
    }
  )
);

// Usage - component only re-renders when used state changes
const Cart = () => {
  const items = useCartStore(state => state.items);
  const removeItem = useCartStore(state => state.removeItem);
  const total = useCartStore(state => state.total());

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>
          {item.name} - ${item.price} x {item.quantity}
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
      <p>Total: ${total}</p>
    </div>
  );
};
```

### Redux Toolkit

**Best for:** Large applications, complex state, time-travel debugging

**Installation:**
```bash
npm install @reduxjs/toolkit react-redux
```

**Setup:**

```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import cartReducer from './cartSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    cart: cartReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// App.tsx
import { Provider } from 'react-redux';
<Provider store={store}>
  <App />
</Provider>
```

**Slice:**

```typescript
// store/cartSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CartItem {
  id: string;
  name: string;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

const initialState: CartState = {
  items: []
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addItem: (state, action: PayloadAction<CartItem>) => {
      const existing = state.items.find(i => i.id === action.payload.id);
      if (existing) {
        existing.quantity += action.payload.quantity;
      } else {
        state.items.push(action.payload);
      }
    },
    removeItem: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(i => i.id !== action.payload);
    }
  }
});

export const { addItem, removeItem } = cartSlice.actions;
export default cartSlice.reducer;

// Usage
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from './store';

const Cart = () => {
  const items = useSelector((state: RootState) => state.cart.items);
  const dispatch = useDispatch();

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>
          {item.name}
          <button onClick={() => dispatch(removeItem(item.id))}>
            Remove
          </button>
        </div>
      ))}
    </div>
  );
};
```

---

## URL State

### React Router

```typescript
import { useSearchParams } from 'react-router-dom';

const ProductList = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const page = parseInt(searchParams.get('page') || '1');
  const sort = searchParams.get('sort') || 'name';
  const filter = searchParams.get('filter') || 'all';

  const updateFilters = (newFilters: Record<string, string>) => {
    setSearchParams(newFilters);
  };

  return (
    <div>
      <FilterBar
        sort={sort}
        filter={filter}
        onFilterChange={(f) => updateFilters({ page: '1', sort, filter: f })}
      />
      <ProductGrid page={page} sort={sort} filter={filter} />
    </div>
  );
};
```

---

## Form State

### React Hook Form

**Installation:**
```bash
npm install react-hook-form
```

**Example:**

```typescript
import { useForm } from 'react-hook-form';

interface FormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

const LoginForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    await login(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email format'
          }
        })}
        type="email"
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        {...register('password', {
          required: 'Password is required',
          minLength: {
            value: 8,
            message: 'Password must be at least 8 characters'
          }
        })}
        type="password"
      />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Log In'}
      </button>
    </form>
  );
};
```

---

## Choosing the Right Solution

### Decision Tree

```
What type of state do you need?

├─ Server data (API responses, cached data)
│  └─ Use: React Query or SWR
│
├─ Form data (inputs, validation)
│  └─ Use: React Hook Form or Formik
│
├─ URL data (filters, pagination, routing)
│  └─ Use: React Router useSearchParams or Next.js router
│
├─ Local UI state (component-specific)
│  ├─ Simple value? → useState
│  └─ Complex logic? → useReducer
│
└─ Global app state (user, theme, cart)
   ├─ Small app, infrequent updates → Context API
   ├─ Medium app, performance matters → Zustand
   └─ Large app, complex workflows → Redux Toolkit
```

### Recommendations by App Size

**Small App (< 10 components)**
- Local: `useState`, `useReducer`
- Global: Context API
- Server: React Query
- Forms: `useState` or React Hook Form

**Medium App (10-50 components)**
- Local: `useState`, `useReducer`
- Global: Zustand or Context API
- Server: React Query
- Forms: React Hook Form

**Large App (50+ components)**
- Local: `useState`, `useReducer`
- Global: Redux Toolkit or Zustand
- Server: React Query or RTK Query
- Forms: React Hook Form
