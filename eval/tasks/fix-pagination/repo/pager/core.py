def page_count(total_items: int, per_page: int) -> int:
    """Number of pages needed for `total_items` (0 items -> 0 pages)."""
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    return total_items // per_page + 1


def page_slice(items: list, page: int, per_page: int) -> list:
    """Items on 1-based `page`; out-of-range pages give an empty list."""
    if page < 1:
        return []
    start = (page - 1) * per_page
    return items[start:start + per_page]
