# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- **Fireworks eval (3 more models).** DeepSeek V4 Flash, GLM 5.2, and Kimi K3 measured via `pi -p --provider fireworks` (the shopify-proxy extension routes them through the proxy's Anthropic-compatible endpoint; `omp -p` couldn't load the extension). Breadth: DeepSeek 0.41, GLM 0.69, Kimi 0.66 — the U-shape holds, open models land on both sides of it. Axis: DeepSeek 0.36/0.39/0.44, GLM 0.65/0.66/0.61. Cost: the style text is in the prompt at full input price (not cached), so all 3 Fireworks models cost more with the style — corrects the v1 economics premise.
- **Metered v2 eval (primary result).** The shipped `terse.md` on 39 fresh cases × 12 models (~$255 of a $400 budget, every run metered): word ratio 0.29–0.80, U-shaped by price tier — mid-tier workhorses ~0.50 (Sonnet 0.29), flagships resist (Opus 0.68, Sol 0.80), cheapest resist too (Luna 0.76); every CI excludes 1.0. Word compression is roughly thinking-level invariant. Task success holds on Sonnet (mechanical 20/22 → 24/24; clarifying ASKED 3/3 both — GLM leg untested). Fresh-set blind judge: quality cost on all four dimensions, largest completeness (−1.24). Raw data in `evals/results/v2/`.
- **Meter.** `run_evals.py` reads omp session-file usage and bills a researched rate card, so every prose row carries real `usage` + `cost_usd`. The first fully metered eval in the repo; spend gates run on real numbers from the first invocation.
- **Install-path fixes.** Pi installs via `~/.pi/agent/APPEND_SYSTEM.md` (the old `rules/` path was not a pi load path); OMP `~/.omp/agent/rules/` and Claude `~/.claude/output-styles/` confirmed.
- **Rule-doc cleanup.** Stripped eval evidence and backstory from the rule files — they are rules, not results. One compact attribution line kept.
- **Release v0.2.0.** First published release (v0.1.0 was a draft, so `releases/latest` download URLs previously 404'd). Assets serve the cleaned rules.
- **Housekeeping (P6).** Restored the GLM run to a clean 96 (re-ran the 2 skipped responses after the watchdog shim's stdin fix); total is now 576 of 576. Committed the three local harness patches (run_evals.py: continue-on-failure, budget cap, holdout-only guard; omp-eval.sh watchdog shim) into evals/harness/ so a third party can reproduce without manual patching. REPRODUCE.md updated. The two open quirks (over-deferral on general knowledge, TTSR hang in -p mode) remain documented limitations.
- **Tool-session compression (P5).** Reused the P0 tool-using task-run responses (no new spend). Prose compression within tool sessions holds at the same rate as text-only (−55% to −56% on both models). The text-only-vs-tools scope gap is closed.
- **Thinking-token economics (P4).** 32-response capture on Sonnet 5 (thinking=high) measuring total billed output (incl thinking) vs visible prose. Thinking is ~55–64% of total output; total-output compression (−14%) is smaller than visible-prose compression (−19%), so the published visible-prose savings overstate real total-billed savings on thinking=high models. The $13/day figure is now labeled an upper bound for thinking=high models. Cache assumption validated (cacheRead >> input). Capture harness and data in evals/.
- **Blind judge (P3).** 91 blind LLM judgments (Sonnet 5, two passes) on independent quality dimensions (correctness, completeness, actionability, calibration), no style file or condition label shown, randomized A/B order. Styled responses are slightly more correct (+0.21) and better calibrated (+0.45), but measurably less complete (−0.93). The skeptic's correctness attack fails; the real cost is completeness, which the mechanical metrics could not see. Judge prompt, raw judgments, and 78% inter-pass agreement published in evals/. Metric-circularity limitation reduced.
- **Held-out generalization (P2).** 16 fresh held-out prompts (frozen before running, `evals/cases-holdout-fresh.jsonl`), identical design, 3 models (GLM 5.2 Fast, Sonnet 5, GPT-5.6-terra), 288 responses. The effect generalizes: word reduction holds within 3–4 points of the dev split on every model (−35%/−53%/−54% vs dev −38%/−56%/−50%). Dev-split overfitting concern retired.
- **Task-success eval (P0).** 10 task types, 3 trials, 2 conditions, 2 models (Sonnet 5 + GLM 5.2 Fast), tools on, 120 task-runs. Totals within noise (baseline 57/60, style 56/60). The style improves honesty probes (verbatim-error, unfixable-premise, multi-step all 5/6→6/6) and both conditions refuse to fabricate on the planted-failure probe. One measured weakness: on genuinely ambiguous tasks the style's action bias makes it implement rather than ask (clarifying-question 3/6 vs baseline 6/6).
- **Harness-variant validation (P1).** Dev-split 16 prompts, 3 trials, Sonnet 5, no TTSR. The shipped `terse.md` (159 words) is close to but not identical to the published `attention-control.md` numbers (149). The Enforcement paragraph does nothing as pure prompt text — `claude/terse.md` (without it, 140 words) beats `omp/terse.md` (with it, 159). Pi users carry a false enforcement claim that's dead weight.
- `evals/p0_run.py` task harness and `evals/results/p0-task-success.jsonl`, `p1-cond2-ompterse-son.jsonl`, `p1-cond3-claudeterse-son.jsonl`. `score.py` regenerates all new tables.

### Changed

- `eval-results.md` is now the single data analysis: full v2 dataset (9-model breadth, thinking axis, task success, blind judge, metered costs) with v1 six-model history folded in; `eval-results-v2.md` removed. README chart is the 9-model breadth plot. Chart generator committed as `evals/make_charts.py` (matplotlib in a uv venv). v1 charts regenerated from `score.py` (previously stale: GLM 410-era numbers).
- Restructured for three harnesses. Per-harness directories: `omp/` (style + TTSR enforcement), `pi/` (style, identical to OMP), `claude/` (Claude Code variant). The canonical style is `omp/terse.md`. Each harness directory has its own install README.
- Added Claude Code support: `claude/terse.md` (Claude frontmatter, TTSR enforcement section removed) with install via `~/.claude/output-styles/` and `/output-style Terse`.
- `eval-results.md`: Setup now states the six-model run used `attention-control.md`, not the shipped `terse.md`. New task-success and harness-variant sections. Limitations rewritten: accuracy spot check closed (P0), provenance gap documented, Enforcement-paragraph placebo rejected, TTSR contribution noted as unmeasured.

## [0.1.0] — 2026-08-05

Initial release.

### Added

- `terse.md` — the output style rule (`alwaysApply: true`), forked from [attention-control](https://github.com/aaddrick/attention-control). Works on OMP and Pi.
- `no-forbidden-openers.md` — TTSR enforcement companion (OMP only). Aborts forbidden openers/closers mid-stream.
- `eval-results.md` — full evaluation across six models (574 responses) with 9 charts.
- `evals/` — raw responses, 16 case prompts, scoring script, and reproduction notes.
- Three evidence-driven fixes over attention-control: verbatim error override, no-tools deadlock guard, deference calibration.

### Eval summary

- 574 responses, six models (Opus 5, GPT-5.6-terra, Gemini-3.1-pro, Sonnet 5, GLM 5.2 Fast, Claude), four providers.
- Word count −38 to −67%. Passive voice −76 to −95%. Long sentences to 0–4%. Forbidden closers eliminated.
- No degradation observed in a small preliminary task-accuracy spot check (4 task-runs, n=1 per cell, 2 models).
- Net cost savings on every model (output tokens saved > cached input tokens added), conditional on cache hits.

### Attribution

Adapted from attention-control (MIT, aaddrick), i-have-adhd (MIT, Ayoub G.), and the asd-ste100 output style (L1nefeed, unlicensed — see `NOTICE.md` for the full attribution chain and the asd-ste100 license caveat).

[0.1.0]: https://github.com/stray-nick/terse-agent-output/releases/tag/v0.1.0
