# terse-agent-output

An output style for agents. Result-first, verbatim errors, no preamble, no fabrication. Forked from [attention-control](https://github.com/aaddrick/attention-control) with three evidence-driven fixes. Proven across six models.

Agents write too much and hedge too often. This rule fixes both. It is a discipline, not a personality — and it is measurable. See [`eval-results.md`](eval-results.md) for the full evaluation.

![Word count: baseline vs style, six models](charts/02-word-count.png)

## Install

Two files. `terse.md` is the style. `no-forbidden-openers.md` is an optional enforcement rule.

### OMP

Copy both files to `~/.omp/agent/rules/`:

```bash
cp terse.md ~/.omp/agent/rules/terse.md
cp no-forbidden-openers.md ~/.omp/agent/rules/no-forbidden-openers.md
```

`terse.md` is `alwaysApply: true` — OMP injects it into the system prompt every turn. It survives `/compact`. `no-forbidden-openers.md` is a TTSR (Time-Traveling Stream Rules) rule that aborts forbidden openers mid-stream and forces a retry.

**TTSR caveat:** the enforcement rule works in interactive sessions. It hangs in `-p` (print) mode. Remove `no-forbidden-openers.md` if you rely on scripted `-p` runs.

### Pi

Pi has the same rule system but no TTSR. Install only the style rule:

```bash
cp terse.md ~/.pi/agent/rules/terse.md
```

`terse.md` is `alwaysApply: true` — Pi injects it every turn. Skip `no-forbidden-openers.md`: Pi cannot run stream rules. You get the full output effect; you do not get mid-stream enforcement.

## What it does

Reshapes output. Same work done. 574 responses across six models (Opus 5, GPT-5.6-terra, Gemini-3.1-pro, Sonnet 5, GLM 5.2 Fast, Claude): word count −38 to −67%, passive voice −76 to −95%, long sentences to 0–4%. No degradation in task accuracy. Net cost savings on every model — output tokens saved outweigh cached input tokens added.

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

MIT. See [`LICENSE`](LICENSE).
