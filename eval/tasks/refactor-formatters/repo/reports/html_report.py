from .data import Row


def _fmt_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"


def _fmt_pct(fraction: float) -> str:
    return f"{fraction * 100:+.1f}%"


def render(rows: list) -> str:
    cells = []
    for r in rows:
        cells.append(
            f"<tr><td>{r.region}</td><td>{_fmt_money(r.revenue_cents)}</td>"
            f"<td>{_fmt_pct(r.growth)}</td></tr>"
        )
    return "<table>\n" + "\n".join(cells) + "\n</table>\n"
