def fmt_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"


def fmt_pct(fraction: float) -> str:
    return f"{fraction * 100:+.1f}%"
