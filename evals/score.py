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


if __name__ == "__main__":
    main()
