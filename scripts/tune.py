#!/usr/bin/env python3
"""Sweep context size x --n-cpu-moe for a MoE GGUF and report VRAM + speed.

Starts llama-server on a spare port for every combination, waits for /health,
sends two requests with a FRESH random prompt each (so the prompt cache cannot
inflate prefill numbers), reads the `timings` block, records VRAM from
nvidia-smi, and kills the server. OOM / early exit is detected and reported.

Example:
  python3 scripts/tune.py --model ~/models/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf \\
      --ctx 65536,131072 --ncpumoe 24,27,30 --json results/mine.json

Pure stdlib. Stop llama-swap (or anything else holding VRAM) first, otherwise
the numbers are wrong; the script warns when VRAM is not idle at start.
"""
import argparse
import json
import os
import random
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request

WORDS = ("alpha beta gamma delta function return value class import loop index "
         "buffer thread socket queue stream token cache parse render commit").split()


def vram():
    """Return (used_mib, total_mib) of GPU 0, or None without nvidia-smi."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total",
             "--format=csv,noheader,nounits"], text=True).splitlines()[0]
        used, total = (int(x) for x in out.split(","))
        return used, total
    except (OSError, subprocess.CalledProcessError, ValueError, IndexError):
        return None


def http_json(url, body=None, timeout=600):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def bench_request(base, model, prompt_words, max_tokens):
    rng = random.Random(time.time_ns())  # fresh prompt every call
    text = " ".join(rng.choice(WORDS) for _ in range(prompt_words))
    body = {"model": model, "max_tokens": max_tokens, "temperature": 0.6,
            "messages": [{"role": "user", "content": text +
                          "\n\nWrite a python function that reverses a string, "
                          "with a docstring. Be brief."}]}
    t = http_json(base + "/v1/chat/completions", body)["timings"]
    return t["prompt_n"], t["prompt_per_second"], t["predicted_per_second"]


OOM_MARKERS = ("out of memory", "cudamalloc failed", "failed to allocate", "cuda error")


def log_has_oom(path):
    try:
        text = open(path, errors="replace").read().lower()
    except OSError:
        return False
    return any(m in text for m in OOM_MARKERS)


def stop_group(proc):
    """Terminate llama-server and anything it spawned (own process group)."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        try:
            proc.wait(20 if sig == signal.SIGTERM else 5)
            return
        except subprocess.TimeoutExpired:
            continue


def run_one(args, ctx, ncpumoe):
    res = {"ctx": ctx, "n_cpu_moe": ncpumoe, "status": "ok"}
    log = tempfile.NamedTemporaryFile("w+", suffix=".log", prefix="lak-tune-", delete=False)
    cmd = [os.path.join(args.llama_bin, "llama-server"), "-m", args.model,
           "--alias", "tune", "--host", "127.0.0.1", "--port", str(args.port),
           "-c", str(ctx), "-ngl", "99", "--n-cpu-moe", str(ncpumoe),
           "-ctk", args.kv_type, "-ctv", args.kv_type, "-fa", "on", "--jinja",
           "--reasoning-budget", "256"] + shlex.split(args.extra)
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    base = f"http://127.0.0.1:{args.port}"
    try:
        deadline = time.time() + args.load_timeout
        healthy = False
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(base + "/health", timeout=2) as r:
                    if json.load(r).get("status") == "ok":
                        healthy = True
                        break
            except Exception:
                pass
            time.sleep(2)
        if not healthy:
            log.flush()
            res["status"] = "OOM" if log_has_oom(log.name) else "failed"
            res["log"] = log.name
            return res
        # n_prompt words ~ 1.3 tokens each; keep well under ctx.
        words = min(12000, max(500, int(ctx * 0.5)))
        runs = [bench_request(base, "tune", words, args.max_tokens)
                for _ in range(args.requests)]
        v = vram()
        res.update(prompt_n=runs[-1][0],
                   prefill_tps=round(sum(r[1] for r in runs) / len(runs), 1),
                   decode_tps=round(sum(r[2] for r in runs) / len(runs), 1))
        if v:
            res["vram_mib"], res["vram_total_mib"] = v
            res["headroom_mib"] = v[1] - v[0]
        return res
    except Exception as e:  # request failures, timeouts; OOM can also strike on the first request
        log.flush()
        res["status"] = "OOM" if log_has_oom(log.name) else f"error: {e}"
        res["log"] = log.name
        return res
    finally:
        stop_group(proc)
        time.sleep(3)  # let the driver release VRAM before the next run


