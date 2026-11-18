import re
from collections import Counter

WORD = re.compile(r"[a-z']+")


def count_words(text: str) -> Counter:
    return Counter(WORD.findall(text.lower()))


def ranked(counts: Counter) -> list:
    """(word, count) pairs: highest count first, ties alphabetical."""
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
