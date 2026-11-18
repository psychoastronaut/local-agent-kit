from .data import Row


def _fmt_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"


def _fmt_pct(fraction: float) -> str:
    return f"{fraction * 100:+.1f}%"


def render(rows: list) -> str:
    lines = ["region,revenue,growth"]
    for r in rows:
        lines.append(f"{r.region},{_fmt_money(r.revenue_cents)},{_fmt_pct(r.growth)}")
    return "\n".join(lines) + "\n"
