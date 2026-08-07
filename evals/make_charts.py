#!/usr/bin/env python3
"""Regenerate all repo charts from the corrected data.

v1 charts (charts/01..09): six-model prose + economics + task-success + trim,
numbers sourced from evals/score.py (the write-up correction source).
v2 charts (charts/v2-*): the 9-model breadth and 4-model thinking axis from
evals/results/v2/ raw data.
"""
import sys, json, math, statistics
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
CHARTS = REPO / "charts"
sys.path.insert(0, str(REPO / "evals"))
import score  # noqa: E402

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# ---------- v1 prose metrics from score.py raw data ----------
rows6 = {}
def stats_for(bf, cf):
    brows = score.load(bf)
    if cf is None:
        crows = [r for r in brows if r.get("condition") == "candidate"]
        brows = [r for r in brows if r.get("condition") == "baseline"]
    else:
        crows = score.load(cf)
    return score.mean_stats(brows)[0], score.mean_stats(crows)[0]
for label, (bf, cf) in score.MODELS.items():
    b, c = stats_for(bf, cf)
    dw = (c["w"] / b["w"] - 1) * 100
    rows6[label] = dict(base_w=b["w"], cand_w=c["w"], dw=dw,
                        base_pv=b["pv"], cand_pv=c["pv"],
                        base_ls=b["lp"] * 100, cand_ls=c["lp"] * 100,
                        base_cl=b["cl"] * 100, cand_cl=c["cl"] * 100)
ORDER = ["Opus 5", "GPT-5.6-terra", "Gemini-3.1-pro", "Sonnet 5", "GLM 5.2 Fast", "Claude (direct)"]
names = {"Opus 5": "Opus", "GPT-5.6-terra": "GPT-5.6", "Gemini-3.1-pro": "Gemini",
         "Sonnet 5": "Sonnet", "GLM 5.2 Fast": "GLM", "Claude (direct)": "Claude"}

def v1_bar(fname, title, key_b, key_c, pct=False, nd=0):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    xs = range(len(ORDER))
    bv = [rows6[m][key_b] for m in ORDER]
    cv = [rows6[m][key_c] for m in ORDER]
    w = 0.38
    ax.bar([x - w/2 for x in xs], bv, w, label="baseline", color="#b0b0b0")
    ax.bar([x + w/2 for x in xs], cv, w, label="style", color="#1e5ab8")
    fmt = lambda v: f"{v:.{nd}f}%" if pct else f"{v:.{nd}f}"
    for x, v in zip([x - w/2 for x in xs], bv): ax.text(x, v, fmt(v), ha="center", va="bottom", fontsize=8)
    for x, v in zip([x + w/2 for x in xs], cv): ax.text(x, v, fmt(v), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(xs)); ax.set_xticklabels([names[m] for m in ORDER])
    ax.set_title(title); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(CHARTS / fname, dpi=150); plt.close(fig)

v1_bar("02-word-count.png", "Word count: baseline vs style", "base_w", "cand_w")
v1_bar("03-passive-voice.png", "Passive constructions per response", "base_pv", "cand_pv", nd=1)
v1_bar("04-long-sentences.png", "Long sentences (25+ words)", "base_ls", "cand_ls", pct=True)
v1_bar("05-forbidden-closers.png", "Forbidden closers", "base_cl", "cand_cl", pct=True)

# 06 compression vs baseline verbosity
fig, ax = plt.subplots(figsize=(9, 4.2))
order6 = sorted(ORDER, key=lambda m: -rows6[m]["base_w"])
xs = range(len(order6))
ax.bar(xs, [abs(rows6[m]["dw"]) for m in order6], color="#1e5ab8")
ax.set_xticks(list(xs)); ax.set_xticklabels([names[m] for m in order6])
for x, m in zip(xs, order6):
    ax.text(x, abs(rows6[m]["dw"]), f"-{abs(rows6[m]['dw']):.0f}%", ha="center", va="bottom", fontsize=9)
ax.set_title("Compression vs baseline verbosity")
fig.tight_layout(); fig.savefig(CHARTS / "06-compression-vs-verbosity.png", dpi=150); plt.close(fig)

# 07 economics (rate card mirrored from score.p4_multi_table)
TOK = 1.3; SYS = 3900
PRICING = {"Opus 5": (75, 1.50), "GPT-5.6-terra": (30, 1.00), "Claude (direct)": (15, 0.30),
           "Sonnet 5": (15, 0.30), "Gemini-3.1-pro": (10, 0.30), "GLM 5.2 Fast": (0.60, 0.015)}
