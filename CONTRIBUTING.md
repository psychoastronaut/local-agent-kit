# Contributing

Thanks for helping. The most valuable contribution is **hardware results**: run
`lak tune` and `lak eval` on your machine and open a "Hardware results" issue (or a PR
adding `results/<gpu>.md` + `.json`).

## Development

- Everything is bash + Python stdlib. Please keep it dependency-free.
- `python3 eval/run_eval.py --self-test` must stay green: every task must fail on the
  untouched fixture and pass with its `solution/` overlay.
- Run `bash -n bin/lak` and `python3 -m py_compile scripts/*.py eval/run_eval.py` before sending a PR.

## Adding an eval task

Create `eval/tasks/<name>/` with `repo/` (3-10 files), `task.md`, `check.sh`
(exit 0 = pass), optional `hidden/` tests (copied in at check time by
`install_hidden`), and `solution/` (an overlay that makes the task pass). Prefer tasks
with an objective check; avoid ones that depend on wording.

## Privacy

Do not commit personal paths, hostnames, usernames or tokens. Use `$HOME` and
`config.env` variables.
