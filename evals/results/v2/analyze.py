#!/usr/bin/env python3
"""Phase-1 verdict: trial stability + real $/response calibration.

Reads /tmp/v2/{baseline,candidate}-<model>.jsonl (2 trials each). Answers:
  1. Does trial 2 replicate trial 1? (log-ratio per case, both trials, per model)
  2. Between-case SD at 1 trial vs within-trial SD -> "is 1 trial enough"
  3. Real cost per response (meter), vs my model forecast
"""
import json, math, statistics, sys
from pathlib import Path

MODELS = ["deepseek-v4", "luna", "haiku-4-5", "grok-4.3"]
D = Path("/tmp/v2")

def rows(name):
    return [json.loads(l) for l in open(D / name)]

def words(r): return len(r["response"].split())

def case_map(name, trial):
    out = {}
    for r in rows(name):
        if r["trial"] == trial:
            out[r["case_id"]] = words(r)
    return out

def logratios(base, cand):
    keys = sorted(set(base) & set(cand))
    return [math.log(cand[k] / max(base[k], 1)) for k in keys]

print(f"{'model':<10} {'trial':>5} {'geo_ratio':>9} {'sd(log)':>7} {'n':>3}  | {'cost_usd':>9} {'$/resp':>7} {'$forecast':>9}")
tot_cost = 0.0
for m in MODELS:
    bf, cf = f"baseline-{m}.jsonl", f"candidate-{m}.jsonl"
    if not (D / bf).exists() or not (D / cf).exists():
        print(f"{m}: MISSING"); continue
    # trial stability
    t1 = logratios(case_map(bf, 1), case_map(cf, 1))
    t2 = logratios(case_map(bf, 2), case_map(cf, 2))
    if not t1 or not t2:
        print(f"{m:<10} no data"); continue
    g1, g2 = math.exp(statistics.mean(t1)), math.exp(statistics.mean(t2))
    s1, s2 = statistics.stdev(t1), statistics.stdev(t2)
    # pooled (both trials, per-case means)
    bm, cm = {}, {}
    for r in rows(bf): bm[r["case_id"]] = (bm.get(r["case_id"], []) + [words(r)])
    for r in rows(cf): cm[r["case_id"]] = (cm.get(r["case_id"], []) + [words(r)])
    pooled = [math.log(statistics.mean(cm[k]) / max(statistics.mean(bm[k]), 1)) for k in sorted(bm)]
    # cost
    cb = sum(r.get("cost_usd") or 0 for r in rows(bf)) + sum(r.get("cost_usd") or 0 for r in rows(cf))
    tot_cost += cb
    n_resp = len(rows(bf)) + len(rows(cf))
    print(f"{m:<10} {1:>5} {g1:>9.2f} {s1:>7.2f} {len(t1):>3}  | {cb:>9.4f} {cb/n_resp:>7.4f}")
    print(f"{'':<10} {2:>5} {g2:>9.2f} {s2:>7.2f} {len(t2):>3}  |")
    print(f"{'':<10} {'both':>5} {math.exp(statistics.mean(pooled)):>9.2f} {statistics.stdev(pooled):>7.2f} {len(pooled):>3}")
    # stability verdict
    drift = abs(g1 - g2) / min(g1, g2)
    verdict = "STABLE" if drift < 0.25 else f"DRIFT {drift:.0%}"
    print(f"{'':<10} {'':>5} trial1-vs-2 ratio: {g1:.2f} vs {g2:.2f} -> {verdict}")
print(f"\nTOTAL spend phase 1: ${tot_cost:.4f}")
