# terse-agent-output

An output style for agents. Result-first, verbatim errors, no preamble, no fabrication. Forked from [attention-control](https://github.com/aaddrick/attention-control) with three evidence-driven fixes.

![Word ratio by model, 39 fresh cases, 95% CI](charts/v2-breadth.png)

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

Reshapes output. Same work done. Measured on 12 models × 39 fresh cases:

- **Compresses output on every model.** Styled responses are 29–80% of baseline words, U-shaped by price tier — mid-tier workhorses compress hardest, flagships and the cheapest tier resist most. Works the same at any thinking level.
- **Does not hurt the work.** Pass rates match or beat baseline on tool-using tasks for both models tested; ambiguous tasks still trigger clarifying questions.
- **Saves money on 6 of 12 models.** Biggest savings on the most expensive one (Opus saves $0.127/request). Costs slightly more on short-baseline or expensive-input models where the prompt cost exceeds the output savings.
- **Costs completeness.** A blind judge sees styled responses as less complete (−1.24 on a 1–5 scale). Compression removes words; some of what was asked goes unsaid.

See [`eval-results.md`](eval-results.md) for the full numbers. Raw data and `score.py` (regenerates every table) are in [`evals/`](evals/).

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
