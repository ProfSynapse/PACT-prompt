# State Management Example: Shopping Cart with Zustand

## Context

**Feature**: Shopping cart for e-commerce application
**Requirements**:
- Add/remove items from cart
- Update item quantities
- Calculate totals (subtotal, tax, shipping, total)
- Persist cart across page reloads
- Display cart count in header
- Optimistic updates for UX

**Stack**: React 18 + TypeScript + Zustand

---

## Implementation

### Step 1: Define Cart Types

```typescript
// types/cart.types.ts
export interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  stock: number;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface CartState {
  items: CartItem[];

  // Computed values
  itemCount: number;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;

  // Actions
  addItem: (product: Product, quantity: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}
```

---

### Step 2: Create Zustand Store

```typescript
// stores/cart-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CartState, CartItem, Product } from '@/types/cart.types';

const TAX_RATE = 0.08; // 8% sales tax
const SHIPPING_THRESHOLD = 50; // Free shipping over $50
const SHIPPING_COST = 5.99;

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      // Computed values (derived from items)
      get itemCount() {
        return get().items.reduce((total, item) => total + item.quantity, 0);
      },

      get subtotal() {
        return get().items.reduce(
          (total, item) => total + item.product.price * item.quantity,
          0
        );
      },

      get tax() {
        return get().subtotal * TAX_RATE;
      },

      get shipping() {
        const subtotal = get().subtotal;
        return subtotal >= SHIPPING_THRESHOLD ? 0 : SHIPPING_COST;
      },

      get total() {
        return get().subtotal + get().tax + get().shipping;
      },

      // Actions
      addItem: (product: Product, quantity: number = 1) => {
        set((state) => {
          // Check if item already exists in cart
          const existingItem = state.items.find(
            (item) => item.product.id === product.id
          );

          if (existingItem) {
            // Update quantity if item exists
            return {
              items: state.items.map((item) =>
                item.product.id === product.id
                  ? {
                      ...item,
                      quantity: Math.min(
                        item.quantity + quantity,
                        product.stock // Don't exceed available stock
                      ),
                    }
                  : item
              ),
            };
          }

          // Add new item to cart
          return {
            items: [
              ...state.items,
              {
                product,
                quantity: Math.min(quantity, product.stock),
              },
            ],
          };
        });
      },

      removeItem: (productId: string) => {
        set((state) => ({
          items: state.items.filter((item) => item.product.id !== productId),
        }));
      },

      updateQuantity: (productId: string, quantity: number) => {
        if (quantity <= 0) {
          // Remove item if quantity is 0 or negative
          get().removeItem(productId);
          return;
        }

        set((state) => ({
          items: state.items.map((item) =>
            item.product.id === productId
              ? {
                  ...item,
                  quantity: Math.min(quantity, item.product.stock),
                }
              : item
          ),
        }));
      },

      clearCart: () => {
        set({ items: [] });
      },
    }),
    {
      name: 'shopping-cart', // LocalStorage key
      partialize: (state) => ({ items: state.items }), // Only persist items, not computed values
    }
  )
);
```

**Key Design Decisions**:
- **Computed values as getters**: Automatically recalculate when items change
- **Immutable updates**: Use spread operators and map/filter for state updates
- **Stock validation**: Prevent adding more items than available
- **Persistence**: Save cart to localStorage for page reloads
- **Partial persistence**: Only persist `items`, computed values are derived

---

### Step 3: Cart Item Component

