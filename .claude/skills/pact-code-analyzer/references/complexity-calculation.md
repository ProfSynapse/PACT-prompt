# Cyclomatic Complexity Calculation

**Reference Guide for complexity_analyzer.py**

## Overview

Cyclomatic complexity is a quantitative measure of the number of linearly independent paths through a program's source code. Developed by Thomas McCabe in 1976, it provides an objective measure of code complexity.

## Algorithm: McCabe's Cyclomatic Complexity

### Mathematical Definition

For a given function or method:

```
M = E - N + 2P
```

Where:
- **M** = Cyclomatic complexity
- **E** = Number of edges in the control flow graph
- **N** = Number of nodes in the control flow graph
- **P** = Number of connected components (typically 1 for a single function)

### Practical Calculation

In practice, complexity is calculated as:

```
Complexity = 1 + number of decision points
```

A **decision point** is any statement that creates a branch in the control flow.

## Decision Points by Language

### Python Decision Points

The complexity_analyzer.py script counts these as decision points in Python:

1. **if statements** (including elif)
   ```python
   if condition:        # +1
       pass
   elif other:          # +1
       pass
   ```

2. **for loops**
   ```python
   for item in items:   # +1
       pass
   ```

3. **while loops**
   ```python
   while condition:     # +1
       pass
   ```

4. **Boolean operators** (and, or)
   ```python
   if a and b:          # +2 (if + and)
       pass

   if x or y or z:      # +3 (if + or + or)
       pass
   ```

5. **Exception handlers**
   ```python
   try:
       pass
   except ValueError:   # +1
       pass
   except KeyError:     # +1
       pass
   ```

6. **with statements**
   ```python
   with open(file):     # +1
       pass
   ```

7. **Comprehensions**
   ```python
   [x for x in items if x > 0]  # +2 (comprehension + if)
   ```

8. **Lambda expressions**
   ```python
   lambda x: x if x > 0 else 0  # +2 (lambda + if)
   ```

### JavaScript/TypeScript Decision Points

For JavaScript/TypeScript, the script uses regex-based detection:

1. **if statements**
   ```javascript
   if (condition) {}    // +1
   ```

2. **for loops**
   ```javascript
   for (let i = 0; i < n; i++) {}  // +1
   ```

3. **while loops**
   ```javascript
   while (condition) {}  // +1
   ```

4. **switch cases**
   ```javascript
   switch (value) {
     case 1:            // +1
       break;
     case 2:            // +1
       break;
   }
   ```

5. **catch blocks**
   ```javascript
   try {}
   catch (e) {}        // +1
   ```

6. **Logical operators** (&&, ||)
   ```javascript
   if (a && b) {}      // +2 (if + &&)
   if (x || y) {}      // +2 (if + ||)
   ```

7. **Ternary operators**
   ```javascript
   result = condition ? a : b;  // +1
   ```

**Note**: JavaScript/TypeScript complexity uses regex parsing, which is less accurate than Python's AST-based approach. Some edge cases may be missed or miscounted.

## Complexity Calculation Examples

### Example 1: Simple Function (Complexity = 1)

```python
def get_user_name(user):
    return user.name
```

**Complexity**: 1 (base complexity, no decision points)

### Example 2: Single If Statement (Complexity = 2)

```python
def get_display_name(user):
    if user.display_name:
        return user.display_name
    return user.name
```

**Complexity**: 1 (base) + 1 (if) = **2**

### Example 3: If-Elif-Else (Complexity = 3)

```python
def get_user_status(user):
    if user.is_active:
        return "active"
    elif user.is_suspended:
        return "suspended"
    else:
        return "inactive"
```

**Complexity**: 1 (base) + 1 (if) + 1 (elif) = **3**

### Example 4: Loop with Condition (Complexity = 3)

```python
def count_active_users(users):
    count = 0
    for user in users:
        if user.is_active:
            count += 1
    return count
```

**Complexity**: 1 (base) + 1 (for) + 1 (if) = **3**

### Example 5: Boolean Operators (Complexity = 4)

```python
def can_edit_post(user, post):
    if user.is_admin or (user.id == post.author_id and not post.is_locked):
        return True
    return False
```

**Complexity**: 1 (base) + 1 (if) + 1 (or) + 1 (and) = **4**

### Example 6: Nested Conditions (Complexity = 5)

```python
def validate_user(user):
    if user is None:
        return False

    if user.email:
        if "@" in user.email:
            return True

    return False
```

**Complexity**: 1 (base) + 1 (if) + 1 (if) + 1 (if) = **4**

### Example 7: High Complexity Function (Complexity = 12)

```python
def process_order(order, user):
    if not order:
        raise ValueError("Order required")

    if not user or not user.is_active:
        raise ValueError("Active user required")

    if order.status == "pending":
        if user.is_admin or order.user_id == user.id:
            if order.total > 0:
                for item in order.items:
                    if item.quantity <= 0:
                        raise ValueError("Invalid quantity")

                    if item.price < 0:
                        raise ValueError("Invalid price")

                order.status = "processing"
                return True

    return False
```

**Complexity**: 1 (base) + 2 (if × 2) + 2 (if with or/and) + 1 (if) + 1 (if with or) + 1 (if) + 1 (for) + 2 (if × 2) = **12**

## Interpretation Guidelines

### Complexity Thresholds

| Complexity | Interpretation | Action |
|------------|----------------|--------|
| 1-5 | **Simple** - Easy to understand and test | None required |
| 6-10 | **Moderate** - Still manageable | Monitor, consider simplification |
| 11-15 | **Complex** - Difficult to test thoroughly | **Refactor recommended** |
| 16-20 | **High** - High risk of bugs | **Refactor urgently** |
| 21+ | **Very High** - Nearly untestable | **Critical refactoring needed** |

