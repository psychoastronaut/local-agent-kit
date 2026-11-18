def normalize_tags(tags):
    """Lowercase, strip and de-duplicate tags, dropping empty ones."""
    return frozenset(t.strip().lower() for t in tags if t and t.strip())
