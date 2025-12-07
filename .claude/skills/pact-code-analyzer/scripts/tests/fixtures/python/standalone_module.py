"""
Test fixture for orphan module detection.

This module has no imports and is not imported by any other module in the fixtures.
It should be identified as an orphan module (excluding entry point patterns).

Expected Dependency Analysis:
- Imports: 0
- Imported by: 0 (orphan module)

Expected Complexity:
- standalone_function: Complexity 2
- helper_function: Complexity 1

Expected File Metrics:
- Functions: 2
- Classes: 0
"""


def standalone_function(data):
    """
    Standalone function with minimal complexity.

    Complexity: 2
    - Base: 1
    - if data: +1
    """
    if data:
        return helper_function(data)
    return None


def helper_function(value):
    """
    Helper function with no decision points.

    Complexity: 1
    """
    return value * 2
