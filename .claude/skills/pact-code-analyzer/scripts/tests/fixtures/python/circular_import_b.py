"""
Test fixture for circular dependency detection (Module B).

This file imports from circular_import_a.py, which imports from this file.

Expected Dependency Analysis:
- Imports: circular_import_a
- Circular dependency detected: circular_import_b -> circular_import_a -> circular_import_b

Expected Complexity:
- function_b: Complexity 1
"""

from circular_import_a import function_a


def function_b(value):
    """Function that uses function_a."""
    if value > 10:
        return function_a(value + 1)
    return value
