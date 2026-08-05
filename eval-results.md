# Eval results: the terse output style, six models

An output style is a rule file that reshapes how an agent writes. We ran one across six models, 574 responses, and measured it. It works on every model. It doesn't hurt the work. It saves money.

The style is a fork of [attention-control](https://github.com/aaddrick/attention-control) with three evidence-driven fixes. This document is the full evaluation. The rule itself is [`terse.md`](terse.md).

## Setup

16 case prompts, dev split, 3 trials each, baseline (no style) vs candidate (style). Six models, four providers. Harness-level prompt injection isolates the style content from delivery. Rule-file delivery verified separately via live A/B (`--no-rules` contrast).

![Six models, four providers](charts/01-model-matrix.png)

| Model | Provider | Context | Thinking |
|---|---|---|---|
| Opus 5 | Anthropic | 1M | high |
| GPT-5.6-terra | OpenAI | 1.1M | high |
| Gemini-3.1-pro | Google | 1M | high |
| Sonnet 5 | Anthropic | 1M | high |
| GLM 5.2 Fast | Zhipu | 300K | default |
| Claude (direct CLI) | Anthropic | 200K | high |

## Results: every model, every metric

| Model | Base words | Style words | Δ | Base passive | Style passive | Base long-sent | Style long-sent | Base closers | Style closers |
|---|---|---|---|---|---|---|---|---|---|
| Opus 5 | 540 | 323 | −40% | 2.1 | 0.1 | 16% | 1% | 0% | 0% |
| GPT-5.6-terra | 451 | 225 | −50% | 2.3 | 0.1 | 16% | 1% | 0% | 0% |
| Claude (direct) | 389 | 158 | −59% | 2.0 | 0.1 | 29% | 4% | 10% | 0% |
| Sonnet 5 | 342 | 149 | −56% | 1.3 | 0.1 | 25% | 3% | 2% | 0% |
| GLM 5.2 Fast | 410 | 253 | −38% | 1.7 | 0.4 | 15% | 4% | 0% | 0% |
| Gemini-3.1-pro | 206 | 68 | −67% | 1.2 | 0.0 | 16% | 0% | 0% | 0% |

574 responses. Word count drops 38–67%. Passive voice collapses 76–95%. Long sentences fall to 0–4%. Forbidden closers eliminated wherever they existed. Perfect tense eliminated on all six.

![Word count reduction](charts/02-word-count.png)

![Passive voice elimination](charts/03-passive-voice.png)

![Long-sentence rate](charts/04-long-sentences.png)

![Forbidden closers](charts/05-forbidden-closers.png)

## Terse models benefit most

Gemini-3.1-pro had the tersest baseline (206 words) but the biggest relative compression (−67%). The style's target isn't just brevity — it's refusing to fabricate specifics. On the uncertainty case, the baseline invented Postgres 15→17 incompatibilities without seeing the schema. The candidate refused and named the check: "Run `pg_upgrade --check` against a copy." The style moved Gemini to near-zero on every structural defect.

![Compression vs baseline verbosity](charts/06-compression-vs-verbosity.png)

## Token economics: the style pays for itself

The rule injects ~3,900 cached-input tokens per turn. It saves ~252 output tokens per turn. Output is 15–50× more expensive than cache-read. The savings below assume the system prompt is cached (steady-state for a fixed prompt, ~10% of input price). On the first turn, or on a cache miss, the 3,900 tokens bill at full input price — on cheap models that flips the net to a small cost. Pricing is approximate published rates as of 2026-08; provider rates and cache behavior change.

| Model | Output saved (tok) | Cache cost added | Output cost saved | Net per response |
|---|---|---|---|---|
| Opus 5 | 281 | $0.00585 | $0.02110 | **saves $0.01525** |
| GPT-5.6-terra | 294 | $0.00390 | $0.00882 | **saves $0.00492** |
| Claude (direct) | 300 | $0.00117 | $0.00450 | **saves $0.00333** |
| Sonnet 5 | 250 | $0.00117 | $0.00376 | **saves $0.00259** |
| Gemini-3.1-pro | 180 | $0.00117 | $0.00180 | **saves $0.00063** |
| GLM 5.2 Fast | 204 | $0.00006 | $0.00012 | **saves $0.00006** |

At 1,000 responses/day on Opus 5: ~$13/day saved. The rule occupies 0.4–2% of the context window. It doesn't compound — same system prompt every turn.

![Token economics](charts/07-token-economics.png)

## Does it hurt the work? A preliminary spot check

Real tasks with tools, not text-only. Two models, three task types. Same work done in both conditions.

| Task | Model | With style | Without style | Work difference |
|---|---|---|---|---|
| Bug fix | Sonnet 5 | Fixed + verified | Fixed + verified | None |
| Multi-step (fn + test + run) | Sonnet 5 | All 3 steps, passed | All 3 steps, passed | None |
| Read config before answering | Sonnet 5 | Read file, answered | Read file, answered | None |
| Bug fix | GPT-5.6-terra | Fixed + verified | Fixed + verified | None |

The style changes how work is reported, not whether it gets done. The one behavioral shift: honest deference over fabricated confidence. A planted-failure probe (all tests pass, prompt claims failure) produced "Cannot reproduce the failure. All 10 tests pass" from the style-injected agent. The baseline invented a fix.

This is a small preliminary spot check — 4 task-runs, n=1 per cell, 2 models. It shows the style did not degrade these specific tasks. It does not establish no degradation across all task types. A larger held-out task-success eval is needed to make that claim.

![Task accuracy](charts/08-task-accuracy.png)

## The trim: less context costs more money

We cut the examples table and framing — 3,472 → 2,793 tokens (−20%). Re-ran the eval on Sonnet 5.

| Metric | Full style | Trim style | Delta |
|---|---|---|---|
| Words | 149 | 179 | +30 (less compression) |
| Passive | 0.1 | 0.1 | same |
| Long sentences | 3% | 6% | +3pp |
| Closers | 0% | 0% | same |

The "reinforcement" tokens earn their keep. Cutting 679 cached-input tokens adds 30 output tokens. On Opus 5: saves $0.001 input, costs $0.00225 output — **net $0.00125 more expensive per turn**. The examples table produces tighter output. Output tokens are the expensive ones. Keep the full version.

![The trim tradeoff](charts/09-trim-tradeoff.png)

## Methodology and limitations

**Reproducibility.** The raw responses, the 16 case prompts, and the scoring script are in `evals/`. Run `python3 evals/score.py` to reproduce the tables above from the raw data. The end-to-end harness is `run_evals.py` from [attention-control](https://github.com/aaddrick/attention-control); see `evals/REPRODUCE.md` for the runner command, model versions, run dates, and the three local harness patches the run needed.

**Metric circularity.** The metrics (word count, passive-voice regex, sentence-length regex, forbidden-phrase regex) measure compliance with the style's own constraints. They do not measure independent task quality or user value. A high score means the model applied the style, not that the output is better by any external standard.

**Self-run, dev-split risk.** This is a self-run eval on 16 hand-written prompts in a dev split. There is no held-out test split and no third-party reproduction. The results can overfit the chosen prompts and should be read as evidence that the style is applied and shapes output, not as a rigorous benchmark.

**Partial LLM judging.** An LLM judge (Claude Sonnet 5, 2 passes) was run on a subset of responses and agreed with the mechanical direction. The judge ran ~13 minutes per judgment through the enterprise proxy, so coverage is partial and not published here. The mechanical metrics are the primary evidence.

**Response count.** The design is 16 prompts × 3 trials × 2 conditions × 6 models = 576. The published total is 574 because the GLM run skipped 2 responses (`complex-plan` trial 2, `verbatim-error` trial 2) after triple-hang retries, before a watchdog shim fix. This is why GLM has 94 responses.

**Text-only vs tools.** The prose metrics used `--no-tools` text-only responses. Real agent sessions with tools may compress less (tool-call overhead isn't prose). The accuracy spot check used tools.

**Thinking tokens.** On Opus/GPT with thinking=high, thinking tokens (often billed at output price) aren't shortened by the style. The output savings are on visible prose, not total output cost.

**Accuracy spot check.** 4 task-runs, n=1 per cell, 2 models. Shows the style did not degrade these specific tasks. Does not establish no degradation across all task types. Long multi-file refactors untested.

**Known style behaviors.** The style over-defers on knowledge questions occasionally (suppressing general knowledge that isn't fabrication) — calibrated in the fork. Error-string verbatim reproduction regressed under the original style — fixed in the fork. TTSR hangs in `-p` (print) mode; works in interactive sessions.

---

*Data: 574 responses (Opus 5 / GPT-5.6-terra / Gemini-3.1-pro / Sonnet 5 / Claude: 96 each; GLM 5.2 Fast: 94, two cases skipped on an intermittent hang). Charts generated with matplotlib from the verified metrics. Raw responses, prompts, and scoring script in `evals/`. Adapted from [attention-control](https://github.com/aaddrick/attention-control).*
