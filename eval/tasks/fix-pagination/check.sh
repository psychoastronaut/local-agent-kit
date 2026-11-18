#!/usr/bin/env bash
. "$TASK_DIR/../_lib.sh"; set -u
install_hidden
run_pytest tests
