/**
 * Test fixture for complex JavaScript code with multiple decision points.
 *
 * Expected Complexity Analysis Results:
 * - processPayment: Complexity 8-10 (if, else if, &&, ||, ternary)
 * - validateCard: Complexity 5-6 (if statements, logical operators)
 * - formatAmount: Complexity 2-3 (ternary operator)
 *
 * Expected File Metrics:
 * - Total lines: ~70
 * - Functions: 3
 * - Classes: 0
 * - Imports: 0
 */

function processPayment(payment, user) {
  /**
   * Complex payment processing function.
   *
   * Complexity (estimated): 8-10
   * - Base: 1
   * - if (!payment): +1
   * - if (!user): +1
   * - if (payment.amount <= 0): +1
   * - || operator: +1
   * - if (payment.method === 'card'): +1
   * - && operator: +1
   * - else if: +1
   * - ternary: +1
   */
  if (!payment) {
    throw new Error('Payment is required');
  }

  if (!user) {
    throw new Error('User is required');
  }

  if (payment.amount <= 0) {
    return { status: 'failed', reason: 'Invalid amount' };
  }

  // Validate payment method
  if (payment.method === 'card' && !validateCard(payment.card)) {
    return { status: 'failed', reason: 'Invalid card' };
  } else if (payment.method === 'paypal' || payment.method === 'crypto') {
    return { status: 'pending', reason: 'External verification required' };
  }

  const fee = user.premium ? 0 : payment.amount * 0.03;
  const total = payment.amount + fee;

  return {
    status: 'success',
    amount: formatAmount(payment.amount),
    fee: formatAmount(fee),
    total: formatAmount(total)
  };
}

function validateCard(card) {
  /**
   * Validate card details.
   *
   * Complexity (estimated): 5-6
   * - Base: 1
   * - if (!card): +1
   * - || operator (2 conditions): +2
   * - if (card.number.length !== 16): +1
   * - && operator: +1
   */
  if (!card) {
    return false;
  }

  if (!card.number || !card.cvv || !card.expiry) {
    return false;
  }

  if (card.number.length !== 16) {
    return false;
  }

  const currentDate = new Date();
  const expiryDate = new Date(card.expiry);

  if (expiryDate <= currentDate) {
    return false;
  }

  return true;
}

const formatAmount = (amount) => {
  /**
   * Format amount with currency.
   *
   * Complexity (estimated): 2-3
   * - Base: 1
   * - ternary: +1
   */
  return amount >= 0 ? `$${amount.toFixed(2)}` : '-$' + Math.abs(amount).toFixed(2);
};

module.exports = { processPayment, validateCard, formatAmount };
