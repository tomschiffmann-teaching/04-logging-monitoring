"""
Shop checkout calculator.

Cart:  2 coffee (7.00 each) + 1 cheese (4.50) + 3 bread (2.00) = 24.50 subtotal
Rules: - 10% discount when subtotal is over 20.00
       - loyalty: 150 points -> 1.50 off (1 point = 0.01, capped at 5.00 off)

EXPECTED correct final total:
    24.50  - 2.45 (10% discount)  - 1.50 (loyalty)  =  20.55

But this program prints something else. Don't read to "find" it —
RUN it, then add logs after each step to see where 24.50 stops becoming 20.55.
"""

PRODUCTS = {
    "apple": 0.50,
    "bread": 2.00,
    "milk": 1.20,
    "cheese": 4.50,
    "coffee": 7.00,
}


def calculate_cart_total(cart):
    total = 0.0
    for item, quantity in cart.items():
        price = PRODUCTS[item]
        total += price * quantity
    return total


def apply_discount(total):
    # 10% off when the order is over 20.00
    if total > 20:
        discount = total * 0.10
        discounted = total - discount
    return total


def apply_loyalty_points(total, points):
    # 1 point = 0.01 off, but never more than 5.00 off
    reduction = points / 100
    if reduction > 5:
        reduction = 5
    total = total - reduction
    return total


def checkout(cart, loyalty_points):
    subtotal = calculate_cart_total(cart)
    after_discount = apply_discount(subtotal)
    final_total = apply_loyalty_points(after_discount, loyalty_points)
    return final_total


if __name__ == "__main__":
    cart = {"coffee": 2, "cheese": 1, "bread": 3}
    final = checkout(cart, loyalty_points=150)
    print(f"Final total: {final:.2f}")
    print("Expected:    20.55")
