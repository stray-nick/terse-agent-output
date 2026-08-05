# Contributing

Contributions welcome. The bar is that changes to the style are backed by eval evidence, not preference. The canonical style is `omp/terse.md` — `pi/terse.md` is an identical copy and `claude/terse.md` is the Claude Code variant. Change `omp/terse.md` and regenerate the other two.

## The one rule

**Any change to `omp/terse.md` must include eval evidence it doesn't regress.** The style is proven by measurement, not taste. If you change a rule, run the eval (see `evals/REPRODUCE.md`) on at least one model and show the metrics hold or improve. Changes that improve compression or accuracy without regressing the structural metrics are welcome. Changes that just reword are welcome only if they're clearer and don't change behavior.

## What to contribute

- **Rule improvements** — with eval evidence (see above).
- **New evidence** — run the eval on a model we haven't tested, or a held-out task-success benchmark, and share the results.
- **Accuracy testing** — the accuracy check is a small spot check. A larger held-out task-success eval is the highest-value contribution.
- **Bug reports** — especially: a prompt where the style over-defers, deadlocks, or degrades output quality.

## How to contribute

1. Open an issue first for anything beyond a typo. Describe the change and the evidence you have or will gather.
2. Fork, change, run the eval, include the before/after metrics in the PR.
3. Keep the style terse. The repo applies its own rule.

## License

By contributing, you agree your contribution is licensed under MIT. See `NOTICE.md` for the upstream attribution chain — contributions must not add content under a more restrictive license without disclosure.
