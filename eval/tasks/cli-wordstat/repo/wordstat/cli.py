import argparse
import sys
from collections import Counter

from .counter import count_words, ranked


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wordstat", description="Count word frequencies.")
    p.add_argument("files", nargs="+", help="input files, or '-' for stdin")
    return p


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    total = Counter()
    for path in args.files:
        total += count_words(read_input(path))
    for word, n in ranked(total):
        print(f"{word} {n}")
    return 0
