# OMP

Two files:

- `terse.md` — the output style (`alwaysApply: true`). OMP injects it every turn; it survives `/compact`.
- `no-forbidden-openers.md` — TTSR (Time-Traveling Stream Rules) enforcement. Aborts forbidden openers mid-stream and forces a retry. OMP only.

## Install

```bash
curl -L -o ~/.omp/agent/rules/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md
curl -L -o ~/.omp/agent/rules/no-forbidden-openers.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/no-forbidden-openers.md
```

**TTSR caveat:** the enforcement rule works in interactive sessions. It hangs in `-p` (print) mode. Remove `no-forbidden-openers.md` if you rely on scripted `-p` runs.
