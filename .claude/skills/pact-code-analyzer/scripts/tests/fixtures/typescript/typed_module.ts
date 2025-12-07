/**
 * Test fixture for TypeScript with type annotations (regex fallback testing).
 *
 * Expected Complexity Analysis Results (Regex Fallback):
 * - calculateTotal: Complexity 4-5 (if, for loop, ternary)
 * - findUser: Complexity 2-3 (if statement, array method)
 *
 * Expected File Metrics:
 * - Total lines: ~45
 * - Functions: 2
 * - Classes: 0
 * - Imports: 0
 */

interface Item {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

interface User {
  id: number;
  name: string;
  email: string;
}

function calculateTotal(items: Item[], applyDiscount: boolean = false): number {
  /**
   * Complexity (estimated): 4-5
   * - Base: 1
   * - for loop: +1
   * - if item.quantity > 10: +1
   * - ternary (applyDiscount): +1
   */
  let total = 0;

  for (const item of items) {
    const itemTotal = item.price * item.quantity;
    if (item.quantity > 10) {
      total += itemTotal * 0.9; // Bulk discount
    } else {
      total += itemTotal;
    }
  }

  return applyDiscount ? total * 0.95 : total;
}

const findUser = (users: User[], email: string): User | null => {
  /**
   * Complexity (estimated): 2-3
   * - Base: 1
   * - if (!email): +1
   */
  if (!email) {
    return null;
  }
  return users.find(u => u.email === email) || null;
};

export { calculateTotal, findUser, Item, User };
