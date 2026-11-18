#!/usr/bin/env python3
"""Run a coding agent on small fixture projects and check the result.

For every task directory (eval/tasks/<name>/):
  repo/       fixture project, copied to a temp dir, `git init` + committed
  task.md     the prompt handed to the agent
  check.sh    exit 0 = pass. Runs in the working copy with $TASK_DIR set; hidden
              tests live in <task>/hidden/ and are copied in only at check time
  solution/   (optional) overlay that makes the task pass; used by --self-test
  task.json   (optional) {"repo": "/abs/path"} to use a project outside the task dir

Agent command: a shell string with {prompt} (shell-quoted task text), {alias}
and {prompt_file} placeholders. Default drives opencode headless:
  opencode run -m local/{alias} {prompt}
stdin is always /dev/null (opencode blocks forever on an open non-tty stdin).

Isolation note: hidden tests and solutions are NOT in the working copy, but the
protection is cooperative. An agent allowed to read absolute paths could open
eval/tasks/*/hidden or */solution. Keep external-directory access denied (the
shipped opencode config does) or run the harness from a copy without them.

Examples:
  python3 eval/run_eval.py --repeat 2
  python3 eval/run_eval.py --task fix-pagination --timeout 900
  python3 eval/run_eval.py --agent-cmd 'claude-code/claude-local -p {prompt} --permission-mode acceptEdits'
  python3 eval/run_eval.py --self-test     # validate the tasks themselves
"""
import argparse
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AGENT = "opencode run -m local/{alias} {prompt}"
GITIGNORE = "__pycache__/\n*.pyc\n.pytest_cache/\n.godot/\n"


def sh(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, **kw)


def git(cwd, *args):
    return sh(["git", "-c", "user.name=eval", "-c", "user.email=eval@example.invalid", *args], cwd)


def prepare(task_dir, work):
    repo = os.path.join(task_dir, "repo")
    meta = os.path.join(task_dir, "task.json")
    if os.path.isfile(meta):
        repo = json.load(open(meta)).get("repo", repo)
    shutil.copytree(repo, work, symlinks=True, dirs_exist_ok=True)
    if not os.path.exists(os.path.join(work, ".gitignore")):
        open(os.path.join(work, ".gitignore"), "w").write(GITIGNORE)
    shutil.rmtree(os.path.join(work, ".git"), ignore_errors=True)
    git(work, "init", "-q", "-b", "main")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "fixture")


