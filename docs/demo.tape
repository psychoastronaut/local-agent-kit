# VHS script for docs/demo.gif.   Render:  vhs docs/demo.tape
# Needs: vhs (+ttyd, ffmpeg), opencode, pytest, and a running llama-swap with
# the alias below. Run it from the repository root.

Output docs/demo.gif

Set Shell bash
Set FontSize 20
Set Width 1200
Set Height 760
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set PlaybackSpeed 1

# --- Hidden setup: neutral prompt, scratch copy of an eval fixture ----------
Hide
# A throwaway venv keeps interpreter paths neutral in pytest's header.
Type "[ -d /tmp/lak-venv ] || (python3 -m venv /tmp/lak-venv && /tmp/lak-venv/bin/pip install -q pytest)" Enter
Type "export PATH=$PWD/bin:$PATH && . /tmp/lak-venv/bin/activate && export PS1='$ '" Enter
Type "rm -rf /tmp/lak-demo && cp -r eval/tasks/fix-pagination/repo /tmp/lak-demo && cd /tmp/lak-demo" Enter
Type "git init -q && git add -A && git -c user.name=demo -c user.email=demo@example.invalid commit -qm fixture" Enter
Type "clear" Enter
Show

# --- 1. Health check --------------------------------------------------------
Type "lak doctor 2>&1 | head -5" Enter
Sleep 8s

# --- 2. The failing test ----------------------------------------------------
Type "clear" Enter
Type "pytest -q 2>&1 | tail -4" Enter
Sleep 3s

# --- 3. The agent fixes it (the wait is hidden; the output stays on screen) -
Type "clear" Enter
Type `ocrun -m local/qwen36 "tests/test_pager.py has a failing test. Find the bug in the library code and fix it."` Enter
Hide
# Wait until the shell prompt is back (agent finished). Generous timeout.
Wait@300s /^\$$/
Show
Sleep 5s

# --- 4. Green ---------------------------------------------------------------
Type "clear" Enter
Type "git diff --stat | tail -3 && pytest -q 2>&1 | tail -2" Enter
Sleep 5s
