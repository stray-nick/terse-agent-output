# Changelog

## [0.2.0] — 2026-08-07

First published release. Assets serve the cleaned rules via `releases/latest`.

### Added

- **12-model eval** on 39 fresh cases with real per-response metering. Compression works on every model (0.29–0.80), holds at any thinking level, doesn't hurt the work, and saves money on 6 of 12 models. Raw data in `evals/results/v2/`.
- **Fireworks models** (DeepSeek V4 Flash, GLM 5.2, Kimi K3) measured via `pi -p --provider fireworks` (shopify-proxy extension). Task-success for GLM: clarifying-question 3/3, no regression.
- **Meter** in `run_evals.py` — reads session-file usage and bills a rate card; every prose row carries real `usage` + `cost_usd`.
- **Chart generator** (`evals/make_charts.py`) — all 14 charts regenerate from current data.
- **Install-path fixes** — Pi installs via `~/.pi/agent/APPEND_SYSTEM.md` (not `rules/`); OMP and Claude paths confirmed.

### Changed

- **Rule files are rules only.** Stripped eval evidence and backstory from the style files. One compact attribution line kept.
- **Docs simplified.** `eval-results.md` is a single aggregated results doc (no history, no caveats-as-sections). README is install-focused. Both point to the rules first.
- **Repo restructured for three harnesses** — `omp/` (style + TTSR enforcement), `pi/` (style), `claude/` (Claude Code variant).

### Removed

- `eval-results-v2.md` (merged into `eval-results.md`).

### Attribution

Adapted from attention-control (MIT, aaddrick), i-have-adhd (MIT, Ayoub G.), and the asd-ste100 output style (L1nefeed, unlicensed — see `NOTICE.md` for the full attribution chain and license caveat).

[0.2.0]: https://github.com/stray-nick/terse-agent-output/releases/tag/v0.2.0
