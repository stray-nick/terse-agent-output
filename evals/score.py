#!/usr/bin/env python3
"""Score the raw eval responses against the rubric-aligned mechanical metrics.

Reads evals/results/*.jsonl (one JSON object per line, fields: case_id, trial,
condition, model, response) and prints per-model baseline vs candidate means.

Usage: python3 evals/score.py
"""
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).parent / "results"

PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b")
PERFECT = re.compile(r"\b(have|has|had)\s+\w+(ed|en)\b")
FORBID_CLOSE = re.compile(r"(let me know if|hope this helps|feel free to)", re.I)
FORBID_OPEN = re.compile(
    r"^(great question|sure!?|certainly|let me |i'll |looking at your|to answer your question)",
    re.I,
)

MODELS = {
    "Opus 5": ("omp-dev-baseline-opus.jsonl", "omp-dev-candidate-opus.jsonl"),
    "GPT-5.6-terra": ("omp-dev-baseline-gpt.jsonl", "omp-dev-candidate-gpt.jsonl"),
    "Gemini-3.1-pro": ("omp-dev-baseline-gem.jsonl", "omp-dev-candidate-gem.jsonl"),
    "Sonnet 5": ("omp-dev-baseline-son.jsonl", "omp-dev-candidate-son.jsonl"),
    "GLM 5.2 Fast": ("omp-dev-baseline-glm300k.jsonl", "omp-dev-candidate-glm300k.jsonl"),
    "Claude (direct)": ("claude002-dev-responses.jsonl", None),
}


def metrics(text):
    """Return (words, passive_hits, perfect_hits, long_sent_pct, has_closer, has_opener)."""
    # Strip code fences before sentence-length analysis; they aren't prose.
    no_code = re.sub(r"```.*?```", "", text, flags=re.S)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", no_code) if s.strip()]
    words = len(text.split())
    passive = len(PASSIVE.findall(text))
    perfect = len(PERFECT.findall(text))
    long_sent = sum(1 for s in sents if len(s.split()) > 25) / max(len(sents), 1)
    closer = bool(FORBID_CLOSE.search(text))
    opener = bool(FORBID_OPEN.search(text.strip()))
    return words, passive, perfect, long_sent, closer, opener


def load(path):
    rows = []
    if path is None:
        return rows
    for line in open(RESULTS / path):
        rows.append(json.loads(line))
    return rows


def mean_stats(rows):
    agg = defaultdict(list)
    for r in rows:
        w, pv, pf, lp, cl, op = metrics(r["response"])
        for k, v in [("w", w), ("pv", pv), ("pf", pf), ("lp", lp), ("cl", int(cl)), ("op", int(op))]:
            agg[k].append(v)
    return {k: statistics.mean(v) for k, v in agg.items()}, len(rows)


def main():
    print(f"{'Model':<18} {'n':>4} {'base_w':>7} {'cand_w':>7} {'dw':>6} {'base_pv':>7} {'cand_pv':>7} {'base_ls':>7} {'cand_ls':>7} {'base_cl':>7} {'cand_cl':>7}")
    print("-" * 100)
    for label, (bfile, cfile) in MODELS.items():
        brows = load(bfile)
        # claude002-dev-responses.jsonl has both conditions in one file
        if cfile is None:
            crows = [r for r in brows if r.get("condition") == "candidate"]
            brows = [r for r in brows if r.get("condition") == "baseline"]
        else:
            crows = load(cfile)
        b, nb = mean_stats(brows)
        c, nc = mean_stats(crows)
        n = nb + nc
        print(
            f"{label:<18} {n:>4} {b['w']:>7.0f} {c['w']:>7.0f} {c['w']-b['w']:>+6.0f} "
            f"{b['pv']:>7.1f} {c['pv']:>7.1f} {b['lp']*100:>6.0f}% {c['lp']*100:>6.0f}% "
            f"{b['cl']*100:>6.0f}% {c['cl']*100:>6.0f}%"
        )


