from .data import Row
from .fmt import fmt_money, fmt_pct


def render(rows: list) -> str:
    width = max(len(r.region) for r in rows)
    out = []
    for r in rows:
        out.append(f"{r.region:<{width}}  {fmt_money(r.revenue_cents):>14}  {fmt_pct(r.growth):>7}")
    total = sum(r.revenue_cents for r in rows)
    out.append(f"{'TOTAL':<{width}}  {fmt_money(total):>14}")
    return "\n".join(out) + "\n"
