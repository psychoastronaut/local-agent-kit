import pytest

from bookmarks.store import BookmarkStore


@pytest.fixture
def store():
    s = BookmarkStore()
    s.add("http://1", "zeta", ["Python", "web"])
    s.add("http://2", "Alpha", ["python"])
    s.add("http://3", "beta", ["Rust", "WEB"])
    return s


def titles(bms):
    return [b.title for b in bms]


def test_all_match(store):
    assert titles(store.search(["python", "web"])) == ["zeta"]


def test_any_match_sorted_case_insensitive(store):
    assert titles(store.search(["python", "rust"], match="any")) == ["Alpha", "beta", "zeta"]


def test_case_insensitive_query(store):
    assert titles(store.search(["WEB"], match="all")) == ["beta", "zeta"]


def test_empty_tags_returns_everything(store):
    assert titles(store.search([])) == ["Alpha", "beta", "zeta"]


def test_bad_match_raises(store):
    with pytest.raises(ValueError):
        store.search(["x"], match="some")


def test_tag_counts(store):
    assert store.tag_counts() == {"python": 2, "web": 2, "rust": 1}
