# Proving an Output Style Works: Attention-Control Across Six Models

An output style is a rule file that reshapes how an agent writes. We ran one across six models, 574 responses, and measured it. It works on every model. It doesn't hurt the work. It saves money.

## The style

[attention-control](https://github.com/aaddrick/attention-control) — aviation-phraseology-inspired: result-first answers, flat error reporting, no preamble, no closer. We forked it for OMP, fixed three issues found in testing, and named the fork **Runway**. Repo: `terse-agent-output`.

## The eval

16 case prompts, dev split, 3 trials each, baseline vs candidate. Six models, four providers. Harness-level prompt injection isolates the style content from delivery. Rule-file delivery verified separately via live A/B.

| Model | Provider | Context | Thinking |
|---|---|---|---|
| Opus 5 | Anthropic | 1M | high |
| GPT-5.6-terra | OpenAI | 1.1M | high |
| Gemini-3.1-pro | Google | 1M | high |
| Sonnet 5 | Anthropic | 1M | high |
| GLM 5.2 Fast | Zhipu | 300K | default |
| Claude (direct CLI) | Anthropic | 200K | high |

**Chart 1 goes here.** See annotation below.

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

**Charts 2–5 go here.** See annotations below.

## The surprise: terse models benefit most

Gemini-3.1-pro had the tersest baseline (206 words) but the biggest relative compression (−67%). The style's target isn't just brevity — it's refusing to fabricate specifics. On the uncertainty case, the baseline invented Postgres 15→17 incompatibilities without seeing the schema. The candidate refused and named the check: "Run `pg_upgrade --check` against a copy." The style moved Gemini to near-zero on every structural defect.

**Chart 6 goes here.** See annotation below.

## Token economics: the style pays for itself

The rule injects ~3,900 cached-input tokens per turn. It saves ~252 output tokens per turn. Output is 15–50× more expensive than cache-read.

| Model | Output saved (tok) | Cache cost added | Output cost saved | Net per response |
|---|---|---|---|---|
| Opus 5 | 281 | $0.00585 | $0.02110 | **saves $0.01525** |
| GPT-5.6-terra | 294 | $0.00390 | $0.00882 | **saves $0.00492** |
| Claude (direct) | 300 | $0.00117 | $0.00450 | **saves $0.00333** |
| Sonnet 5 | 250 | $0.00117 | $0.00376 | **saves $0.00259** |
| Gemini-3.1-pro | 180 | $0.00117 | $0.00180 | **saves $0.00063** |
| GLM 5.2 Fast | 204 | $0.00006 | $0.00012 | **saves $0.00006** |

At 1,000 responses/day on Opus 5: ~$13/day saved. The rule occupies 0.4–2% of the context window. It doesn't compound — same system prompt every turn.

**Chart 7 goes here.** See annotation below.

## Does it hurt the work?

Real tasks with tools, not text-only. Two models, three task types. Same work done in both conditions.

| Task | Model | With style | Without style | Work difference |
|---|---|---|---|---|
| Bug fix | Sonnet 5 | Fixed + verified | Fixed + verified | None |
| Multi-step (fn + test + run) | Sonnet 5 | All 3 steps, passed | All 3 steps, passed | None |
| Read config before answering | Sonnet 5 | Read file, answered | Read file, answered | None |
| Bug fix | GPT-5.6-terra | Fixed + verified | Fixed + verified | None |

The style changes how work is reported, not whether it gets done. The one behavioral shift: honest deference over fabricated confidence. A planted-failure probe (all tests pass, prompt claims failure) produced "Cannot reproduce the failure. All 10 tests pass" from the style-injected agent. The baseline invented a fix.

**Chart 8 goes here.** See annotation below.

## The trim: less context costs more money

We cut the examples table and framing — 3,472 → 2,793 tokens (−20%). Re-ran the eval on Sonnet 5.

| Metric | Full style | Trim style | Delta |
|---|---|---|---|
| Words | 149 | 179 | +30 (less compression) |
| Passive | 0.1 | 0.1 | same |
| Long sentences | 3% | 6% | +3pp |
| Closers | 0% | 0% | same |

The "reinforcement" tokens earn their keep. Cutting 679 cached-input tokens adds 30 output tokens. On Opus 5: saves $0.001 input, costs $0.00225 output — **net $0.00125 more expensive per turn**. The examples table produces tighter output. Output tokens are the expensive ones. Keep the full version.

**Chart 9 goes here.** See annotation below.

## How to implement it

One rule file, `~/.omp/agent/rules/runway.md`, `alwaysApply: true`. OMP injects it every turn. Survives `/compact`. Optional TTSR companion aborts forbidden openers mid-stream.

```yaml
---
description: Result-first, verbatim errors, no preamble or closer.
alwaysApply: true
---
```

Five routes tested. Sticky rule wins: composable, native reminder cadence, unlocks TTSR. System-prompt append is a dead end (consumes the slot, no enforcement). Skills are weakest (on-demand load, unreliable).

## What we'd be honest about

- Metrics are mechanical and rubric-aligned, not human-judged. LLM judging was partial and agreed with the mechanical direction.
- The style over-defers on knowledge questions occasionally — suppressing general knowledge that isn't fabrication. Calibrated in the fork.
- Error-string verbatim reproduction regressed under the original style. Fixed in the fork.
- TTSR hangs in `-p` (print) mode. Works in interactive sessions.
- Accuracy test: n=1 per cell, two models. Long multi-file refactors untested.

---

## Chart annotations (for the visualization agent)

Each annotation describes one chart. Data is final and verified. Use the exact numbers.

### Chart 1: Model matrix

**Type:** heat map or card grid.
**Purpose:** Show the six models and their specs at a glance.
**Data:** The model table above (6 rows: model, provider, context, thinking).
**Style:** One card per model. Color-code by provider (Anthropic = orange, OpenAI = green, Google = blue, Zhipu = purple). Show context size and thinking level as secondary metadata.

### Chart 2: Word count reduction (headline chart)

**Type:** Grouped horizontal bar chart.
**Purpose:** The headline result — baseline vs style word count per model.
**Data (baseline, style):**
- Opus 5: 540, 323
- GPT-5.6-terra: 451, 225
- Claude (direct): 389, 158
- Sonnet 5: 342, 149
- GLM 5.2 Fast: 410, 253
- Gemini-3.1-pro: 206, 68
**Style:** Two bars per model (baseline = gray, style = accent color). Annotate the % reduction on each style bar. Sort by baseline descending. Title: "Word count: baseline vs style, 574 responses." Y-axis: words per response. X-axis: model name.

### Chart 3: Passive voice elimination

**Type:** Grouped bar chart.
**Purpose:** Show passive-voice collapse.
**Data (baseline, style):**
- Opus 5: 2.1, 0.1
- GPT-5.6-terra: 2.3, 0.1
- Claude (direct): 2.0, 0.1
- Sonnet 5: 1.3, 0.1
- GLM 5.2 Fast: 1.7, 0.4
- Gemini-3.1-pro: 1.2, 0.0
**Style:** Baseline bars gray, style bars accent. Annotate "−76%" to "−95%" on each pair. Y-axis: passive constructions per response.

### Chart 4: Long-sentence rate

**Type:** Grouped bar chart.
**Purpose:** Show sentence-length compression.
**Data (baseline %, style %):**
- Opus 5: 16, 1
- GPT-5.6-terra: 16, 1
- Claude (direct): 29, 4
- Sonnet 5: 25, 3
- GLM 5.2 Fast: 15, 4
- Gemini-3.1-pro: 16, 0
**Style:** Y-axis: % of sentences over 25 words. Annotate the reduction (−73% to −94%).

### Chart 5: Forbidden closers elimination

**Type:** Before/after dot plot or bar chart.
**Purpose:** Show that closers existed in some baselines and were eliminated.
**Data (baseline %, style %):**
- Opus 5: 0, 0
- GPT-5.6-terra: 0, 0
- Claude (direct): 10, 0
- Sonnet 5: 2, 0
- GLM 5.2 Fast: 0, 0
- Gemini-3.1-pro: 0, 0
**Style:** Highlight the three models where closers existed (Claude 10→0, Sonnet 2→0). The others were already at 0. Title: "Forbidden closers: eliminated where they existed."

### Chart 6: Compression vs baseline verbosity

**Type:** Scatter plot.
**Purpose:** Show the counterintuitive finding — terse models compress more (relatively).
**Data (x = baseline words, y = % reduction):**
- Opus 5: 540, 40%
- GPT-5.6-terra: 451, 50%
- GLM 5.2 Fast: 410, 38%
- Claude (direct): 389, 59%
- Sonnet 5: 342, 56%
- Gemini-3.1-pro: 206, 67%
**Style:** One point per model, labeled with model name. Trend line showing negative correlation (higher baseline → lower % reduction, but note Gemini is the outlier — tersest + biggest reduction). X-axis: baseline words. Y-axis: % word reduction. Annotate Gemini as the outlier.

### Chart 7: Token economics — net savings per model

**Type:** Waterfall or diverging bar chart.
**Purpose:** Show that the style saves money on every model — cache-read cost vs output savings.
**Data per model (cache cost added, output cost saved, net):**
- Opus 5: +$0.00585, −$0.02110, net −$0.01525
- GPT-5.6-terra: +$0.00390, −$0.00882, net −$0.00492
- Claude (direct): +$0.00117, −$0.00450, net −$0.00333
- Sonnet 5: +$0.00117, −$0.00376, net −$0.00259
- Gemini-3.1-pro: +$0.00117, −$0.00180, net −$0.00063
- GLM 5.2 Fast: +$0.00006, −$0.00012, net −$0.00006
**Style:** Each model: a small red bar (cost added) and a larger green bar (cost saved), with the net as a line or annotation. All nets are negative (savings). Title: "Net cost per response: the style saves money on every model." Add a callout: "1,000 responses/day on Opus 5 = ~$13/day saved."

### Chart 8: Task accuracy — work done with and without style

**Type:** Comparison matrix or checkmark grid.
**Purpose:** Show the style doesn't degrade the work.
**Data (4 tasks × 2 conditions):**
- Bug fix / Sonnet 5: with-style ✓ fixed+verified, no-style ✓ fixed+verified, difference = none
- Multi-step / Sonnet 5: with-style ✓ all 3 steps, no-style ✓ all 3 steps, difference = none
- Read config / Sonnet 5: with-style ✓ read+answered, no-style ✓ read+answered, difference = none
- Bug fix / GPT-5.6-terra: with-style ✓ fixed+verified, no-style ✓ fixed+verified, difference = none
**Style:** Green checkmarks for completed work. Both columns all-green. "None" in the difference column. Title: "Does the style hurt the work? No — same tasks completed, same correctness."

### Chart 9: The trim tradeoff — less context, more cost

**Type:** Dual-axis or paired bar chart.
**Purpose:** The counterintuitive finding: cutting "reinforcement" tokens costs more money.
**Data:**
- Full style: 3,472 tokens injected, 149 output words, net cost −$0.00259/resp (Sonnet)
- Trim style: 2,793 tokens injected, 179 output words, net cost −$0.00234/resp (Sonnet)
**Style:** Show that tokens-down → words-up → cost-up. Left axis: tokens (injected). Right axis: output words. Annotate: "Cutting 679 cached-input tokens adds 30 output tokens. Output is 50× more expensive. The trim costs more." Title: "The trim: less context, more cost."

---

*Adapted from [`attention-control`](https://github.com/aaddrick/attention-control) by aaddrick. Shape layer from [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) by Ayoub G. (MIT). Language layer from [`asd-ste100`](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2) by L1nefeed, adapted from ASD-STE100 Issue 9. Fork: `terse-agent-output`.*
