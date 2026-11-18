import pytest

from pager.core import page_count, page_slice
from pager.render import pager_label


def test_partial_last_page():
    assert page_count(21, 10) == 3


def test_exact_multiple_has_no_empty_last_page():
    assert page_count(20, 10) == 2


def test_slice_middle():
    assert page_slice(list(range(25)), 2, 10) == list(range(10, 20))


def test_label():
    assert pager_label(45, 10, 2) == "Page 2 of 5"


def test_bad_per_page():
    with pytest.raises(ValueError):
        page_count(5, 0)
