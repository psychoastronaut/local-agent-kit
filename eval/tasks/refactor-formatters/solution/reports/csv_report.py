from .data import Row
from .fmt import fmt_money, fmt_pct


def render(rows: list) -> str:
    lines = ["region,revenue,growth"]
    for r in rows:
        lines.append(f"{r.region},{fmt_money(r.revenue_cents)},{fmt_pct(r.growth)}")
    return "\n".join(lines) + "\n"
