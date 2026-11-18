from reports import csv_report, html_report, text_report
from reports.data import Row


def test_negative_money_and_thousands():
    rows = [Row("X", -123456789, 1.5)]
    assert csv_report.render(rows).splitlines()[1] == "X,-$1,234,567.89,+150.0%"
    assert "-$1,234,567.89" in html_report.render(rows)


def test_text_total_matches():
    rows = [Row("A", 500, 0.1), Row("B", 250, -0.1)]
    assert "$7.50" in text_report.render(rows).splitlines()[-1]
