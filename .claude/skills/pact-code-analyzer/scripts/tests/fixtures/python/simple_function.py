"""
Test fixture for simple, low-complexity Python functions.

Expected Complexity Analysis Results:
- greet: Complexity 1 (no decision points)
- add_numbers: Complexity 1 (no decision points)
- Total file complexity: 2
- Functions exceeding threshold (10): 0
- Average complexity: 1.0

Expected File Metrics:
- Total lines: ~20
- Functions: 2
- Classes: 0
- Imports: 0
"""


def greet(name):
    """Simple function with no decision points."""
    return f"Hello, {name}!"


def add_numbers(a, b):
    """Simple arithmetic with no branching."""
    result = a + b
    return result