def p0_table():
    """P0 task-success: per-task-type pass rates by condition (pooled across models)."""
    from collections import defaultdict
    rows = [json.loads(l) for l in open(RESULTS / "p0-task-success.jsonl")]
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        agg[(r["task_id"], r["condition"])][r["grade"]] += 1
    print("\n=== P0 task-success (120 task-runs, tools on, 2 models x 3 trials) ===")
    print(f"{'task':<22} {'cond':<9} {'pass':>4} {'fail':>4} {'rate':>6}")
    bp = bf = sp = sf = 0
    for task in sorted(set(r["task_id"] for r in rows)):
        for cond in ["baseline", "style"]:
            g = agg[(task, cond)]
            p, fl = g.get("pass", 0), g.get("fail", 0)
            tot = p + fl
            print(f"{task:<22} {cond:<9} {p:>4} {fl:>4} {p}/{tot}")
            if cond == "baseline":
                bp, bf = bp + p, bf + fl
            else:
                sp, sf = sp + p, sf + fl
    print(f"{'TOTAL':<22} baseline {bp}/{bp+bf}  style {sp}/{sp+sf}")


def p1_table():
    """P1 harness-variant: baseline vs published attention-control vs shipped terse (omp) vs claude variant, all no TTSR."""
    def stats(rows):
        agg = defaultdict(list)
        for r in rows:
            w, pv, pf, lp, cl, op = metrics(r["response"])
            for k, v in [("w", w), ("pv", pv), ("lp", lp)]:
                agg[k].append(v)
        return {k: statistics.mean(v) for k, v in agg.items()}
    base = stats([r for r in load("omp-dev-baseline-son.jsonl")])
    pub = stats([r for r in load("omp-dev-candidate-son.jsonl")])
    c2 = stats([json.loads(l) for l in open(RESULTS / "p1-cond2-ompterse-son.jsonl")])
    c3 = stats([json.loads(l) for l in open(RESULTS / "p1-cond3-claudeterse-son.jsonl")])
    print("\n=== P1 harness-variant (Sonnet 5, dev split, no TTSR) ===")
    print(f"{'condition':<42} {'n':>3} {'words':>6} {'passive':>7} {'longSent':>8}")
    print(f"{'cond1 baseline (no style)':<42} {48:>3} {base['w']:>6.0f} {base['pv']:>7.1f} {base['lp']*100:>7.0f}%")
    print(f"{'attention-control (published numbers)':<42} {48:>3} {pub['w']:>6.0f} {pub['pv']:>7.1f} {pub['lp']*100:>7.0f}%")
    print(f"{'cond2 omp/terse.md (shipped, no TTSR)':<42} {48:>3} {c2['w']:>6.0f} {c2['pv']:>7.1f} {c2['lp']*100:>7.0f}%")
    print(f"{'cond3 claude/terse.md (no TTSR)':<42} {48:>3} {c3['w']:>6.0f} {c3['pv']:>7.1f} {c3['lp']*100:>7.0f}%")
    print(f"\nProvenance: shipped terse ({c2['w']:.0f}w) vs published attention-control ({pub['w']:.0f}w), delta {c2['w']-pub['w']:+.0f}w")
    print(f"Placebo: omp with Enforcement ({c2['w']:.0f}w) vs claude without ({c3['w']:.0f}w), delta {c2['w']-c3['w']:+.0f}w")


