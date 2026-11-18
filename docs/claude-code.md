# Claude Code notes

`claude-code/claude-local` runs Claude Code against the local llama-swap endpoint with an
isolated config dir (`~/.claude-local` by default). Copy `claude-code/settings.json` there
as `settings.json` if you want the shipped defaults.

**Not a sandbox.** The permission rules in `settings.json` are a speed bump. `Bash(python3:*)`
allows arbitrary code, and deny rules such as `Bash(rm -rf:*)` match command text only, so
env-prefixed or scripted deletions slip through. Use a container or VM for untrusted work.

## Optional: validate Godot edits after every Edit/Write

Add to `settings.json` (replace `<kit>` with the path of this checkout; put `tools/godot-check`
on your PATH first, the hook warns loudly if it is missing):

```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": "<kit>/claude-code/hooks/godot-postedit.sh", "timeout": 60 }
      ]
    }
  ]
}
```
