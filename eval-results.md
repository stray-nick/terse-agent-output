# Eval results: the terse output style

The terse output style is a rule file that reshapes how an agent writes: result first, verbatim errors, no preamble, no filler, no fabrication. This document is the data analysis. Everything here is regenerable — v1 tables from `python3 evals/score.py`, v2 numbers from `evals/results/v2/` raw data (see [Reproducibility](#reproducibility)).

The rule itself is [`omp/terse.md`](omp/terse.md) (OMP/Pi) or [`claude/terse.md`](claude/terse.md) (Claude Code). It is a fork of [attention-control](https://github.com/aaddrick/attention-control) with three fixes: verbatim reproduction of quoted text, a no-tools deadlock guard, and a calibration of general knowledge vs user-specific facts.

## Design

Two evaluations, one rule family:

- **v2 (primary)** — the shipped `terse.md` injected as the candidate style on **39 fresh hand-written cases**, baseline (no style) vs styled, 2 conditions, 1–2 trials. Nine models across five providers, ~$255 of a $400 budget, every response metered (real token usage + rate-card cost). The 39 cases were written fresh because the v1 dev set and the v2 held-out set are spent and published.
- **v1 (historical)** — the upstream `attention-control.md` on the 16-case dev set, six models, 576 responses (~$210). This is what the original numbers came from; its raw data and `score.py` regenerators are preserved.

**Models not measured:** deepseek-v4-flash-0731, glm-5.2, kimi-k3 — all Fireworks-hosted; the Fireworks API key on the run machine was invalid (401). They slot back into the same harness when the key is fixed.

## 1. Word compression across models

On 39 fresh cases, styled responses are shorter on every model tested. The table is the ratio of styled to baseline words (log-ratio per case, pooled means); ratios below 1.0 mean compression.

| Model | Ratio | 95% CI | | Model | Ratio | 95% CI |
|---|---:|---:|---|---|---:|---:|
| **Sonnet 5** | **0.29** | 0.23–0.37 | | Gemini 3.1 | 0.50 | 0.37–0.67 |
| Grok 4.3 | 0.50 | 0.39–0.64 | | Terra | 0.51 | 0.43–0.60 |
| Grok 4.5 | 0.52 | 0.43–0.64 | | Haiku 4.5 | 0.52 | 0.44–0.62 |
| **Opus 5** | **0.68** | 0.51–0.90 | | **Luna** | **0.76** | 0.68–0.85 |
| **Sol** | **0.80** | 0.70–0.92 | | | | |

![Word ratio by model, 39 fresh cases, 95% CI](charts/v2-breadth.png)

Every CI excludes 1.0: the style compresses output on every model tested. The effect is **U-shaped by price tier** — compression is 20–71%, strongest on the mid-tier coding workhorses (Sonnet 0.29, Grok/Gemini/Terra ~0.50) and weakest on the flagships (Opus 0.68, Sol 0.80) and the cheapest tier (Luna 0.76). The v1 headline "word drops 41–67%" was a six-model slice of this wider spread.

**Trial stability.** The two cheapest models ran 2 trials: grok-4.3 (0.48/0.49) and haiku-4.5 (0.49/0.54) agree across trials; luna drifts more (0.70/0.82), consistent with it being the weakest compressor. One trial per case is enough for the ratio estimate; per-case variance, not trial variance, dominates.

## 2. Thinking level: roughly invariant

The same cases run with explicit `--thinking` levels show no monotone effect, and every level sits within ~0.1 of the model's default band.

| Model | default | low | medium | high |
|---|---:|---:|---:|---:|
| Sonnet 5 | 0.29 | 0.43 | 0.43 | 0.38 |
| Terra | 0.51 | 0.59 | 0.54 | 0.53 |
| Grok 4.5 | 0.52 | 0.57 | 0.59 | 0.54 |
| Gemini 3.1 | 0.50 | 0.44 | — | 0.39 |

![Word ratio by thinking level](charts/v2-axis.png)

Word compression does not collapse at high thinking (separate from P4's finding that *billed* thinking tokens compress less — both are true). One caveat: sonnet's no-flag default (0.29) beats all its explicit levels (0.38–0.43) — a distinct default config or batch noise; the axis cells are 1 trial, so this is flagged, not explained.

## 3. Task success: it does not hurt the work

Sonnet, tools on, 10 real tasks × 3 trials, graded mechanically where a script can check (tests pass, file contains the change, verbatim string present).

| Metric | Baseline | Style |
|---|---:|---:|
| Mechanical pass | 20/22 | **24/24** |
| Clarifying question (judged) | 3/3 asked before acting | **3/3 asked before acting** |
| Unfixable premise (judged) | 3/3 refused to fabricate | 3/3 refused to fabricate |

The old v1 finding — clarifying questions regressed 6/6 → 3/6 — pooled sonnet (2/3) and GLM (1/3). The v2 sonnet-only run shows 3/3 asked in both conditions, one better than v1's sonnet (2/3, n=3). The GLM leg is untested (Fireworks blocked), so this is a partial non-replication, not a general one; the old number stays in the historical record.

## 4. Blind judge: compression costs, mostly completeness

An independent judge (Sonnet 5, blind to condition, randomized A/B order) scored 39 fresh-case pairs × 2 passes on four dimensions, 1–5.

| Dimension | Baseline | Styled | Δ |
|---|---:|---:|---:|
| Correctness | 4.36 | 4.18 | −0.18 |
| Completeness | 4.73 | 3.49 | **−1.24** |
| Actionability | 4.47 | 3.67 | −0.81 |
| Calibration | 4.26 | 3.96 | −0.29 |

Inter-pass agreement: 76% exact-match, mean |diff| 0.29 (v1: 78% / 0.22). The fresh-set judge sees a quality cost on **all four** dimensions, largest on completeness. v1's dev-set judge found correctness positive (+0.21) — the two are different sets and both are sonnet-judges-sonnet; the fresh set is the better-powered measurement and is harsher.

## 5. Cost

Real metered $/response (default thinking, cached system prompt): luna $0.013, grok-4.3 $0.035, haiku $0.049, grok-4.5 $0.086, gemini/terra/sonnet ~$0.13, sol $0.35, opus $0.65. The ~7.2K-token cached system prompt dominates cheap-tier cost; output price dominates premium. The v2 campaign spent ~$255 of the $400 doubled budget, with per-phase spend gates fed by the meter.

On the v1 six-model data, net per-response savings (visible prose, cached, researched rates) were positive on every model — smallest on the cheap tiers (GLM $0.00008, Gemini $0.00063), largest on Opus ($0.01522).

## Historical v1 (six models, attention-control.md)

The original run: 16-case dev set × 3 trials × 2 conditions × 6 models = 576 responses (~$210). Word count −41 to −67%, passive −76 to −95%, long sentences to 0–4%, forbidden closers eliminated. Held-out generalization held within 3–4 points on three models. Task success (120 tool-using runs, 2 models) was within noise (57/60 vs 56/60) with honesty probes improving. Its blind judge found completeness the main cost (−0.93) with correctness +0.21. Its economics table (visible-prose basis) showed net savings on every model; P4 found thinking tokens compress less than visible prose on thinking=high models.

## Limitations

1. **Fireworks trio missing** — deepseek/glm/kimi untested; the cheap-open-model tier and GLM's task/axis legs are gaps, not results.
2. **GLM clarifying leg untested** — v2's sonnet-only non-replication is partial.
3. **Axis cells are 1 trial** — sonnet's default-vs-level gap is noise or config, not separable.
4. **Blind judge is one model judging its own family** — Sonnet scores among others Sonnet output; self-preference is not controlled for, on either the fresh set or v1.
5. **Case sets are hand-written** — v1 dev, v1 held-out, and the v2 39-case set are all spent or published; a future iteration needs a fresh set to test generalization again.
6. **Meter pricing is approximate** — researched list rates as of 2026-08; provider rates and cache behavior change.

## Reproducibility

- v1 tables: `python3 evals/score.py` regenerates every number in the historical section from `evals/results/*.jsonl`.
- v2 numbers: raw rows in `evals/results/v2/` (breadth, axis, task-depth, judge) with `breadth.py` / `analyze.py` alongside; every run_evals row carries `usage` + `cost_usd` from the session-file meter.
- Charts: `evals/make_charts.py` (a `uv` venv with matplotlib; no system matplotlib was available) regenerates `charts/`.
- End-to-end prose harness: `run_evals.py` from attention-control, patched in `evals/harness/` (watchdog shim, resume, meter); runner config `evals/runners.example.json`; fresh cases `evals/cases-v2.jsonl`.