def recommend(rows, min_headroom):
    ok = [r for r in rows if r["status"] == "ok" and r.get("headroom_mib", 1 << 30) >= min_headroom]
    if not ok:
        return None
    # An agent wants the largest window that fits, then the fastest decode.
    return max(ok, key=lambda r: (r["ctx"], r["decode_tps"]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default=None, help="path to the GGUF (default: $LAK_MODELS_DIR/$LAK_MODEL_FILE)")
    p.add_argument("--llama-bin", default=os.environ.get("LAK_LLAMA_BIN", ""), help="dir with llama-server")
    p.add_argument("--ctx", default="65536,131072", help="comma list of context sizes")
    p.add_argument("--ncpumoe", default="24,27,30", help="comma list of --n-cpu-moe values")
    p.add_argument("--port", type=int, default=9100, help="spare port for the test server")
    p.add_argument("--kv-type", default="q8_0", help="KV cache type for -ctk/-ctv")
    p.add_argument("--extra", default="", help="extra llama-server args, e.g. '--temp 0.6'")
    p.add_argument("--requests", type=int, default=2, help="requests per config (averaged)")
    p.add_argument("--max-tokens", type=int, default=300)
    p.add_argument("--load-timeout", type=int, default=300)
    p.add_argument("--min-headroom-mib", type=int, default=1024, help="free VRAM to keep (default 1 GiB)")
    p.add_argument("--json", help="write raw results to this file")
    args = p.parse_args()

    if not args.model:
        d, f = os.environ.get("LAK_MODELS_DIR"), os.environ.get("LAK_MODEL_FILE")
        if not (d and f):
            p.error("--model is required (or set LAK_MODELS_DIR and LAK_MODEL_FILE)")
        args.model = os.path.join(os.path.expanduser(d), f)
    args.model = os.path.expanduser(args.model)
    if not os.path.isfile(args.model):
        p.error(f"model not found: {args.model}")
    if not os.path.isfile(os.path.join(args.llama_bin, "llama-server")):
        p.error("llama-server not found; pass --llama-bin or set LAK_LLAMA_BIN")

    v = vram()
    if v and v[0] > 600:
        print(f"WARNING: {v[0]} MiB of VRAM already in use by other processes; "
              "stop llama-swap/Ollama first for clean numbers.", file=sys.stderr)

    rows = []
    for ctx in (int(x) for x in args.ctx.split(",")):
        for n in (int(x) for x in args.ncpumoe.split(",")):
            print(f"-> ctx={ctx} n-cpu-moe={n} ...", flush=True)
            r = run_one(args, ctx, n)
            rows.append(r)
            print("   ", {k: v for k, v in r.items() if k != "log"}, flush=True)

    print("\n| ctx | n-cpu-moe | VRAM (GiB) | headroom (GiB) | prefill t/s | decode t/s | status |")
    print("|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        g = lambda k: f"{r[k] / 1024:.2f}" if k in r else "-"
        print(f"| {r['ctx']} | {r['n_cpu_moe']} | {g('vram_mib')} | {g('headroom_mib')} | "
              f"{r.get('prefill_tps', '-')} | {r.get('decode_tps', '-')} | {r['status']} |")
    best = recommend(rows, args.min_headroom_mib)
    if best:
        print(f"\nRecommended: LAK_CTX={best['ctx']} LAK_NCPUMOE={best['n_cpu_moe']} "
              f"({best['decode_tps']} t/s decode, {best.get('headroom_mib', '?')} MiB free)")
    else:
        print(f"\nNo configuration kept >= {args.min_headroom_mib} MiB free. "
              "Raise --n-cpu-moe or lower --ctx.")
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"model": os.path.basename(args.model), "rows": rows, "recommended": best}, f, indent=2)
    return 0 if best else 1


if __name__ == "__main__":
    sys.exit(main())
