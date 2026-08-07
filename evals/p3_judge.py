#!/usr/bin/env python3
"""P3 blind judge. Scores baseline vs styled responses on independent quality
dimensions, blind to condition, with randomized A/B order.

The judge NEVER sees a style file, a condition label, or any hint that
terseness is good. It scores two responses to the same prompt on:
  factual correctness, completeness, actionability, appropriate calibration.
Output is structured JSON per response. Order is randomized per pair and recorded.

Usage: python3 evals/p3_judge.py --pairs <baseline.jsonl> <candidate.jsonl> --out <judgments.jsonl> [--passes N] [--judge-model M]
"""
import argparse
import json
import os
import random
import re
import subprocess

JUDGE_PROMPT = """You are grading two AI-assistant responses to the same user prompt. You do not know how either was produced. Grade each response on its own merits. Do not reward or penalize brevity or length; do not consider formatting style, tone, or politeness.

User prompt:
{prompt}

Response A:
{resp_a}

Response B:
{resp_b}

Score each response on these four dimensions, 1 (worst) to 5 (best):
- correctness: are the factual and technical claims accurate?
- completeness: does it actually answer the question asked, covering what was needed?
- actionability: can the user act on it (concrete, runnable, specific)?
- calibration: does it claim exactly what it can support — no fabrication, no overclaiming, no under-answering when it could know?

Reply with ONLY a JSON object, no other text:
{{"A": {{"correctness": 1-5, "completeness": 1-5, "actionability": 1-5, "calibration": 1-5}}, "B": {{"correctness": 1-5, "completeness": 1-5, "actionability": 1-5, "calibration": 1-5}}}}"""


def judge(model, prompt, ra, rb, profile=""):
    full = JUDGE_PROMPT.format(prompt=prompt, resp_a=ra, resp_b=rb)
    cmd = ["omp"]
    if profile:
        cmd += ["--profile", profile]
    cmd += ["-p", "--no-tools", "--model", model, "--thinking", "high", full]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        out = p.stdout.strip()
        m = re.search(r"\{.*\}", out, re.S)
        if m:
            return json.loads(m.group(0)), None
        return None, f"unparseable: {out[:120]}"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except json.JSONDecodeError as e:
        return None, f"json: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs=2, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--passes", type=int, default=1)
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--profile", default=os.environ.get("OMP_PROFILE", ""),
                    help="omp profile (omit for install default)")
    ap.add_argument("--cases", nargs="+", default=["evals/cases-v2.jsonl"])
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    base = {(json.loads(l)["case_id"], json.loads(l)["trial"]): json.loads(l) for l in open(args.pairs[0])}
    cand = {(json.loads(l)["case_id"], json.loads(l)["trial"]): json.loads(l) for l in open(args.pairs[1])}
    keys = sorted(set(base) & set(cand))
    rng = random.Random(args.seed)

    # Prompts live in the cases file, keyed by case_id (result rows carry no prompt).
    prompts = {}
    for cf in args.cases:
        for l in open(cf):
            c = json.loads(l)
            prompts[c["id"]] = c["prompt"]

    done = set()
    try:
        for l in open(args.out):
            d = json.loads(l)
            done.add((d["case_id"], d["trial"], d["pass"]))
    except FileNotFoundError:
        pass

    for (cid, trial) in keys:
        b, c = base[(cid, trial)], cand[(cid, trial)]
        # Randomize A/B order; record it. order='bc' means A=baseline, B=candidate.
        order = "bc" if rng.random() < 0.5 else "cb"
        ra, rb = (b["response"], c["response"]) if order == "bc" else (c["response"], b["response"])
        for p in range(1, args.passes + 1):
            if (cid, trial, p) in done:
                continue
            scores, err = judge(args.judge_model, prompts[cid], ra, rb, args.profile)
            rec = {"case_id": cid, "trial": trial, "pass": p, "order": order,
                   "judge_model": args.judge_model, "scores": scores, "error": err}
            with open(args.out, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            tag = "ok" if scores else f"ERR {err}"
            print(f"[{cid} t{trial} p{p}] order={order} {tag}", flush=True)


if __name__ == "__main__":
    main()
