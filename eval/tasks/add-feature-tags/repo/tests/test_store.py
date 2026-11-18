import pytest

from bookmarks.store import BookmarkStore


def test_add_normalizes_tags():
    s = BookmarkStore()
    bm = s.add("http://a", "A", [" Python ", "python", ""])
    assert bm.tags == frozenset({"python"})


def test_duplicate_url_rejected():
    s = BookmarkStore()
    s.add("http://a", "A")
    with pytest.raises(ValueError):
        s.add("http://a", "Other")


def test_find_by_title_is_case_insensitive():
    s = BookmarkStore()
    s.add("http://a", "Python Tips")
    assert [b.url for b in s.find_by_title("python")] == ["http://a"]