econ = []
for m in ORDER:
    out_saved = round((rows6[m]["base_w"] - rows6[m]["cand_w"]) * TOK)
    out_p, cache_p = PRICING[m]
    net = out_saved * out_p / 1e6 - SYS * cache_p / 1e6
    econ.append((m, out_saved, net))
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(range(6), [e[2] for e in econ], color="#1e5ab8")
ax.set_xticks(range(6)); ax.set_xticklabels([names[e[0]] for e in econ])
for i, e in enumerate(econ):
    ax.text(i, e[2], f"${e[2]:.4f}", ha="center", va="bottom", fontsize=8)
ax.set_title("Net $ saved per response (visible prose, cached)")
fig.tight_layout(); fig.savefig(CHARTS / "07-token-economics.png", dpi=150); plt.close(fig)

# 08 task success from p0 raw data (same source as score.p0_table)
prows = [json.loads(l) for l in open(REPO / "evals/results/p0-task-success.jsonl")]
agg = defaultdict(lambda: defaultdict(int))
for r in prows:
    agg[(r["task_id"], r["condition"])][r["grade"]] += 1
tasks = sorted({k[0] for k in agg})
tb = [agg[(t, "baseline")]["pass"] for t in tasks]
ts = [agg[(t, "style")]["pass"] for t in tasks]
fig, ax = plt.subplots(figsize=(10, 4.6))
xs = range(len(tasks)); w = 0.38
ax.bar([x - w/2 for x in xs], tb, w, label="baseline", color="#b0b0b0")
ax.bar([x + w/2 for x in xs], ts, w, label="style", color="#1e5ab8")
for x, v in zip([x - w/2 for x in xs], tb): ax.text(x, v, f"{v}/6", ha="center", va="bottom", fontsize=8)
for x, v in zip([x + w/2 for x in xs], ts): ax.text(x, v, f"{v}/6", ha="center", va="bottom", fontsize=8)
ax.set_xticks(list(xs)); ax.set_xticklabels([t.replace("-", "\n") for t in tasks], fontsize=8)
ax.set_ylim(0, 7); ax.set_title("Task success: pass counts (2 models pooled)"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(CHARTS / "08-task-accuracy.png", dpi=150); plt.close(fig)

# 09 trim from raw sonnet candidate files
full = score.mean_stats(score.load("omp-dev-candidate-son.jsonl"))[0]
trim = score.mean_stats(score.load("omp-dev-candidate-son-trim.jsonl"))[0]
fig, ax = plt.subplots(figsize=(6, 4))
metrics = [("words", full["w"], trim["w"], None), ("long-sent %", full["lp"]*100, trim["lp"]*100, None)
           # passive too small to see; words + long-sent carry the story
          ]
mnames = [m[0] for m in metrics]
vals = [[m[1], m[2]] for m in metrics]
x = range(len(metrics)); w = 0.3
ax.bar([i - w/2 for i in x], [v[0] for v in vals], w, label="full", color="#b0b0b0")
ax.bar([i + w/2 for i in x], [v[1] for v in vals], w, label="trim", color="#1e5ab8")
for i, v in enumerate(vals):
    ax.text(i - w/2, v[0], f"{v[0]:.0f}", ha="center", va="bottom")
    ax.text(i + w/2, v[1], f"{v[1]:.0f}", ha="center", va="bottom")
ax.set_xticks(list(x)); ax.set_xticklabels(mnames)
ax.set_title("Trim: full vs trimmed style"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(CHARTS / "09-trim-tradeoff.png", dpi=150); plt.close(fig)

# ---------- v2 charts ----------
V2 = REPO / "evals/results/v2"

def _case_mean_words(path):
    agg = defaultdict(list)
    for r in score.load(path):
        agg[r["case_id"]].append(len(r["response"].split()))
    return {k: statistics.mean(v) for k, v in agg.items()}

def v2_ratio(basep, candp):
    """Return (geo_ratio, lo, hi, n) plus baseline mean words for bar drawing."""
    b = _case_mean_words(basep)
    c = _case_mean_words(candp)
    ks = sorted(set(b) & set(c))
    lr = [math.log(c[k] / max(b[k], 1)) for k in ks]
    m_, sd = statistics.mean(lr), statistics.stdev(lr)
    sem = sd / math.sqrt(len(ks))
    bmean = statistics.mean(b[k] for k in ks)
    return math.exp(m_), math.exp(m_ - 1.96 * sem), math.exp(m_ + 1.96 * sem), len(ks), bmean

V2M = ["sonnet-5", "grok-4.3", "gemini-3.1", "terra", "grok-4.5", "haiku-4-5", "opus-5", "luna", "sol", "deepseek-v4", "glm-5.2", "kimi-k3"]
V2L = {"sonnet-5": "Sonnet", "grok-4.3": "Grok 4.3", "gemini-3.1": "Gemini", "terra": "Terra",
       "grok-4.5": "Grok 4.5", "haiku-4-5": "Haiku", "opus-5": "Opus", "luna": "Luna", "sol": "Sol",
       "deepseek-v4": "DeepSeek", "glm-5.2": "GLM 5.2", "kimi-k3": "Kimi K3"}

# ---- v2-breadth: paired bars baseline vs style, CI whiskers on the style bar ----
breadth = []
for m in V2M:
    r = v2_ratio(V2 / f"baseline-{m}.jsonl", V2 / f"candidate-{m}.jsonl")
    breadth.append((m, *r))
breadth.sort(key=lambda x: x[1])  # by ratio ascending (strongest compression left)
fig, ax = plt.subplots(figsize=(11, 5))
xs = range(len(breadth)); w = 0.38
for i, (m, ratio, lo, hi, n, bmean) in enumerate(breadth):
    cand = bmean * ratio
    cand_lo = bmean * lo
    cand_hi = bmean * hi
    ax.bar(i - w/2, bmean, w, color="#b0b0b0", label="baseline" if i == 0 else "")
    ax.bar(i + w/2, cand, w, color="#1e5ab8", label="style" if i == 0 else "")
    # CI whisker on the style bar
    ax.errorbar(i + w/2, cand, yerr=[[cand - cand_lo], [cand_hi - cand]], fmt="none",
                ecolor="#1e5ab8", capsize=4, elinewidth=1.5)
    ax.text(i - w/2, bmean + 8, f"{bmean:.0f}", ha="center", va="bottom", fontsize=8, color="#666")
    ax.text(i + w/2, cand_hi + 12, f"{cand:.0f}", ha="center", va="bottom", fontsize=8, color="#1e5ab8")
    ax.text(i, -28, f"{ratio:.2f}", ha="center", va="top", fontsize=9, fontweight="bold")
ax.set_xticks(list(xs)); ax.set_xticklabels([V2L[b[0]] for b in breadth], fontsize=10)
ax.set_ylabel("words per response (mean)")
ax.set_ylim(-40, max(b[5] for b in breadth) * 1.25)
ax.legend(frameon=False, loc="upper left")
ax.set_title("Word count: baseline vs style (39 fresh cases)\nratio = style/baseline; whiskers = 95% CI on style")
fig.tight_layout(); fig.savefig(CHARTS / "v2-breadth.png", dpi=150); plt.close(fig)

# ---- v2-axis: small multiples, each model's levels vs its own default ----
AXM = {"sonnet-5": ["low", "medium", "high"], "terra": ["low", "medium", "high"],
       "grok-4.5": ["low", "medium", "high"], "gemini-3.1": ["low", "high"],
       "deepseek-v4": ["low", "medium", "high"], "glm-5.2": ["low", "medium", "high"]}
AXL = {"sonnet-5": "Sonnet", "terra": "Terra", "grok-4.5": "Grok 4.5", "gemini-3.1": "Gemini",
       "deepseek-v4": "DeepSeek", "glm-5.2": "GLM 5.2"}
# default ratios from the breadth data
DEFAULTS = {b[0]: b[1] for b in breadth}
fig, axes = plt.subplots(2, 3, figsize=(12, 6.5))
for ax, (m, lvls) in zip(axes.flat, AXM.items()):
    pts = []
    for lvl in lvls:
        r = v2_ratio(V2 / f"axis-{m}-{lvl}-baseline.jsonl", V2 / f"axis-{m}-{lvl}-candidate.jsonl")
        pts.append(r[0])
    xpos = range(len(lvls))
    ax.bar(xpos, pts, 0.5, color="#1e5ab8", alpha=0.7)
    ax.axhline(DEFAULTS[m], color="#e06000", ls="--", lw=1.5, label=f"default {DEFAULTS[m]:.2f}")
    for x, v in zip(xpos, pts):
        ax.text(x, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(list(xpos)); ax.set_xticklabels(lvls, fontsize=9)
    ax.set_ylim(0, max(max(pts), DEFAULTS[m]) * 1.3)
    ax.set_title(f"{AXL[m]}  (default {DEFAULTS[m]:.2f})", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
fig.suptitle("Thinking level: compression vs each model's default (dashed)", fontsize=12, y=1.01)
fig.tight_layout(); fig.savefig(CHARTS / "v2-axis.png", dpi=150, bbox_inches="tight"); plt.close(fig)

# ---- v2-judge: blind judge, paired bars per dimension + delta ----
jrows = [json.loads(l) for l in open(V2 / "judge-sonnet.jsonl")]
dims = ["correctness", "completeness", "actionability", "calibration"]
jb = [statistics.mean([r["scores"]["A"][d] if r["order"] == "bc" else r["scores"]["B"][d]
                       for r in jrows]) for d in dims]
jc = [statistics.mean([r["scores"]["B"][d] if r["order"] == "bc" else r["scores"]["A"][d]
                       for r in jrows]) for d in dims]
fig, ax = plt.subplots(figsize=(8, 4.5))
xs = range(len(dims)); w = 0.35
ax.bar([x - w/2 for x in xs], jb, w, color="#b0b0b0", label="baseline")
ax.bar([x + w/2 for x in xs], jc, w, color="#1e5ab8", label="style")
for i, d in enumerate(dims):
    delta = jc[i] - jb[i]
    ax.text(i, max(jb[i], jc[i]) + 0.12, f"{delta:+.2f}", ha="center", fontsize=10,
            color="#c02020" if delta < 0 else "#208020", fontweight="bold")
ax.set_xticks(list(xs)); ax.set_xticklabels([d.capitalize() for d in dims])
ax.set_ylim(0, 5.3); ax.set_ylabel("judge score (1-5)")
ax.legend(frameon=False, loc="upper right")
ax.set_title("Blind judge: baseline vs style (39 pairs x 2 passes)\nDelta labelled; all four negative")
fig.tight_layout(); fig.savefig(CHARTS / "v2-judge.png", dpi=150); plt.close(fig)

# ---- cost-from-usage helper: compute $ for rows with nil cost_usd (written before the pricing fix) ----
FW_PRICING = {
    "fireworks:accounts/fireworks/models/deepseek-v4-flash-0731": {"input": 0.14, "output": 0.28, "cache_read": 0.028, "cache_write": 0},
    "fireworks:accounts/fireworks/routers/glm-5p2-fast":          {"input": 2.10, "output": 6.60, "cache_read": 0.21, "cache_write": 0},
    "fireworks:accounts/fireworks/models/kimi-k3":                {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 0},
}
def cost_for_row(r):
    if r.get("cost_usd") is not None and r.get("cost_usd") > 0:
        return r["cost_usd"]
    u = r.get("usage") or {}
    rate = FW_PRICING.get(r.get("model", ""))
    if not rate or not u: return 0.0
    def t(k):
        v = u.get(k)
        return float(v) if isinstance(v, (int, float)) else 0.0
    return (t("input") * rate["input"] + t("cacheRead") * rate["cache_read"]
            + t("cacheWrite") * rate["cache_write"] + t("output") * rate["output"]) / 1e6

# ---- v2-cost-impact: per-request cost delta from applying the style ----
import json as _json
cost_impact = []
for m in V2M:
    b = [cost_for_row(r) for r in score.load(str(V2 / f"baseline-{m}.jsonl"))]
    c = [cost_for_row(r) for r in score.load(str(V2 / f"candidate-{m}.jsonl"))]
    bm, cm = statistics.mean(b), statistics.mean(c)
    cost_impact.append((m, V2L[m], bm, cm, cm - bm))
cost_impact.sort(key=lambda x: x[4])  # biggest savings at top
fig, ax = plt.subplots(figsize=(9, 5))
ys = range(len(cost_impact))
deltas = [r[4] for r in cost_impact]
colors = ["#1e5ab8" if d < 0 else "#c02020" for d in deltas]
ax.barh(ys, deltas, color=colors, height=0.6)
ax.axvline(0, color="#404040", lw=0.8)
for y, r in zip(ys, cost_impact):
    d = r[4]
    offset = 0.003 if d >= 0 else -0.003
    ha = "left" if d >= 0 else "right"
    ax.text(d + offset, y, f"${d:+.4f}", va="center", ha=ha, fontsize=9,
            color="#c02020" if d >= 0 else "#1e5ab8", fontweight="bold")
ax.set_yticks(list(ys)); ax.set_yticklabels([r[1] for r in cost_impact])
ax.set_xlim(min(deltas) * 1.35, max(deltas) * 1.35)
ax.set_xlabel("$ per request (style minus baseline; left = saves, right = costs)")
ax.set_title("Per-request cost impact of applying the style\n(39 fresh cases, default thinking, metered)")
fig.tight_layout(); fig.savefig(CHARTS / "v2-cost-impact.png", dpi=150); plt.close(fig)

print("charts written:", sorted(p.name for p in CHARTS.iterdir() if p.suffix == ".png"))
