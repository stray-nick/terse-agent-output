#!/usr/bin/env python3
"""Breadth table: per-model log-ratio, CIs, cost, for all runnable models."""
import json, math, statistics
from pathlib import Path
D = Path("/tmp/v2")
MODELS = ["deepseek-v4", "luna", "haiku-4-5", "grok-4.3", "gemini-3.1", "grok-4.5",
          "terra", "sonnet-5", "kimi-k3", "sol", "opus-5", "glm-5.2"]

def rows(name):
    p = D / name
    return [json.loads(l) for l in open(p)] if p.exists() else []

def run():
    print(f"{'model':<12} {'n':>3} {'geo':>6} {'95% CI':>12} {'trial1':>7} {'trial2':>7} {'spend':>8} {'$/resp':>7}")
    tot = 0.0
    for m in MODELS:
        b = rows(f"baseline-{m}.jsonl"); c = rows(f"candidate-{m}.jsonl")
        if not b or not c:
            print(f"{m:<12} BLOCKED/EMPTY"); continue
        bm, cm = {}, {}
        key = lambda r: (r["case_id"], r["trial"])
        # per-case pooled means
        for r in b: bm.setdefault(r["case_id"], []).append(len(r["response"].split()))
        for r in c: cm.setdefault(r["case_id"], []).append(len(r["response"].split()))
        cases = sorted(set(bm) & set(cm))
        lr = [math.log(statistics.mean(cm[k]) / max(statistics.mean(bm[k]), 1)) for k in cases]
        if len(lr) < 2:
            print(f"{m:<12} INSUFFICIENT ({len(lr)} cases)"); continue
        m_, sd = statistics.mean(lr), statistics.stdev(lr)
        sem = sd / math.sqrt(len(lr))
        lo, hi = math.exp(m_ - 1.96*sem), math.exp(m_ + 1.96*sem)
        # trial 1 vs 2 ratios (best effort)
        def tri(t):
            bb = {r["case_id"]: len(r["response"].split()) for r in b if r["trial"] == t}
            cc = {r["case_id"]: len(r["response"].split()) for r in c if r["trial"] == t}
            ks = sorted(set(bb) & set(cc))
            return f"{math.exp(statistics.mean([math.log(cc[k]/max(bb[k],1)) for k in ks])):.2f}" if ks else "-"
        t1, t2 = tri(1), tri(2)
        cost = sum(r.get("cost_usd") or 0 for r in b) + sum(r.get("cost_usd") or 0 for r in c)
        tot += cost
        n = len(b) + len(c)
        print(f"{m:<12} {n:>3} {math.exp(m_):>6.2f} {f'{lo:.2f}-{hi:.2f}':>12} {t1:>7} {t2:>7} {cost:>8.3f} {cost/n:>7.4f}")
    print(f"\nTOTAL spend breadth: ${tot:.2f}")
run()
