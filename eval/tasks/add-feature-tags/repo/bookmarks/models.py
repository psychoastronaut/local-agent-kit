from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    url: str
    title: str
    tags: frozenset = frozenset()
