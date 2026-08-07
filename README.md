# terse-agent-output

An output style for agents. Result-first, verbatim errors, no preamble, no fabrication. Forked from [attention-control](https://github.com/aaddrick/attention-control) with three evidence-driven fixes. Proven across six models.

Agents write too much and hedge too often. This rule fixes both. It is a discipline, not a personality — and it is measurable. See [`eval-results.md`](eval-results.md) for the full evaluation, and [`evals/`](evals/) for the raw responses, prompts, and scoring script (`python3 evals/score.py` reproduces the tables).

![Word count: baseline vs style, six models](charts/02-word-count.png)

## Install

One style, three harnesses. Pick your harness:

| Harness | Style | Enforcement | Directory |
|---|---|---|---|
| **OMP** | `omp/terse.md` | `omp/no-forbidden-openers.md` (TTSR) | [`omp/`](omp/) |
| **Pi** | `pi/terse.md` | none (no stream rules) | [`pi/`](pi/) |
| **Claude Code** | `claude/terse.md` | none (no stream rules) | [`claude/`](claude/) |

OMP and Pi share the same style file. Claude Code uses a variant with Claude frontmatter and the TTSR enforcement section removed. Each harness directory has its own install README.

Quick install:

```bash
# OMP (style + enforcement)
curl -L -o ~/.omp/agent/rules/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md
curl -L -o ~/.omp/agent/rules/no-forbidden-openers.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/no-forbidden-openers.md

# Pi (style only — pi injects ~/.pi/agent/APPEND_SYSTEM.md every session)
curl -fsSL https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md \
  | awk '/^---$/{n++; next} n>=2' > ~/.pi/agent/APPEND_SYSTEM.md

# Claude Code (style only)
curl -L -o ~/.claude/output-styles/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/claude-terse.md
```

**Enforcement caveat (OMP only):** the TTSR rule works in interactive sessions but hangs in `-p` (print) mode. Remove `no-forbidden-openers.md` if you rely on scripted `-p` runs.

## What it does

Reshapes output. Same work done. Two evals, neither a spot check:

- **v2 — the shipped `terse.md`** on 39 fresh cases × 9 models (~$255, every response metered): word ratio 0.29–0.80, U-shaped — the mid-tier coding workhorses compress hardest (Sonnet 0.29, Grok/Gemini/Terra ~0.50), the flagships (Opus 0.68, Sol 0.80) and the cheapest tier (Luna 0.76) resist. Every model's CI excludes 1.0. Compression is roughly thinking-level invariant. Task success holds (Sonnet 20/22 → 24/24 mechanical; the old clarifying-question regression did not replicate on Sonnet — GLM leg untested). A fresh-set blind judge finds a quality cost on all four dimensions, largest on completeness (−1.24).
- **v1 — six models, 576 responses** (`attention-control.md`): word count −41 to −67%, passive −76 to −95%, long sentences 0–4%; held-out generalization within 3–4 points; task totals within noise (57/60 vs 56/60); blind judge's main cost was completeness (−0.93).
- **Economics**: net savings on every model, conditional on cache hits; real $/response is now metered in the v2 data ($0.013–$0.65).

See [`eval-results.md`](eval-results.md) (v1) and [`eval-results-v2.md`](eval-results-v2.md) (v2) for the full evaluations, and [`evals/`](evals/) for raw data, prompts, harnesses, and `score.py` (regenerates every v1 table). The honest limitations — including the completeness cost, the U-shaped compression, and the GLM-untested legs — are documented, not hidden.

## The three fixes over attention-control

1. **Verbatim override.** Error strings reproduced character-for-character. The original paraphrased them.
2. **No-tools deadlock guard.** The agent answers in prose when it has no tools. The original went silent.
3. **Deference calibration.** General knowledge is not fabrication. The original over-deferred on knowledge questions.

## The three sources

- [attention-control](https://github.com/aaddrick/attention-control) by aaddrick — the concept and the evaluation harness. Proven portable across six models.
- [i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub G. (MIT) — the shape layer (result-first, no preamble).
- [asd-ste100](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2) by L1nefeed, adapted from [ASD-STE100](https://www.asd-ste100.org/) Issue 9 — the language layer (active voice, simple tenses).

This fork drops the air-traffic-control framing in favor of a direct discipline, adds the three fixes, and packages the rule for OMP and Pi.

## License

MIT for the original contributions in this repo. See [`LICENSE`](LICENSE). The upstream attribution chain is in [`NOTICE.md`](NOTICE.md) — attention-control (MIT) and i-have-adhd (MIT) are clean, but the asd-ste100 language layer derives from an unlicensed gist adapting a trademarked standard, and its license status is uncertain. Read `NOTICE.md` before relying on the full chain for commercial use.
