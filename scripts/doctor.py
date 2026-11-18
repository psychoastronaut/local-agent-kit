#!/usr/bin/env python3
"""lak doctor: check the whole local-agent chain and explain what is wrong.

Checks: VRAM hogs, endpoint, /v1/models, a real tool-call round trip,
opencode config (provider key, limit.context vs -c), opencode version.
Exit code 0 when no check FAILs (warnings are allowed).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

HOST = os.environ.get("LAK_HOST", "127.0.0.1")
PORT = os.environ.get("LAK_PORT", "8080")
ALIAS = os.environ.get("LAK_MODEL_ALIAS", "qwen36")
BASE = f"http://{HOST}:{PORT}"
XDG = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
OC_CFG = os.environ.get("LAK_OPENCODE_CONFIG", os.path.join(XDG, "opencode", "opencode.jsonc"))
YAMLS = [os.environ.get("LAK_SWAP_YAML", ""), os.path.join(XDG, "local-agent-kit", "llama-swap.yaml")]

failed = 0


def report(level, name, msg=""):
    global failed
    if level == "FAIL":
        failed += 1
    print(f"[{level:4}] {name}" + (f": {msg}" if msg else ""))


def http(path, body=None, timeout=300):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def strip_jsonc(text):
    """Remove // and /* */ comments without touching strings (URLs contain //)."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1]); i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            i = text.find("*/", i) + 2 or n
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def check_gpu():
    if not shutil.which("nvidia-smi"):
        return report("WARN", "gpu", "nvidia-smi not found (CPU-only or non-NVIDIA?)")
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
             "--format=csv,noheader,nounits"], text=True).strip()
    except subprocess.CalledProcessError as e:
        return report("WARN", "gpu", f"nvidia-smi failed: {e}")
    procs = [l.split(", ") for l in out.splitlines() if l.strip()]
    hogs = [p for p in procs if "llama-server" not in p[1] and int(p[2]) > 500]
    if hogs:
        names = "; ".join(f"{p[1]} (pid {p[0]}, {p[2]} MiB)" for p in hogs)
        report("FAIL", "vram", f"other processes hold VRAM: {names}. llama-swap will die with "
               "'upstream command exited prematurely'. Stop them (e.g. docker stop ollama).")
    else:
        report("ok", "vram", "no other process is holding VRAM")


def check_endpoint():
    try:
        models = http("/v1/models", timeout=10)
    except Exception as e:
        report("FAIL", "endpoint", f"{BASE}/v1/models unreachable ({e}). Is llama-swap running? "
               "`systemctl --user status lak-llama-swap`")
        return False
    ids = [m["id"] for m in models.get("data", [])]
    report("ok", "endpoint", f"{BASE} up, {len(ids)} model(s) configured")
    if ALIAS not in ids:
        report("FAIL", "alias", f"'{ALIAS}' not in /v1/models; check LAK_MODEL_ALIAS and the yaml")
    else:
        report("ok", "alias", f"'{ALIAS}' is served")
    return True


def check_tool_call():
    body = {"model": ALIAS, "max_tokens": 1024, "temperature": 0,
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."}],
            "tools": [{"type": "function", "function": {
                "name": "get_weather", "description": "Get current weather for a city",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                               "required": ["city"]}}}],
            "tool_choice": "auto"}
    try:
        r = http("/v1/chat/completions", body)  # may load the model: slow on cold start
    except Exception as e:
        return report("FAIL", "tool-call", f"request failed: {e}")
    msg = r["choices"][0]["message"]
    calls = msg.get("tool_calls") or []
    if not calls:
        return report("FAIL", "tool-call", "no tool_calls in reply (content: "
                      f"{(msg.get('content') or '')[:80]!r}). Missing --jinja or a broken chat template?")
    try:
        json.loads(calls[0]["function"]["arguments"])
        report("ok", "tool-call", f"got {calls[0]['function']['name']}({calls[0]['function']['arguments']})")
    except ValueError:
        report("FAIL", "tool-call", "tool_calls arguments are not valid JSON "
               "(presence_penalty > 0 is a known cause)")