### PACT Framework Recommendations

- **Default threshold**: 10 (warn on functions > 10)
- **Critical threshold**: 15 (must refactor before adding features)
- **Maximum acceptable**: 20 (block PRs, require justification)

### Context Matters

Some functions legitimately have higher complexity:

1. **State machines**: May have many cases but clear logic
2. **Parsers**: Often have complex branching for grammar rules
3. **Validators**: May check many conditions sequentially

**Mitigation**: Extract decision logic into well-named helper functions.

## Testing Implications

### Test Coverage by Complexity

**Minimum test coverage targets**:

| Complexity | Minimum Coverage | Recommended Test Cases |
|------------|------------------|------------------------|
| 1-5 | 80% | Happy path + 1-2 edge cases |
| 6-10 | 85% | All decision paths + edge cases |
| 11-15 | 90% | Full branch coverage + error cases |
| 16+ | 95% | Complete path coverage + integration tests |

### Test Case Estimation

A rough estimate: **Number of test cases ≈ Complexity**

For a function with complexity 10, aim for at least 10 test cases covering different decision paths.

## Refactoring Strategies

### Strategy 1: Extract Conditions

**Before** (Complexity = 5):
```python
def can_process(user, order):
    if user.is_active and order.status == "pending" and order.total > 0:
        return True
    return False
```

**After** (Complexity = 2 × 2 = 4 total):
```python
def is_user_active(user):
    return user.is_active

def is_order_valid(order):
    return order.status == "pending" and order.total > 0

def can_process(user, order):
    if is_user_active(user) and is_order_valid(order):
        return True
    return False
```

### Strategy 2: Extract Loops

**Before** (Complexity = 8):
```python
def validate_items(items):
    errors = []
    for item in items:
        if not item.name:
            errors.append("Name required")
        if item.price < 0:
            errors.append("Invalid price")
        if item.quantity <= 0:
            errors.append("Invalid quantity")
    return errors
```

**After** (Complexity = 3 + 4 = 7 total, better separation):
```python
def validate_item(item):
    errors = []
    if not item.name:
        errors.append("Name required")
    if item.price < 0:
        errors.append("Invalid price")
    if item.quantity <= 0:
        errors.append("Invalid quantity")
    return errors

def validate_items(items):
    errors = []
    for item in items:
        errors.extend(validate_item(item))
    return errors
```

### Strategy 3: Use Polymorphism

**Before** (Complexity = 6):
```python
def calculate_discount(customer, order):
    if customer.type == "premium":
        return order.total * 0.2
    elif customer.type == "standard":
        return order.total * 0.1
    elif customer.type == "new":
        return order.total * 0.05
    return 0
```

**After** (Complexity = 1 per method):
```python
class PremiumCustomer:
    def calculate_discount(self, order):
        return order.total * 0.2

class StandardCustomer:
    def calculate_discount(self, order):
        return order.total * 0.1

class NewCustomer:
    def calculate_discount(self, order):
        return order.total * 0.05
```

### Strategy 4: Use Guard Clauses

**Before** (Complexity = 4, nested):
```python
def process_payment(user, amount):
    if user:
        if user.is_active:
            if amount > 0:
                return charge_card(user, amount)
    return None
```

**After** (Complexity = 4, but flatter):
```python
def process_payment(user, amount):
    if not user:
        return None
    if not user.is_active:
        return None
    if amount <= 0:
        return None

    return charge_card(user, amount)
```

## Accuracy Limitations

### Python (AST-based)

**High Accuracy**: AST parsing correctly identifies all decision points.

**Edge Cases**:
- Walrus operator (`:=`) in Python 3.8+: May not count correctly
- Complex comprehensions: Counts each decision separately

### JavaScript/TypeScript (Regex-based)

**Moderate Accuracy**: Regex parsing misses some cases.

**Known Limitations**:
- Nested arrow functions: May miscount
- Template literals with embedded logic: Not detected
- Chained ternary operators: May undercount

**Recommendation**: For production JavaScript/TypeScript analysis, use dedicated tools like `complexity-report` or `eslint-plugin-complexity`. Use this script for quick estimates only.

## Related Metrics

### Comparison with Other Metrics

| Metric | Measures | Relationship to Complexity |
|--------|----------|----------------------------|
| **Lines of Code (LOC)** | Size | High LOC often means high complexity |
| **Halstead Complexity** | Program vocabulary | Alternative complexity measure |
| **Maintainability Index** | Overall quality | Inversely related to complexity |
| **Cognitive Complexity** | Understandability | More nuanced than cyclomatic |

### When to Use Alternative Metrics

- **Cognitive Complexity**: Better for nested conditions (penalizes nesting more)
- **Essential Complexity**: Measures structured vs. unstructured flow
- **LOC**: Quick proxy for complexity in large codebases

## Further Reading

- **Original Paper**: McCabe, T. J. (1976). "A Complexity Measure". IEEE Transactions on Software Engineering.
- **Python AST**: https://docs.python.org/3/library/ast.html
- **Testing Coverage**: Martin Fowler on Test Coverage (martinfowler.com)
- **Cognitive Complexity**: SonarSource white paper on Cognitive Complexity

## Summary

Cyclomatic complexity provides an objective, quantitative measure of code complexity:

- **Formula**: 1 + number of decision points
- **Threshold**: 10 (warn), 15 (refactor urgently)
- **Testing**: Complexity ≈ minimum test cases needed
- **Refactoring**: Extract conditions, loops, use polymorphism, guard clauses
- **Accuracy**: High for Python (AST), moderate for JavaScript (regex)

Use complexity metrics to **guide refactoring decisions** and **prioritize testing efforts**, not as absolute rules. Context and code clarity matter more than hitting exact thresholds.