```typescript
// components/CartItem.tsx
import React from 'react';
import { CartItem as CartItemType } from '@/types/cart.types';
import { useCartStore } from '@/stores/cart-store';

interface CartItemProps {
  item: CartItemType;
}

export const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const { updateQuantity, removeItem } = useCartStore((state) => ({
    updateQuantity: state.updateQuantity,
    removeItem: state.removeItem,
  }));

  const handleQuantityChange = (newQuantity: number) => {
    updateQuantity(item.product.id, newQuantity);
  };

  const handleRemove = () => {
    removeItem(item.product.id);
  };

  return (
    <div className="cart-item">
      <img
        src={item.product.image}
        alt={item.product.name}
        className="cart-item__image"
      />

      <div className="cart-item__details">
        <h3 className="cart-item__name">{item.product.name}</h3>
        <p className="cart-item__price">
          ${item.product.price.toFixed(2)}
        </p>
      </div>

      <div className="cart-item__quantity">
        <button
          onClick={() => handleQuantityChange(item.quantity - 1)}
          disabled={item.quantity <= 1}
          aria-label="Decrease quantity"
        >
          −
        </button>

        <input
          type="number"
          min="1"
          max={item.product.stock}
          value={item.quantity}
          onChange={(e) => handleQuantityChange(parseInt(e.target.value, 10))}
          aria-label="Quantity"
        />

        <button
          onClick={() => handleQuantityChange(item.quantity + 1)}
          disabled={item.quantity >= item.product.stock}
          aria-label="Increase quantity"
        >
          +
        </button>
      </div>

      <div className="cart-item__total">
        ${(item.product.price * item.quantity).toFixed(2)}
      </div>

      <button
        onClick={handleRemove}
        className="cart-item__remove"
        aria-label={`Remove ${item.product.name} from cart`}
      >
        ✕
      </button>
    </div>
  );
};
```

**Key Points**:
- **Selective subscription**: Only subscribe to needed actions, not entire store
- **Optimistic updates**: UI updates immediately, no loading states for cart operations
- **Accessibility**: ARIA labels for icon buttons
- **Stock constraints**: Disable increment button when at max stock

---

### Step 4: Cart Summary Component

```typescript
// components/CartSummary.tsx
import React from 'react';
import { useCartStore } from '@/stores/cart-store';

export const CartSummary: React.FC = () => {
  // Subscribe only to computed values (automatically updates when items change)
  const { subtotal, tax, shipping, total } = useCartStore((state) => ({
    subtotal: state.subtotal,
    tax: state.tax,
    shipping: state.shipping,
    total: state.total,
  }));

  return (
    <div className="cart-summary">
      <h2>Order Summary</h2>

      <div className="cart-summary__line">
        <span>Subtotal:</span>
        <span>${subtotal.toFixed(2)}</span>
      </div>

      <div className="cart-summary__line">
        <span>Tax (8%):</span>
        <span>${tax.toFixed(2)}</span>
      </div>

      <div className="cart-summary__line">
        <span>Shipping:</span>
        <span>
          {shipping === 0 ? (
            <strong>FREE</strong>
          ) : (
            `$${shipping.toFixed(2)}`
          )}
        </span>
      </div>

      {subtotal > 0 && subtotal < 50 && (
        <p className="cart-summary__notice">
          Add ${(50 - subtotal).toFixed(2)} more for free shipping!
        </p>
      )}

      <div className="cart-summary__total">
        <span>Total:</span>
        <span>${total.toFixed(2)}</span>
      </div>

      <button className="cart-summary__checkout" disabled={total === 0}>
        Proceed to Checkout
      </button>
    </div>
  );
};
```

**Key Points**:
- **Automatic reactivity**: Component re-renders when computed values change
- **Derived state**: Tax, shipping, and total calculated from items
- **Conditional messaging**: Encourage users to reach free shipping threshold

---

### Step 5: Header Cart Badge

```typescript
// components/Header.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useCartStore } from '@/stores/cart-store';

export const Header: React.FC = () => {
  // Subscribe only to itemCount for optimal performance
  const itemCount = useCartStore((state) => state.itemCount);

  return (
    <header className="header">
      <div className="header__logo">
        <Link to="/">My Store</Link>
      </div>

      <nav className="header__nav">
        <Link to="/products">Products</Link>
        <Link to="/about">About</Link>
      </nav>

      <Link to="/cart" className="header__cart">
        <span className="cart-icon">🛒</span>
        {itemCount > 0 && (
          <span className="cart-badge" aria-label={`${itemCount} items in cart`}>
            {itemCount}
          </span>
        )}
      </Link>
    </header>
  );
};
```

