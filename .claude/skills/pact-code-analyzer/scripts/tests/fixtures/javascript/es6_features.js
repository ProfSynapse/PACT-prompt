/**
 * Test fixture for ES6 JavaScript features (arrow functions, classes, async).
 *
 * Expected Complexity Analysis Results:
 * - filterActive: Complexity 2 (arrow function with filter/ternary)
 * - UserManager.addUser: Complexity 3 (if statements)
 * - UserManager.removeUser: Complexity 2 (if statement)
 * - fetchUserData: Complexity 4 (async, if, catch, ternary)
 *
 * Expected File Metrics:
 * - Total lines: ~70
 * - Functions: 4+ (including class methods)
 * - Classes: 1
 * - Imports: 0
 */

// Arrow function with array method
const filterActive = (items) => items.filter(item => item.active ? item : null);

// Class with methods
class UserManager {
  constructor() {
    this.users = [];
  }

  addUser(user) {
    /**
     * Complexity: 3
     * - Base: 1
     * - if (!user): +1
     * - if (this.users.find...): +1
     */
    if (!user || !user.id) {
      throw new Error('Invalid user');
    }

    if (this.users.find(u => u.id === user.id)) {
      throw new Error('User already exists');
    }

    this.users.push(user);
  }

  removeUser(userId) {
    /**
     * Complexity: 2
     * - Base: 1
     * - if (index === -1): +1
     */
    const index = this.users.findIndex(u => u.id === userId);
    if (index === -1) {
      return false;
    }
    this.users.splice(index, 1);
    return true;
  }

  getUser(userId) {
    /**
     * Complexity: 1
     */
    return this.users.find(u => u.id === userId);
  }
}

// Async function with error handling
async function fetchUserData(userId) {
  /**
   * Complexity: 4
   * - Base: 1
   * - if (!userId): +1
   * - catch block: +1
   * - ternary: +1
   */
  if (!userId) {
    throw new Error('User ID is required');
  }

  try {
    const response = await fetch(`/api/users/${userId}`);
    return response.ok ? await response.json() : null;
  } catch (error) {
    console.error('Failed to fetch user:', error);
    return null;
  }
}

// Single-line arrow function
const square = x => x * x;

module.exports = { filterActive, UserManager, fetchUserData, square };
