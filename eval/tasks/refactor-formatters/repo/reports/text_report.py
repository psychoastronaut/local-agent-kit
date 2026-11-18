from .data import Row


def _fmt_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"


def _fmt_pct(fraction: float) -> str:
    return f"{fraction * 100:+.1f}%"


def render(rows: list) -> str:
    width = max(len(r.region) for r in rows)
    out = []
    for r in rows:
        out.append(f"{r.region:<{width}}  {_fmt_money(r.revenue_cents):>14}  {_fmt_pct(r.growth):>7}")
    total = sum(r.revenue_cents for r in rows)
    out.append(f"{'TOTAL':<{width}}  {_fmt_money(total):>14}")
    return "\n".join(out) + "\n"
