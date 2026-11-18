"""Discount codes. Kinds: 'percent' (value = whole percent) and 'fixed' (value = cents)."""

DISCOUNTS = {
    "SAVE10": ("percent", 10),
    "FIVEOFF": ("fixed", 500),
}


def discount_amount(code, subtotal: int) -> int:
    """Return the discount in cents for `code` on `subtotal` (0 for unknown/None codes)."""
    if not code or code not in DISCOUNTS:
        return 0
    kind, value = DISCOUNTS[code]
    if kind == "percent":
        return subtotal * value // 100
    return value
