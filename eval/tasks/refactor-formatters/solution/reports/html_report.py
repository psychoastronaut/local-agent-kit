from .data import Row
from .fmt import fmt_money, fmt_pct


def render(rows: list) -> str:
    cells = []
    for r in rows:
        cells.append(
            f"<tr><td>{r.region}</td><td>{fmt_money(r.revenue_cents)}</td>"
            f"<td>{fmt_pct(r.growth)}</td></tr>"
        )
    return "<table>\n" + "\n".join(cells) + "\n</table>\n"
