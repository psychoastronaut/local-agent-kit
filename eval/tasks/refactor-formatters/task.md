The `reports` package has the same money/percent formatting helpers copy-pasted into
three modules (`csv_report.py`, `text_report.py`, `html_report.py`).

Refactor: move the shared helpers into a new module `reports/fmt.py` (one definition of
`fmt_money` and one of `fmt_pct`), and make the three report modules import them.
Behaviour must not change: the existing tests must still pass. Do not edit the tests.
When you are done, no `def _fmt_money` / `def _fmt_pct` copies may remain in the report modules.
