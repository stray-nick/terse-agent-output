# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Changed

- Restructured for three harnesses. Per-harness directories: `omp/` (style + TTSR enforcement), `pi/` (style, identical to OMP), `claude/` (Claude Code variant). The canonical style is `omp/terse.md`. Each harness directory has its own install README.
- Added Claude Code support: `claude/terse.md` (Claude frontmatter, TTSR enforcement section removed) with install via `~/.claude/output-styles/` and `/output-style Terse`.

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
