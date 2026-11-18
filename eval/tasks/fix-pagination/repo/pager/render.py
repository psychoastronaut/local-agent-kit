from .core import page_count


def pager_label(total_items: int, per_page: int, page: int) -> str:
    """E.g. 'Page 2 of 5'. Empty result sets read 'No results'."""
    pages = page_count(total_items, per_page)
    if pages == 0:
        return "No results"
    return f"Page {page} of {pages}"


def page_numbers(total_items: int, per_page: int) -> list:
    return list(range(1, page_count(total_items, per_page) + 1))
