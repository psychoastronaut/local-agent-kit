#!/usr/bin/env python3
"""Fill @@NAME@@ markers in a template from the environment.

Usage: render.py TEMPLATE OUTPUT [--set NAME=VALUE ...]

Fails loudly if a marker has no value, so a typo never ships a half-rendered
config. Pure stdlib.
"""
import os
import re
import sys

MARK = re.compile(r"@@([A-Za-z0-9_]+)@@")


def render(text, values):
    missing = set()

    def sub(m):
        name = m.group(1)
        if name in values:
            return values[name]
        missing.add(name)
        return m.group(0)

    out = MARK.sub(sub, text)
    if missing:
        raise KeyError("no value for: " + ", ".join(sorted(missing)))
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, dst = argv[1], argv[2]
    values = dict(os.environ)
    for arg in argv[3:]:
        if arg == "--set":
            continue
        k, _, v = arg.partition("=")
        values[k] = v
    try:
        with open(src) as f:
            out = render(f.read(), values)
    except KeyError as e:
        print(f"render: {src}: {e}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, "w") as f:
        f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
