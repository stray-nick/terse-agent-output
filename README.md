# terse-agent-output

An OMP-native output style. Result-first, verbatim errors, no preamble, no closer. Forked from [attention-control](https://github.com/aaddrick/attention-control) with three evidence-driven fixes.

## Install

Copy two files to `~/.omp/agent/rules/`:

```bash
cp runway.md ~/.omp/agent/rules/runway.md
cp no-forbidden-openers.md ~/.omp/agent/rules/no-forbidden-openers.md
```

`runway.md` is `alwaysApply: true` — OMP injects it every turn. `no-forbidden-openers.md` is a TTSR rule that aborts forbidden openers mid-stream.

## What it does

Reshapes output. Same work done. 574 responses across six models (Opus 5, GPT-5.6-terra, Gemini-3.1-pro, Sonnet 5, GLM 5.2 Fast, Claude). Word count −38 to −67%. Passive voice −76 to −95%. Long sentences to 0–4%. No degradation in task accuracy. Net cost savings on every model (output tokens saved > cached input tokens added).

See [`blog-post.md`](blog-post.md) for the full eval, results, and chart annotations.

## The three fixes

1. **Verbatim override** — error strings reproduced character-for-character. The original paraphrased them.
2. **No-tools deadlock guard** — the agent answers in prose when it has no tools. The original went silent.
3. **Deference calibration** — general knowledge is not fabrication. The original over-deferred.

## TTSR caveat

The TTSR rule works in interactive sessions. It hangs in `-p` (print) mode. Remove `no-forbidden-openers.md` if you rely on scripted `-p` runs.

## License

MIT. Adapted from attention-control (MIT) by aaddrick, i-have-adhd (MIT) by Ayoub G., and asd-ste100 by L1nefeed.