**Performance Optimization**:
- **Minimal subscription**: Only subscribes to `itemCount`, not entire cart
- **Conditional rendering**: Badge only shown when cart has items
- **No unnecessary re-renders**: Header doesn't re-render when item prices/quantities change

---

### Step 6: Product Card with Add to Cart

```typescript
// components/ProductCard.tsx
import React, { useState } from 'react';
import { Product } from '@/types/cart.types';
import { useCartStore } from '@/stores/cart-store';

interface ProductCardProps {
  product: Product;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const addItem = useCartStore((state) => state.addItem);
  const [quantity, setQuantity] = useState(1);
  const [showAddedMessage, setShowAddedMessage] = useState(false);

  const handleAddToCart = () => {
    addItem(product, quantity);

    // Show temporary success message
    setShowAddedMessage(true);
    setTimeout(() => setShowAddedMessage(false), 2000);

    // Reset quantity
    setQuantity(1);
  };

  return (
    <div className="product-card">
      <img
        src={product.image}
        alt={product.name}
        className="product-card__image"
      />

      <h3 className="product-card__name">{product.name}</h3>
      <p className="product-card__price">${product.price.toFixed(2)}</p>

      <div className="product-card__stock">
        {product.stock > 0 ? (
          <span className="in-stock">{product.stock} in stock</span>
        ) : (
          <span className="out-of-stock">Out of stock</span>
        )}
      </div>

      {product.stock > 0 && (
        <>
          <div className="product-card__quantity">
            <label htmlFor={`quantity-${product.id}`}>Quantity:</label>
            <input
              id={`quantity-${product.id}`}
              type="number"
              min="1"
              max={product.stock}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value, 10) || 1)}
            />
          </div>

          <button
            onClick={handleAddToCart}
            className="product-card__add-btn"
          >
            Add to Cart
          </button>

          {showAddedMessage && (
            <p className="product-card__success" role="status">
              ✓ Added to cart
            </p>
          )}
        </>
      )}
    </div>
  );
};
```

**UX Enhancements**:
- **Optimistic update**: Cart updates immediately without loading state
- **Success feedback**: Temporary message confirms item added
- **Stock awareness**: Disable add button when out of stock
- **Quantity control**: User can add multiple items at once

---

### Step 7: Cart Page

```typescript
// pages/CartPage.tsx
import React from 'react';
import { useCartStore } from '@/stores/cart-store';
import { CartItem } from '@/components/CartItem';
import { CartSummary } from '@/components/CartSummary';

export const CartPage: React.FC = () => {
  const { items, clearCart } = useCartStore((state) => ({
    items: state.items,
    clearCart: state.clearCart,
  }));

  if (items.length === 0) {
    return (
      <div className="cart-page cart-page--empty">
        <h1>Your Cart is Empty</h1>
        <p>Add some products to get started!</p>
        <a href="/products" className="btn btn-primary">
          Browse Products
        </a>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <header className="cart-page__header">
        <h1>Shopping Cart ({items.length} items)</h1>
        <button
          onClick={clearCart}
          className="btn btn-secondary"
        >
          Clear Cart
        </button>
      </header>

      <div className="cart-page__content">
        <div className="cart-page__items">
          {items.map((item) => (
            <CartItem key={item.product.id} item={item} />
          ))}
        </div>

        <aside className="cart-page__summary">
          <CartSummary />
        </aside>
      </div>
    </div>
  );
};
```

---

## Advanced: Persist to Backend

### Step 8: Sync Cart with Backend

```typescript
// stores/cart-store.ts (enhanced)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CartState, CartItem, Product } from '@/types/cart.types';
import { api } from '@/services/api';

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      isLoading: false,
      error: null,

      // ... (previous computed values and actions)

      // Sync cart to backend after login
      syncCart: async (userId: string) => {
        set({ isLoading: true, error: null });

        try {
          const localItems = get().items;

          // Send local cart to backend
          await api.post(`/users/${userId}/cart`, { items: localItems });

          // Fetch updated cart from backend (handles merges/conflicts)
          const response = await api.get(`/users/${userId}/cart`);
          set({ items: response.data.items, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to sync cart', isLoading: false });
        }
      },

      // Load cart from backend
      loadCart: async (userId: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.get(`/users/${userId}/cart`);
          set({ items: response.data.items, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to load cart', isLoading: false });
        }
      },
    }),
    {
      name: 'shopping-cart',
      partialize: (state) => ({ items: state.items }),
    }
  )
);
```

