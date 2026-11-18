#!/usr/bin/env bash
set -u; . "$TASK_DIR/../_lib.sh"; install_hidden
run_pytest tests
