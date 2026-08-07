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
    b = _case_mean_words(basep)
    c = _case_mean_words(candp)
    ks = sorted(set(b) & set(c))
    lr = [math.log(c[k] / max(b[k], 1)) for k in ks]
    m_, sd = statistics.mean(lr), statistics.stdev(lr)
    sem = sd / math.sqrt(len(ks))
    return math.exp(m_), math.exp(m_ - 1.96 * sem), math.exp(m_ + 1.96 * sem), len(ks)

V2M = ["sonnet-5", "grok-4.3", "gemini-3.1", "terra", "grok-4.5", "haiku-4-5", "opus-5", "luna", "sol"]
V2L = ["Sonnet", "Grok 4.3", "Gemini", "Terra", "Grok 4.5", "Haiku", "Opus", "Luna", "Sol"]
ratios = []
for m in V2M:
    r = v2_ratio(V2 / f"baseline-{m}.jsonl", V2 / f"candidate-{m}.jsonl")
    ratios.append((m, r))
ratios.sort(key=lambda x: x[1][0])
fig, ax = plt.subplots(figsize=(10, 4.6))
xs = range(len(ratios))
means = [r[1][0] for r in ratios]; lo = [r[1][0] - r[1][1] for r in ratios]; hi = [r[1][2] - r[1][0] for r in ratios]
ax.errorbar(xs, means, yerr=[lo, hi], fmt="o", color="#1e5ab8", capsize=4, markersize=7)
ax.axhline(1.0, color="#b0b0b0", ls="--")
for x, m in zip(xs, ratios):
    ax.text(x, means[x] + 0.05, f"{means[x]:.2f}", ha="center", fontsize=9)
ax.set_xticks(list(xs)); ax.set_xticklabels([dict(zip(V2M, V2L))[r[0]] for r in ratios])
ax.set_ylabel("styled / baseline word ratio"); ax.set_ylim(0, 1.15)
ax.set_title("v2 breadth: compression ratio on 39 fresh cases (95% CI)")
fig.tight_layout(); fig.savefig(CHARTS / "v2-breadth.png", dpi=150); plt.close(fig)

# axis curves
fig, ax = plt.subplots(figsize=(9, 4.6))
AXM = {"sonnet-5": ["low", "medium", "high"], "terra": ["low", "medium", "high"],
       "grok-4.5": ["low", "medium", "high"], "gemini-3.1": ["low", "high"]}
AXL = {"sonnet-5": "Sonnet", "terra": "Terra", "grok-4.5": "Grok 4.5", "gemini-3.1": "Gemini"}
for m, lvls in AXM.items():
    pts = []
    for lvl in lvls:
        r = v2_ratio(V2 / f"axis-{m}-{lvl}-baseline.jsonl", V2 / f"axis-{m}-{lvl}-candidate.jsonl")
        pts.append(r[0])
    ax.plot(range(1, len(lvls) + 1), pts, marker="o", label=AXL[m])
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["low", "medium", "high"])
ax.set_ylabel("styled / baseline word ratio"); ax.legend(frameon=False)
ax.set_title("v2 thinking axis: compression by thinking level")
fig.tight_layout(); fig.savefig(CHARTS / "v2-axis.png", dpi=150); plt.close(fig)

print("charts written:", sorted(p.name for p in CHARTS.iterdir() if p.suffix == ".png"))
