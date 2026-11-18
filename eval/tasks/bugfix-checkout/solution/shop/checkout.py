from .discounts import discount_amount
from .models import Cart
from .tax import tax_for


def checkout(cart: Cart, code=None) -> dict:
    subtotal = cart.subtotal
    discount = min(discount_amount(code, subtotal), subtotal)
    tax = tax_for(subtotal - discount)
    total = subtotal - discount + tax
    return {"subtotal": subtotal, "discount": discount, "tax": tax, "total": total}
