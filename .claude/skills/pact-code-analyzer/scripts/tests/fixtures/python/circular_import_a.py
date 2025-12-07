"""
Test fixture for circular dependency detection (Module A).

This file imports from circular_import_b.py, which in turn imports from this file.

Expected Dependency Analysis:
- Imports: circular_import_b
- Circular dependency detected: circular_import_a -> circular_import_b -> circular_import_a

Expected Complexity:
- function_a: Complexity 1
"""

from circular_import_b import function_b


def function_a(value):
    """Function that uses function_b."""
    if value > 0:
        return function_b(value - 1)
    return 0
