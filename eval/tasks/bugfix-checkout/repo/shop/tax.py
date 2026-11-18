TAX_RATE_BP = 800  # 8.00 % expressed in basis points


def tax_for(amount_cents: int) -> int:
    """Tax on `amount_cents`, rounded half up to the cent."""
    return (amount_cents * TAX_RATE_BP + 5000) // 10000
