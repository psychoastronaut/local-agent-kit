from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    region: str
    revenue_cents: int
    growth: float  # fraction, 0.05 == 5 %


def sample_rows():
    return [
        Row("North", 1234567, 0.052),
        Row("South", 89050, -0.0125),
        Row("East", 100, 0.0),
    ]
