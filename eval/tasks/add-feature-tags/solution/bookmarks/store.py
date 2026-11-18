from collections import Counter

from .models import Bookmark
from .util import normalize_tags


class BookmarkStore:
    def __init__(self):
        self._items = []

    def add(self, url, title, tags=()):
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

    def search(self, tags, match="all"):
        if match not in ("all", "any"):
            raise ValueError(f"bad match: {match}")
        wanted = normalize_tags(tags)
        if not wanted:
            hits = self._items
        elif match == "all":
            hits = [b for b in self._items if wanted <= b.tags]
        else:
            hits = [b for b in self._items if wanted & b.tags]
        return sorted(hits, key=lambda b: b.title.lower())

    def tag_counts(self):
        return dict(Counter(t for b in self._items for t in b.tags))
