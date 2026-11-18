from reports import csv_report, html_report, text_report
from reports.data import sample_rows


def test_csv():
    assert csv_report.render(sample_rows()) == (
        "region,revenue,growth\n"
        "North,$12,345.67,+5.2%\n"
        "South,$890.50,-1.2%\n"
        "East,$1.00,+0.0%\n"
    )


def test_text():
    out = text_report.render(sample_rows())
    assert "$12,345.67    +5.2%" in out
    assert out.splitlines()[-1].startswith("TOTAL")


def test_html():
    assert "<td>$890.50</td><td>-1.2%</td>" in html_report.render(sample_rows())
