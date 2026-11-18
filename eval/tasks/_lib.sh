# Shared helpers sourced by every check.sh.
# Contract: cwd = the agent's working copy, $TASK_DIR = the task directory.
run_pytest() {
  if command -v pytest >/dev/null 2>&1; then pytest -q -p no:cacheprovider "$@"
  else python3 -m pytest -q -p no:cacheprovider "$@"; fi
}
# Copy hidden tests in only now, so the agent could never read or game them.
install_hidden() { mkdir -p tests; cp "$TASK_DIR"/hidden/*.py tests/; }