def check_messages_api():
    """Claude Code talks to /v1/messages; llama-swap must proxy it."""
    body = {"model": ALIAS, "max_tokens": 8,
            "messages": [{"role": "user", "content": "Say hi."}]}
    try:
        r = http("/v1/messages", body)
    except Exception as e:
        return report("FAIL", "messages-api", f"POST /v1/messages failed ({e}); Claude Code needs this")
    if r.get("type") == "message" and r.get("content") is not None:
        report("ok", "messages-api", "Anthropic Messages API works (Claude Code path)")
    else:
        report("FAIL", "messages-api", f"unexpected reply shape: {str(r)[:120]}")


def yaml_ctx():
    """Return the -c value for ALIAS from the rendered llama-swap yaml, if found."""
    for path in YAMLS:
        if path and os.path.isfile(path):
            text = open(path).read()
            m = re.search(r"^\s{2}%s:\s*$(.*?)(?=^\s{2}\S|\Z)" % re.escape(ALIAS), text, re.S | re.M)
            block = m.group(1) if m else text
            c = re.search(r"(?:^|\s)-c\s+(\d+)", block)
            if c:
                return int(c.group(1)), path
    return None, None


def check_opencode():
    ver = shutil.which("opencode")
    if not ver:
        report("WARN", "opencode", "not on PATH (skip if you only use Claude Code)")
    else:
        v = subprocess.run(["opencode", "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        report("ok", "opencode", f"version {v.stdout.strip() or v.stderr.strip()}")
    if not os.path.isfile(OC_CFG):
        return report("WARN", "opencode-config", f"{OC_CFG} not found (run `lak render --apply`)")
    try:
        cfg = json.loads(strip_jsonc(open(OC_CFG).read()))
    except ValueError as e:
        return report("FAIL", "opencode-config", f"cannot parse {OC_CFG}: {e}")
    for name, prov in cfg.get("provider", {}).items():
        base = (prov.get("options") or {}).get("baseURL", "")
        if HOST not in base and "127.0.0.1" not in base and "localhost" not in base:
            continue
        if "npm" not in prov:
            hint = " ('package' is an old key that opencode silently ignores)" if "package" in prov else ""
            report("FAIL", f"provider.{name}", f"missing 'npm' key{hint}; use \"npm\": \"@ai-sdk/openai-compatible\"")
        else:
            report("ok", f"provider.{name}", f"npm = {prov['npm']}")
        if f":{PORT}" not in base:
            report("WARN", f"provider.{name}", f"baseURL {base} does not use port {PORT}")
        ctx, path = yaml_ctx()
        for mid, m in (prov.get("models") or {}).items():
            lim = (m.get("limit") or {}).get("context")
            out = (m.get("limit") or {}).get("output")
            if mid == ALIAS and out is not None:
                if lim and out >= lim // 2:
                    report("WARN", "limit.output", f"{out} is large relative to context {lim}")
                elif out < 1024:
                    report("WARN", "limit.output", f"{out} is very small; edits will be cut off")
                else:
                    report("ok", "limit.output", str(out))
            if mid == ALIAS and ctx and lim is not None:
                if lim == ctx:
                    report("ok", "limit.context", f"{lim} == llama-server -c ({path})")
                else:
                    report("FAIL", "limit.context", f"{lim} != -c {ctx}: compaction will loop or the server will truncate")
            elif mid == ALIAS and not ctx:
                report("WARN", "limit.context", "could not find llama-swap yaml to compare with -c")
    for key in ("model", "small_model"):
        val = cfg.get(key, "")
        if val and val != f"local/{ALIAS}" and val.startswith("local/"):
            report("WARN", key, f"{val} differs from local/{ALIAS}: two aliases means 25-40 s model reloads")


def main():
    check_gpu()
    if check_endpoint():
        check_tool_call()
        check_messages_api()
    check_opencode()
    print("\nall checks passed" if not failed else f"\n{failed} check(s) FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
