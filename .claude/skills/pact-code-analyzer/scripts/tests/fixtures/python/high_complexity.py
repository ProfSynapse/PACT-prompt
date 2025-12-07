"""
Test fixture for high complexity Python code (exceeds threshold).

Expected Complexity Analysis Results:
- process_order: Complexity 12 (exceeds threshold)
- validate_user: Complexity 7 (below threshold)
- Total file complexity: 19
- Functions exceeding threshold (10): 1
- Average complexity: 9.5

Expected File Metrics:
- Total lines: ~80
- Functions: 2
- Classes: 0
- Imports: 0
"""


def process_order(order, user, inventory):
    """
    Complex order processing with multiple decision points.

    Complexity: 12
    - Base: 1
    - if not order: +1
    - if not user: +1
    - if not order.get('items'): +1
    - for loop: +1
    - if item not in inventory: +1
    - if inventory[item] < quantity: +1
    - if order.get('discount'): +1
    - and operator: +1
    - if total > 1000: +1
    - elif total > 500: +1
    - if user.get('premium'): +1
    """
    if not order:
        return {'error': 'No order provided'}

    if not user:
        return {'error': 'No user provided'}

    if not order.get('items'):
        return {'error': 'Order has no items'}

    total = 0
    for item, quantity in order['items'].items():
        if item not in inventory:
            return {'error': f'Item {item} not in inventory'}

        if inventory[item] < quantity:
            return {'error': f'Insufficient inventory for {item}'}

        total += quantity * 10  # Simplified pricing

    # Apply discounts
    if order.get('discount') and order['discount'] > 0:
        total = total * (1 - order['discount'])

    # Shipping calculation
    if total > 1000:
        shipping = 0
    elif total > 500:
        shipping = 5
    else:
        shipping = 10

    # Premium user benefit
    if user.get('premium'):
        shipping = 0

    return {
        'total': total,
        'shipping': shipping,
        'grand_total': total + shipping
    }


def validate_user(user_data):
    """
    Validate user data with multiple checks.

    Complexity: 7
    - Base: 1
    - if not user_data: +1
    - if 'email' not in user_data: +1
    - or operator: +1
    - if 'age' in user_data: +1
    - and operator: +1
    - if len(user_data.get('password', '')) < 8: +1
    """
    if not user_data:
        return False

    if 'email' not in user_data or 'username' not in user_data:
        return False

    if 'age' in user_data and user_data['age'] < 18:
        return False

    if len(user_data.get('password', '')) < 8:
        return False

    return True
