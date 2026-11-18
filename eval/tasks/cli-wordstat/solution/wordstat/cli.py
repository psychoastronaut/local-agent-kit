import argparse
import json
import sys
from collections import Counter

from .counter import count_words, ranked


def positive(s):
    n = int(s)
    if n < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return n


def non_negative(s):
    n = int(s)
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wordstat", description="Count word frequencies.")
    p.add_argument("files", nargs="+", help="input files, or '-' for stdin")
    p.add_argument("--top", type=positive)
    p.add_argument("--min-length", type=non_negative, default=0)
    p.add_argument("--json", action="store_true")
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
    pairs = [(w, n) for w, n in ranked(total) if len(w) >= args.min_length]
    if args.top:
        pairs = pairs[: args.top]
    if args.json:
        print(json.dumps(dict(pairs)))
    else:
        for word, n in pairs:
            print(f"{word} {n}")
    return 0
