# Reproduce the eval

The eval measures whether the output style changes agent output. It ran 16 case prompts, dev split, 3 trials each, baseline (no style) vs candidate (style injected), across six models. 574 responses total.

## What's here

- `cases.jsonl` — the 16 case prompts, one per line (`id`, `prompt`, plus harness metadata).
- `results/*.jsonl` — the raw responses, one JSON object per line: `case_id`, `trial`, `condition` (`baseline` or `candidate`), `model`, `response` (the full text), `cost_usd`, `usage`, plus provenance hashes.
- `score.py` — the scoring script. Reproduces the published metrics from the raw responses.

**Redaction.** The published responses are redacted for internal references and example tokens. Some responses reference internal systems because the eval agent explored its environment instead of answering from the message alone (contamination, mostly in the `real-ambiguity` and `unknown-flag` cases). Those system names are replaced with `<internal-...>` placeholders. Model-generated example tokens that looked real are replaced with `<example-token>` / `<example-jwt>`. Affected responses carry a `"redacted": true` field. The published metrics are computed on the redacted data and match `eval-results.md`.

## Re-score the published data

```bash
python3 evals/score.py
```

Output is the six-model baseline-vs-candidate table in `eval-results.md`. The numbers match.

## Metrics

The scoring is mechanical and rubric-aligned, computed from response text:

- **words** — `len(text.split())`. The primary concision metric.
- **passive** — regex for `is/are/was/were/be/been/being + <word>ed|en`. Passive constructions per response.
- **perfect** — regex for `have/has/had + <word>ed|en`. Perfect-tense constructions.
- **long-sent** — fraction of sentences (split on `.!?`) with >25 words. Code fences stripped first.
- **closers / openers** — regex for the forbidden phrases (`hope this helps`, `let me know if`, `great question`, etc.).

These metrics measure compliance with the style's own constraints. They do not measure independent task quality or user value. See the Limitations section in `eval-results.md`.

## Re-run the eval end to end

The eval harness is `run_evals.py` from [attention-control](https://github.com/aaddrick/attention-control) (`scripts/run_evals.py`). It runs each case prompt through a runner command and writes one JSON object per response.

### Runner command (OMP)

The runner invokes OMP in print mode with no tools:

```bash
omp --profile <profile> -p --no-tools --model <model> --thinking high \
  --append-system-prompt "You are a helpful assistant. Answer the message directly and completely. Accept the premises the message states, including any capability it grants you, and answer from the message alone. Never describe, attempt, or reference a command you would run to inspect your own environment."
```

The candidate condition appends the style body (`terse.md`) to the user prompt via the harness's `--condition-style` flag. Baseline omits it.

### Model versions and settings

| Model | Model string | Context | Thinking | Run date |
|---|---|---|---|---|
| Opus 5 | `claude-opus-5` | 1M | high | 2026-08-04 |
| GPT-5.6-terra | `gpt-5.6-terra` | 1.1M | high | 2026-08-05 |
| Gemini-3.1-pro | `gemini-3.1-pro-preview` | 1M | high | 2026-08-05 |
| Sonnet 5 | `claude-sonnet-5` | 1M | high | 2026-08-04/05 |
| GLM 5.2 Fast | `glm-5p2-fast` | 300K | default | 2026-08-04 |
| Claude (direct) | Claude CLI | 200K | high | recorded run "002" |

### Local harness patches (committed in `evals/harness/`)

The eval run used three local patches to the attention-control harness, because OMP's print mode has intermittent failure modes the upstream harness aborts on. These are environment-specific workarounds, not part of the eval logic:

1. **Watchdog shim** (`omp-eval.sh`) — wraps each `omp` invocation in a Python `subprocess.run(timeout=600, stdin=DEVNULL)`. ~10% of `-p` invocations hang indefinitely (CPU spin, no OMP or harness timeout) or block on piped-stdin EOF. The shim caps them at 600s and closes stdin. Without it, one hang aborts the run.
2. **Continue-on-failure** (`run_evals.py`) — upstream raises and aborts the whole run when one case fails all retries. Patched to `continue` past the failed case and log a `SKIP`, so one triple-hang doesn't scrap a 96-response run.
3. **Budget cap** (`run_evals.py`) — the default `--budget-usd 25` was raised to 75 to accommodate the Opus 5 run's cost.

The GLM run initially skipped 2 of 96 responses (`complex-plan` trial 2, `verbatim-error` trial 2) after triple-hang retries — before the watchdog shim's stdin fix. Both were re-run after the fix (with `--allow-provenance-drift`, since the watchdog shim had evolved). The 2 filled rows use a slightly later runner config; the rest use the original. GLM is now 96 responses, restoring the design to 576.

### Cost

Approximate OMP-reported cost for the full eval (all six models, 574 responses): ~$210. Driven mostly by Opus 5 (thinking=high, ~$84) and Gemini-3.1-pro (thinking=high, ~2h17m of compute).

## What this does not prove

This is a self-run, dev-split eval. It measures style compliance on 16 hand-written prompts. It does not measure independent task quality, user satisfaction, or performance on a held-out task-success benchmark. The accuracy check is a small preliminary spot check (4 task-runs, n=1 per cell, 2 models). Treat the results as evidence that the style is applied and shapes output, not as a rigorous benchmark.