def p2_table():
    """P2 held-out: dev-split vs fresh held-out prompt set, per model."""
    def stats(path):
        rows = [json.loads(l) for l in open(RESULTS / path)]
        agg = defaultdict(list)
        for r in rows:
            w, pv, pf, lp, cl, op = metrics(r["response"])
            for k, v in [("w", w), ("pv", pv), ("lp", lp)]:
                agg[k].append(v)
        return {k: statistics.mean(v) for k, v in agg.items()}
    pairs = [
        ("GLM 5.2 Fast", "omp-dev-baseline-glm300k.jsonl", "omp-dev-candidate-glm300k.jsonl", "p2-holdout-glm-baseline.jsonl", "p2-holdout-glm-candidate.jsonl"),
        ("Sonnet 5", "omp-dev-baseline-son.jsonl", "omp-dev-candidate-son.jsonl", "p2-holdout-son-baseline.jsonl", "p2-holdout-son-candidate.jsonl"),
        ("GPT-5.6-terra", "omp-dev-baseline-gpt.jsonl", "omp-dev-candidate-gpt.jsonl", "p2-holdout-gpt-baseline.jsonl", "p2-holdout-gpt-candidate.jsonl"),
    ]
    print("\n=== P2 held-out vs dev split (attention-control candidate) ===")
    print(f"{'model':<14} {'split':<8} {'base_w':>7} {'cand_w':>7} {'dw%':>6} {'base_pv':>7} {'cand_pv':>7} {'base_ls':>7} {'cand_ls':>7}")
    for label, db, dc, hb, hc in pairs:
        b_dev, c_dev = stats(db), stats(dc)
        b_ho, c_ho = stats(hb), stats(hc)
        dw_dev = (c_dev["w"] / b_dev["w"] - 1) * 100
        dw_ho = (c_ho["w"] / b_ho["w"] - 1) * 100
        print(f"{label:<14} {'dev':<8} {b_dev['w']:>7.0f} {c_dev['w']:>7.0f} {dw_dev:>5.0f}% {b_dev['pv']:>7.1f} {c_dev['pv']:>7.1f} {b_dev['lp']*100:>6.0f}% {c_dev['lp']*100:>6.0f}%")
        print(f"{label:<14} {'heldout':<8} {b_ho['w']:>7.0f} {c_ho['w']:>7.0f} {dw_ho:>5.0f}% {b_ho['pv']:>7.1f} {c_ho['pv']:>7.1f} {b_ho['lp']*100:>6.0f}% {c_ho['lp']*100:>6.0f}%")
        print(f"{'':<14} {'delta':<8} {'':>7} {'':>7} {dw_ho-dw_dev:>+5.0f}pp")


def p3_table():
    """P3 blind judge: baseline vs styled on independent quality dimensions."""
    dims = ["correctness", "completeness", "actionability", "calibration"]
    rows = [json.loads(l) for l in open(RESULTS / "p3-son-judgments.jsonl")]
    from collections import defaultdict
    base = defaultdict(list); cand = defaultdict(list)
    p1 = defaultdict(list); p2 = defaultdict(list)
    for r in rows:
        s = r["scores"]; order = r["order"]
        for d in dims:
            b = s["A"][d] if order == "bc" else s["B"][d]
            c = s["B"][d] if order == "bc" else s["A"][d]
            base[d].append(b); cand[d].append(c)
            key = (r["case_id"], r["trial"], d)
            (p1 if r["pass"] == 1 else p2)[key].append(c)
    print("\n=== P3 blind judge (Sonnet 5, independent dimensions, judge blind to condition) ===")
    print(f"{'dimension':<16} {'baseline':>10} {'styled':>10} {'delta':>8}")
    for d in dims:
        print(f"{d:<16} {statistics.mean(base[d]):>10.2f} {statistics.mean(cand[d]):>10.2f} {statistics.mean(cand[d])-statistics.mean(base[d]):>+8.2f}")
    agreed = tot = 0; diffs = []
    for k in set(p1) & set(p2):
        for a in p1[k]:
            for b in p2[k]:
                tot += 1; agreed += a == b; diffs.append(abs(a - b))
    if tot:
        print(f"\nInter-pass agreement: {agreed}/{tot} exact-match ({100*agreed/tot:.0f}%), mean |diff| {statistics.mean(diffs):.2f}")


if __name__ == "__main__":
    main()
    p0_table()
    p1_table()
    p2_table()
    p3_table()
