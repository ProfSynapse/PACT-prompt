/**
 * Test fixture for simple JavaScript functions.
 *
 * Expected Complexity Analysis Results (Node.js AST or Regex):
 * - greet: Complexity 1 (no decision points)
 * - add: Complexity 1 (no decision points)
 * - Total file complexity: 2
 * - Functions exceeding threshold (10): 0
 * - Average complexity: 1.0
 *
 * Expected File Metrics:
 * - Total lines: ~25
 * - Functions: 2
 * - Classes: 0
 * - Imports: 0
 */

function greet(name) {
  return `Hello, ${name}!`;
}

const add = (a, b) => {
  return a + b;
};

module.exports = { greet, add };
