#!/usr/bin/env bash
set -u; . "$TASK_DIR/../_lib.sh"
# The agent must have ADDED at least 3 test functions (baseline: 3).
n=$(grep -rhE '^\s*def test_' tests | wc -l)
[ "$n" -ge 6 ] || { echo "expected >= 3 new test functions, found $((n-3))"; exit 1; }
install_hidden
run_pytest tests