**Usage After Login**:
```typescript
// In login handler
const handleLogin = async (email: string, password: string) => {
  const user = await authService.login(email, password);

  // Sync local cart with backend
  await useCartStore.getState().syncCart(user.id);
};
```

---

## Testing Cart Store

```typescript
// stores/__tests__/cart-store.test.ts
import { renderHook, act } from '@testing-library/react-hooks';
import { useCartStore } from '../cart-store';

const mockProduct = {
  id: '1',
  name: 'Test Product',
  price: 29.99,
  image: '/test.jpg',
  stock: 10,
};

describe('useCartStore', () => {
  beforeEach(() => {
    // Clear cart before each test
    useCartStore.setState({ items: [] });
  });

  test('adds item to cart', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 2);
    });

    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].quantity).toBe(2);
    expect(result.current.itemCount).toBe(2);
  });

  test('updates quantity when adding existing item', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 1);
      result.current.addItem(mockProduct, 2);
    });

    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].quantity).toBe(3);
  });

  test('respects stock limit when adding items', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 15); // More than stock (10)
    });

    expect(result.current.items[0].quantity).toBe(10); // Capped at stock
  });

  test('calculates totals correctly', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 2); // 2 × $29.99 = $59.98
    });

    expect(result.current.subtotal).toBe(59.98);
    expect(result.current.tax).toBeCloseTo(4.80, 2); // 8% of $59.98
    expect(result.current.shipping).toBe(0); // Free shipping over $50
    expect(result.current.total).toBeCloseTo(64.78, 2);
  });

  test('removes item from cart', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 1);
      result.current.removeItem(mockProduct.id);
    });

    expect(result.current.items).toHaveLength(0);
    expect(result.current.itemCount).toBe(0);
  });

  test('clears entire cart', () => {
    const { result } = renderHook(() => useCartStore());

    act(() => {
      result.current.addItem(mockProduct, 3);
      result.current.clearCart();
    });

    expect(result.current.items).toHaveLength(0);
  });
});
```

---

## Key Decisions

### 1. State Management Library: Zustand
**Decision**: Use Zustand over Redux or Context API
**Rationale**:
- Simpler API than Redux (no reducers, action creators, or middleware boilerplate)
- Better performance than Context API (selective subscriptions)
- Built-in persistence middleware
- Minimal bundle size (~1KB)
**Trade-off**: Less ecosystem tooling than Redux (DevTools not as robust)

### 2. Computed Values as Getters
**Decision**: Use getters for derived state (subtotal, tax, total)
**Rationale**: Automatically recalculate when items change, no manual synchronization
**Alternative**: Could use `useMemo` in components, but centralizing logic in store is cleaner

### 3. Optimistic Updates
**Decision**: Update cart immediately without waiting for backend confirmation
**Rationale**: Improved UX, cart operations feel instant
**Trade-off**: Must handle sync conflicts if backend rejects update

### 4. LocalStorage Persistence
**Decision**: Persist cart to localStorage for page reloads
**Rationale**: Preserve cart across sessions for better UX
**Security Note**: Don't persist sensitive data (use for cart IDs, not payment info)

---

## Common Pitfalls Avoided

1. **Prop drilling**: Zustand provides global access without Context API nesting
2. **Unnecessary re-renders**: Selective subscriptions prevent components from re-rendering on unrelated changes
3. **Stale closures**: Zustand handles this automatically
4. **Lost cart on reload**: Persistence middleware saves cart to localStorage
5. **Stock overflow**: Validation prevents adding more items than available
6. **Floating point errors**: Use `.toFixed(2)` for currency display

---

*Example from pact-frontend-patterns skill - Zustand state management implementation for shopping cart feature*
