from pager.core import page_count, page_slice
from pager.render import page_numbers, pager_label


def test_zero_items():
    assert page_count(0, 10) == 0
    assert pager_label(0, 10, 1) == "No results"
    assert page_numbers(0, 10) == []


def test_one_item():
    assert page_count(1, 10) == 1


def test_last_partial_page_slice():
    assert page_slice(list(range(21)), 3, 10) == [20]


def test_out_of_range_pages():
    data = list(range(20))
    assert page_slice(data, 3, 10) == []
    assert page_slice(data, 0, 10) == []
    assert page_slice(data, -1, 10) == []


def test_page_numbers_exact():
    assert page_numbers(30, 10) == [1, 2, 3]
