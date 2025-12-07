"""
Test fixture for moderate complexity Python code.

Expected Complexity Analysis Results:
- validate_email: Complexity 3 (2 if statements)
- calculate_discount: Complexity 4 (3 if/elif branches, else not counted)
- process_items: Complexity 4 (1 for loop, 1 if, 1 and operator)
- Total file complexity: 11
- Functions exceeding threshold (10): 0
- Average complexity: 3.7

Expected File Metrics:
- Total lines: ~50
- Functions: 3
- Classes: 0
- Imports: 1
"""

import re


def validate_email(email):
    """
    Validate email format.

    Complexity: 3
    - Base: 1
    - if not email: +1
    - if not re.match: +1
    """
    if not email:
        return False
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return False
    return True


def calculate_discount(total, customer_type):
    """
    Calculate discount based on customer type.

    Complexity: 4
    - Base: 1
    - if customer_type == 'premium': +1
    - elif customer_type == 'gold': +1
    - elif customer_type == 'silver': +1
    (else clause does not add complexity in Python AST)
    """
    if customer_type == 'premium':
        return total * 0.2
    elif customer_type == 'gold':
        return total * 0.15
    elif customer_type == 'silver':
        return total * 0.1
    else:
        return 0


def process_items(items):
    """
    Process list of items.

    Complexity: 4
    - Base: 1
    - for loop: +1
    - if condition: +1
    - and operator: +1
    """
    result = []
    for item in items:
        if item and item.get('active'):
            result.append(item['name'])
    return result
