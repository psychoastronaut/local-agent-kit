<!-- DRAFT for r/LocalLLaMA. Not published. Fill the numbers from results/ before posting. -->

**Title:** A 35B MoE coding agent on a 12 GB GPU at ~40 t/s decode, 128k context (opencode / Claude Code + llama.cpp), with configs, a tuner and an eval harness

Hi all. I spent a while getting a local coding agent to work properly on a mid-range
box (RTX 3060 12 GB, Ryzen 5 3600, 32 GB DDR4-3200) and packaged everything as a small kit:
**local-agent-kit**.

**What you get**
- llama.cpp `llama-server` behind llama-swap, one endpoint serving both the OpenAI and
  the Anthropic API, so opencode *and* Claude Code (via `ANTHROPIC_BASE_URL`) work.
- Qwen3.6-35B-A3B Q4_K_M with `--n-cpu-moe 27 -c 131072 -ctk q8_0 -ctv q8_0`: 10.9 GB VRAM,
  ~750 t/s prefill, ~42 t/s decode.
- `lak tune`: sweeps context x `--n-cpu-moe` and tells you what fits with 1 GB headroom.
- `lak doctor`: finds the usual foot-guns (VRAM held by another container, wrong
  opencode provider key, `limit.context` != `-c`, tool calls not parsed).
- `lak eval`: 6 small fixture projects with hidden tests, so you can measure how often
  the agent actually fixes things instead of trusting vibes.

**Numbers** (see the repo for the full table): <paste table>

**Things that cost me hours**
- DDR4-2666 -> 3200 gave ~37% more decode: with expert offload you are memory-bandwidth bound.
- opencode: provider key must be `npm` (the old `package` is silently ignored), and
  `limit.context` must equal `-c`.
- One GPU = one model. Point main/small/title/compaction at the same alias or eat 25-40 s reloads.
- Claude Code sends `tool_reference` content blocks that crash the stock Qwen template
  ("Unexpected item type in content"); the kit ships a patched template.
- `CLAUDE_CODE_ATTRIBUTION_HEADER=0` or the prompt cache is invalidated every turn.

Repo: <link>. If you try it, please post your `lak tune` table in the "Hardware results"
issue template: I would like to build a table across GPUs.

Honest limitations: the eval tasks are small, a 3B-active model still fails some of them,
and the permission rules in the opencode config are a speed bump, not a sandbox.
