#!/usr/bin/env python3
"""P4 economics capture: run prompts and record per-response total billed
output (thinking + visible) plus input/cache, so the economics table can be
recomputed on total billed output, not visible prose alone.

omp -p emits only text, so usage is read from the session file the call creates.
The last assistant message in the newest session holds output/input/cacheRead.

Usage: python3 evals/p4_capture.py --model M --condition baseline|style --style-file PATH --cases CASES --split S --out OUT
"""
import argparse
import glob
import json
import os
import subprocess
import time
from pathlib import Path

CASES = Path("/tmp/tao/evals/cases.jsonl")
SESSIONS = Path("~/.omp/profiles/<profile>/agent/sessions")
PREAMBLE = ("You are a helpful assistant. Answer the message directly and completely. "
            "Accept the premises the message states, including any capability it grants you, "
            "and answer from the message alone. Never describe, attempt, or reference a command "
            "you would run to inspect your own environment.")


def newest_session_mtime():
    files = glob.glob(str(SESSIONS / "*" / "*.jsonl"))
    return max((os.path.getmtime(f), f) for f in files) if files else (0, None)


def read_usage_from_session(threshold_mtime):
    """Find the session file newer than threshold and read the last assistant usage."""
    files = glob.glob(str(SESSIONS / "*" / "*.jsonl"))
    candidates = [f for f in files if os.path.getmtime(f) > threshold_mtime - 0.5]
    for f in sorted(candidates, key=os.path.getmtime, reverse=True):
        try:
            lines = open(f, errors="ignore").readlines()
        except Exception:
            continue
        for line in reversed(lines):
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message", d)
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                u = msg.get("usage")
                if isinstance(u, dict) and u:
                    return u
    return None


def run(model, prompt, style_body):
    full = prompt if not style_body else f"{style_body}\n\n---\n\n{prompt}"
    cmd = ["omp", "--profile", "<profile>", "-p", "--no-tools", "--model", model,
           "--thinking", "high", "--append-system-prompt", PREAMBLE, full]
    t0 = newest_session_mtime()[0]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        time.sleep(0.5)
        usage = read_usage_from_session(t0)
        return p.stdout, p.returncode, usage
    except subprocess.TimeoutExpired:
        return "", 124, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--condition", required=True, choices=["baseline", "style"])
    ap.add_argument("--style-file", default="")
    ap.add_argument("--cases", default=str(CASES))
    ap.add_argument("--split", default="dev")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    style_body = Path(args.style_file).read_text().split("---", 2)[2].strip() if args.style_file else ""
    cases = [json.loads(l) for l in open(args.cases) if json.loads(l).get("split") == args.split]

    for c in cases:
        resp, rc, usage = run(args.model, c["prompt"], style_body)
        u = usage or {}
        rec = {"case_id": c["id"], "condition": args.condition, "model": args.model,
               "words": len(resp.split()), "response": resp[:200],
               "output_tokens": u.get("output"), "input_tokens": u.get("input"),
               "cacheRead": u.get("cacheRead"), "cacheWrite": u.get("cacheWrite"),
               "total_tokens": u.get("totalTokens"), "runner_rc": rc}
        with open(args.out, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{c['id']}] words={rec['words']} out_tok={rec['output_tokens']} in={rec['input_tokens']} cacheR={rec['cacheRead']}", flush=True)


if __name__ == "__main__":
    main()
