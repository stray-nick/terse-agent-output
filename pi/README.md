# Pi

One file:

- `terse.md` — the output style (`alwaysApply: true`). Identical to `omp/terse.md`. Pi injects it every turn; it survives `/compact`.

Pi has the same rule system as OMP but no TTSR, so there is no enforcement companion. You get the full output effect; you do not get mid-stream abort.

## Install

```bash
curl -L -o ~/.pi/agent/rules/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md
```
