---
name: godot4
description: GDScript pitfalls in Godot 4 that models confuse with Godot 3, and the write-check loop. Read before writing or editing any .gd/.tscn.
---

# Godot 4.x: do not use the Godot 3 API

- Dictionary: `erase(key)` (not `remove`). Array: `remove_at(i)` or `erase(value)`.
- `@export var`, `@onready var` (not `export` / `onready`). `await` (not `yield`). `signal.emit()` (not `emit_signal`).
- Colors in upper case: `Color.RED`. Integer grids: `Vector2i`. Always use static typing.
- `CharacterBody2D`/`CharacterBody3D` ALREADY HAS `velocity`: NEVER declare `var velocity`.
  `move_and_slide()` takes no arguments and returns `bool`; do not assign its result.

      Godot 3:  velocity = move_and_slide(velocity * speed)
      Godot 4:  velocity = velocity * speed
                move_and_slide()

## Errors that only show up when running (not at parse time)
- `Identifier "x" not declared`: a variable used in a function where it does not exist. Declare it in the right scope or pass it as a parameter.
- Particles (`GPUParticles3D`): need `process_material` and `draw_pass_1`; `emitting = true` with `one_shot = true`; only trigger after the scene is in the tree (`add_child` before `restart()`/`emitting`).
- `get_node("Path")` / `$Path` fails if the node does not exist yet: check the `.tscn` and use `@onready`.
- Signals: connect with `signal.connect(callable)`; the callable must accept the same arguments the signal emits.
- UIDs in `.tscn` (`uid://...`) cannot be invented. Reference by `res://` path if you do not know the uid.

## Mandatory loop
1. Read the file. 2. Make one small edit. 3. Run `godot-check` (project root).
4. Read the output. `[FAILED]` means fix and repeat. `OK` means you may answer.

To check a single script: `godot-check . res://dir/file.gd`.
