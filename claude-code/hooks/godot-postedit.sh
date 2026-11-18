#!/usr/bin/env bash
# PostToolUse hook (matcher: Edit|Write). After a .gd/.tscn/.tres edit, run
# godot-check on the enclosing Godot project. Exit code 2 sends stderr back to
# the model so it can fix its own mistake before answering.
f=$(python3 -I -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
case "$f" in *.gd|*.tscn|*.tres) ;; *) exit 0 ;; esac
d=$(dirname "$f")
while [ "$d" != "/" ] && [ ! -f "$d/project.godot" ]; do d=$(dirname "$d"); done
[ -f "$d/project.godot" ] || exit 0
if ! command -v godot-check >/dev/null 2>&1; then
  echo "godot-postedit: godot-check is not on PATH; Godot edits are NOT being validated (see tools/godot-check)." >&2
  exit 0
fi
out=$(godot-check "$d" 2>&1); rc=$?
if [ $rc -ne 0 ]; then
  { echo "godot-check found errors after your edit of $f. Fix them before answering:"; echo "$out"; } >&2
  exit 2
fi
exit 0