def run_check(task_dir, work, timeout=300):
    env = dict(os.environ, TASK_DIR=task_dir)
    try:
        r = subprocess.run(["bash", os.path.join(task_dir, "check.sh")], cwd=work, env=env,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
    except subprocess.TimeoutExpired:
        return False, "check.sh timed out"


def run_agent(cmd, prompt, work, timeout, log_path):
    pf = os.path.join(os.path.dirname(work), "prompt.txt")  # outside the repo, so it is never in the diff
    with open(pf, "w") as f:
        f.write(prompt)
    full = cmd.format(prompt=shlex.quote(prompt), alias=shlex.quote(os.environ.get("LAK_MODEL_ALIAS", "qwen36")),
                      prompt_file=shlex.quote(pf))
    t0 = time.time()
    status = "done"
    with open(log_path, "w") as log:
        p = subprocess.Popen(full, shell=True, cwd=work, stdin=subprocess.DEVNULL,
                             stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            p.wait(timeout)
        except subprocess.TimeoutExpired:
            status = "timeout"
            os.killpg(p.pid, signal.SIGKILL)  # kill the whole process group
            p.wait()
    return status, p.returncode, time.time() - t0


def diff_stats(work):
    git(work, "add", "-A")
    stat = git(work, "diff", "--cached", "--stat").stdout.strip().splitlines()
    numstat = git(work, "diff", "--cached", "--numstat").stdout.strip().splitlines()
    files = [l.split("\t")[2] for l in numstat if l.count("\t") >= 2]
    return {"files_changed": len(files), "files": files,
            "diff_summary": stat[-1].strip() if stat else "no changes"}


def discover(tasks_dir, only):
    names = sorted(d for d in os.listdir(tasks_dir)
                   if os.path.isfile(os.path.join(tasks_dir, d, "task.md")))
    if only:
        missing = set(only) - set(names)
        if missing:
            sys.exit(f"unknown task(s): {', '.join(sorted(missing))}; available: {', '.join(names)}")
        names = [n for n in names if n in only]
    return names


def self_test(tasks_dir, names):
    bad = 0
    for n in names:
        td = os.path.abspath(os.path.join(tasks_dir, n))
        with tempfile.TemporaryDirectory(prefix="lak-self-") as w:
            work = os.path.join(w, "p")
            prepare(td, work)
            before, _ = run_check(td, work)
            sol = os.path.join(td, "solution")
            if os.path.isdir(sol):
                shutil.copytree(sol, work, dirs_exist_ok=True)
            after, out = run_check(td, work)
        ok = (not before) and after
        bad += not ok
        print(f"{'ok  ' if ok else 'BAD '} {n}: unsolved={'pass' if before else 'fail'} (want fail), "
              f"solved={'pass' if after else 'fail'} (want pass)")
        if not ok:
            print(out)
    return 1 if bad else 0


def markdown(results, meta):
    by = {}
    for r in results:
        by.setdefault(r["task"], []).append(r)
    lines = [f"Agent: `{meta['agent_cmd']}`  ", f"Timeout per task: {meta['timeout']} s", "",
             "| task | pass | median wall time | files changed (median) |", "|---|---:|---:|---:|"]

    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2]

    for t, rs in by.items():
        p = sum(r["passed"] for r in rs)
        lines.append(f"| {t} | {p}/{len(rs)} | {med([r['wall_s'] for r in rs]):.0f} s | "
                     f"{med([r['files_changed'] for r in rs])} |")
    tot = sum(r["passed"] for r in results)
    lines.append(f"| **total** | **{tot}/{len(results)}** | | |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks-dir", default=os.path.join(HERE, "tasks"))
    ap.add_argument("--task", action="append", help="run only this task (repeatable)")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--agent-cmd", default=DEFAULT_AGENT)
    ap.add_argument("--timeout", type=int, default=600, help="seconds per agent run")
    ap.add_argument("--out", default=os.path.join(HERE, "runs"), help="results directory")
    ap.add_argument("--keep", action="store_true", help="keep temp working copies")
    ap.add_argument("--self-test", action="store_true", help="validate tasks: fail unsolved, pass with solution/")
    args = ap.parse_args()

    tasks_dir = os.path.abspath(args.tasks_dir)
    names = discover(tasks_dir, args.task)
    if args.self_test:
        return self_test(tasks_dir, names)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = os.path.join(args.out, stamp)
    os.makedirs(out, exist_ok=True)
    results = []
    for name in names:
        td = os.path.join(tasks_dir, name)
        prompt = open(os.path.join(td, "task.md")).read().strip()
        for i in range(1, args.repeat + 1):
            work_root = tempfile.mkdtemp(prefix=f"lak-{name}-")
            work = os.path.join(work_root, "project")
            prepare(td, work)
            print(f"[{name} #{i}] running agent ...", flush=True)
            log = os.path.join(out, f"{name}-{i}.log")
            status, rc, wall = run_agent(args.agent_cmd, prompt, work, args.timeout, log)
            stats = diff_stats(work)
            ok, check_out = run_check(td, work)
            r = {"task": name, "run": i, "passed": ok, "agent_status": status, "agent_exit": rc,
                 "wall_s": round(wall, 1), "check_output": check_out[-600:], **stats}
            results.append(r)
            print(f"[{name} #{i}] {'PASS' if ok else 'FAIL'} ({status}, {wall:.0f}s, "
                  f"{stats['files_changed']} files)", flush=True)
            if args.keep:
                print(f"    kept: {work}")
            else:
                shutil.rmtree(work_root, ignore_errors=True)

    meta = {"agent_cmd": args.agent_cmd, "timeout": args.timeout, "repeat": args.repeat, "date": stamp}
    with open(os.path.join(out, "results.json"), "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=2)
    md = markdown(results, meta)
    with open(os.path.join(out, "results.md"), "w") as f:
        f.write(md)
    print("\n" + md)
    print(f"results: {out}")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
