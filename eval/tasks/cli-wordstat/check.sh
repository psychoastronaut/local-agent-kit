#!/usr/bin/env bash
set -u; . "$TASK_DIR/../_lib.sh"
n=$(grep -rhE "^\s*def test_" tests | wc -l)
[ "$n" -ge 4 ] || { echo "no new tests added"; exit 1; }
install_hidden
run_pytest tests
