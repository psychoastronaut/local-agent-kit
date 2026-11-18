from .models import Bookmark
from .util import normalize_tags


class BookmarkStore:
    def __init__(self):
        self._items = []

    def add(self, url, title, tags=()):
        """Add a bookmark; duplicate URLs are rejected with ValueError."""
        if any(b.url == url for b in self._items):
            raise ValueError(f"duplicate url: {url}")
        bm = Bookmark(url, title, normalize_tags(tags))
        self._items.append(bm)
        return bm

    def all(self):
        return list(self._items)

    def find_by_title(self, text):
        text = text.lower()
        return [b for b in self._items if text in b.title.lower()]
