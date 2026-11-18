from .discounts import discount_amount
from .models import Cart
from .tax import tax_for


def checkout(cart: Cart, code=None) -> dict:
    """Compute the order summary for `cart`, optionally applying a discount `code`."""
    subtotal = cart.subtotal
    discount = discount_amount(code, subtotal)
    tax = tax_for(subtotal)
    total = subtotal - discount + tax
    return {"subtotal": subtotal, "discount": discount, "tax": tax, "total": total}
