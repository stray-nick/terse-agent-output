# Eval results v2: the terse output style, 9 models + thinking axis

Second-generation eval. Ran June—August 2026 on **39 fresh hand-written cases** (`evals/cases-v2.jsonl`) — the old 16-case dev set and 16-case held-out set are both spent and published, so the whole design is new cases, frozen before running. **~$255 spent of the $400 doubled budget.** Every run_evals row carries real `usage` + `cost_usd` (session-file meter + researched rate card) — the first fully metered eval in this repo.

Raw data: `evals/results/v2/` (breadth, axis, task-depth, judge). Regenerate tables with `evals/results/v2/breadth.py` and `analyze.py`.

## Setup / what was tested

| Tier | Design | Models | Spend |
|---|---|---|---|
| Breadth | 39 fresh cases × 2 cond, default thinking | grok-4.3, haiku-4.5, luna, gemini-3.1, grok-4.5, terra, sonnet-5, opus-5, sol (9) | ~$131 |
| Thinking axis | 39 cases × 2 cond × low/med/high | sonnet-5, terra, grok-4.5 (+gemini low/high) | ~$60 |
| Task depth | 10 tool tasks × 3 trials × 2 cond | sonnet-5 (glm/deepseek blocked) | ~$20 |
| Blind judge | 39 pairs × 2 passes | sonnet-5 judging | ~$8 |
| Trial stability | 2 trials on the cheap tier | grok-4.3, haiku-4.5, luna | in breadth |

**Missing: deepseek-v4-flash-0731, glm-5.2, kimi-k3** — all Fireworks-hosted; the Fireworks API key on this machine is invalid (401, both fireworks profiles). The old GLM measurement stands as historical. Fix the key and they slot back in (~$20–30).

## Breadth: works on every model, magnitude varies 2.8×

| Model | Geo ratio | 95% CI | | Model | Geo ratio | 95% CI |
|---|---:|---:|---|---|---:|---:|
| **Sonnet 5** | **0.29** | 0.23–0.37 | | Gemini 3.1 | 0.50 | 0.37–0.67 |
| Grok 4.3 | 0.50 | 0.39–0.64 | | Terra | 0.51 | 0.43–0.60 |
| Grok 4.5 | 0.52 | 0.43–0.64 | | Haiku 4.5 | 0.52 | 0.44–0.62 |
| **Opus 5** | **0.68** | 0.51–0.90 | | **Luna** | **0.76** | 0.68–0.85 |
| **Sol** | **0.80** | 0.70–0.92 | | | | |

Every CI excludes 1.0 — *compresses output on every model tested*. But the old headline "word count drops 41–67%" is dead. The effect is **8–71%**, U-shaped: the mid-tier coding workhorses compress hardest (sonnet 0.29, grok/gemini/terra ~0.50), and the poles resist — the flagships (sol 0.80, opus 0.68) and the cheapest tier (luna 0.76). The six-model run could not see this because it never varied the price tier this way.

## Thinking axis: the interaction is level-invariant

Geo ratio by explicit `--thinking` level (1 trial per cell — see caveat):

| Model | default | low | medium | high |
|---|---:|---:|---:|---:|
| Sonnet 5 | 0.29 | 0.43 | 0.43 | 0.38 |
| Terra | 0.51 | 0.59 | 0.54 | 0.53 |
| Grok 4.5 | 0.52 | 0.57 | 0.59 | 0.54 |
| Gemini 3.1 | 0.50 | 0.44 | — | 0.39 |

No monotone effect; every explicit level sits within ~0.1 of the model's band. **Word compression does not collapse at high thinking** (P4's finding that thinking tokens compress less is about billed tokens, not words — both true). One caveat: sonnet's no-flag default (0.29) beats all its explicit levels (0.38–0.43). Either "default" is a distinct, more aggressive config, or it is between-run noise — the axis cells are 1 trial, so this gap is flagged, not explained.

## Task success: no harm; the old clarifying-regression is partially non-replicated

Sonnet, tools on, 10 tasks × 3 trials. Mechanical pass: **baseline 20/22, style 24/24**. Judged tasks (sonnet judge, 1 pass):

- **Clarifying question: baseline 3/3 ASKED, style 3/3 ASKED — no regression on sonnet.**
- Unfixable premise: 3/3 CORRECT both conditions.
- Dont-know-check: REFUSED both.

The old P0 found 6/6 → 3/6 *pooled across sonnet+glm*. Split by model, the old regression was sonnet 3/3→2/3 (1 row) plus glm 3/3→1/3 (2 rows). The new sonnet-only run shows 3/3 ASKED (0 rows) — one better than old-sonnet, n=3. **The sonnet component improved; the GLM component is untested** (Fireworks blocked). This is a partial non-replication, treated as such — the old 6/6→3/6 stays in the record.

## Blind judge: the quality cost is real and broad

Sonnet-judges-sonnet, 39 pairs × 2 passes, blind to condition, fresh prompts.

| Dimension | baseline | styled | Δ |
|---|---:|---:|---:|
| Correctness | 4.36 | 4.18 | **−0.18** |
| Completeness | 4.73 | 3.49 | **−1.24** |
| Actionability | 4.47 | 3.67 | **−0.81** |
| Calibration | 4.26 | 3.96 | **−0.29** |

Inter-pass: 76% exact-match, mean |diff| 0.29 (old P3: 78% / 0.22 — comparable reliability).

The old P3 (16 dev cases) found correctness +0.21 and calibration +0.45. The fresh set flips both negative. The honest read: **on 39 fresh prompts, the blind judge sees a quality cost on every dimension** — harsher than the old claim. Old vs new are different measurements (different sets, both sonnet-judges-sonnet); the new one is the better-powered (−1.24 completeness, wider case coverage). Both agree the dominant cost is completeness.

## Trial stability (cheap-tier experiment): confirmed

2 trials on the cheapest tier: grok-4.3 0.48/0.49, haiku-4.5 0.49/0.54 — trials agree, 1-trial breadth is valid. Luna 0.70/0.82 is the drift outlier, consistent with it being the weakest compressor.

## Cost realism

Real metered $/response (default thinking): luna $0.013, grok-4.3 $0.035, haiku $0.049, grok-4.5 $0.086, gemini/terra/sonnet ~$0.13, sol $0.35, opus $0.65. The 7.2K-token cached system prompt dominates cheap-tier cost; output price dominates premium. Total ~$255 of the $400 doubled budget, gated per phase (the meter made the gates real from the first invocation).

## Limitations (new + carried)

1. **Fireworks trio missing** — deepseek/glm/kimi absent; glm's task-depth + axis legs and the whole cheap-open-model tier are untested.
2. **Clarifying-question GLM leg untested** — partial non-replication, not general.
3. **Axis cells are 1 trial** — sonnet's default-vs-level gap is between-run noise or config difference, not separable.
4. **Fresh-set judge deltas** — new prompts, sonnet judges sonnet (self-preference risk carried), 2 passes only.
5. Blind judge is still one model judging — self-preference not controlled for.
6. Case set is hand-written; a third independent set would test generalization again (the old held-out is spent and published).
7. Task depth is sonnet-only this round; old pooled-and-judged structure not fully reproduced.

## What changed vs the v1 claim

- "41–67% on six models" → **8–71% on nine models, U-shaped by price tier**.
- "Enforcement paragraph unclear / Pi vs Claude variant" — untouched; still the shipped-file contrast, still one model.
- "Doesn't hurt the work" → holds on sonnet (mechanical + clarifying clean); GLM unresolved.
- "Blind judge: correctness better, completeness costs" → fresh set: **all four dimensions cost, completeness the largest**.
