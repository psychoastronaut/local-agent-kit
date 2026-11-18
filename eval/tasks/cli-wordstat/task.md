Extend the `wordstat` command line tool (see README.md) with three options, keeping the
current behaviour as the default:

- `--top N`: only print the N most frequent words.
- `--min-length N`: ignore words shorter than N characters.
- `--json`: print a JSON object `{"word": count, ...}` (keys in the same order as the
  normal output) instead of the text lines.

Options combine (`--min-length` is applied before `--top`). Invalid values (e.g. `--top 0`
or a negative number) must make argparse exit with status 2. Add tests for the new options
to the existing test files and make the whole suite pass.
