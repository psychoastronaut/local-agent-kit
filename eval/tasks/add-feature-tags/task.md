Add tag search to the bookmarks library.

1. In `bookmarks/store.py` add `BookmarkStore.search(tags, match="all")`:
   - `tags` is a list of tag strings, compared case-insensitively.
   - `match="all"` returns bookmarks having every given tag; `match="any"` returns bookmarks having at least one.
   - Any other `match` value raises `ValueError`.
   - Empty `tags` returns all bookmarks.
   - Results are sorted by title, case-insensitively.
2. Add `BookmarkStore.tag_counts()` returning a dict `{tag: number_of_bookmarks}` with lowercase tags.
3. Add tests for both methods to the `tests/` directory (at least 3 new test functions) and make sure the whole suite passes.
