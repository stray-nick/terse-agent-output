# Pi

One file:

- `terse.md` — the output style. Identical to `omp/terse.md`. Pi has no TTSR, so there is no enforcement companion; you get the full output effect, not mid-stream abort.

## Install

Pi appends `~/.pi/agent/APPEND_SYSTEM.md` to the system prompt every session. Install the style there. The release asset carries OMP-style YAML frontmatter, which pi would inject verbatim, so strip it:

```bash
curl -fsSL https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md \
  | awk '/^---$/{n++; next} n>=2' > ~/.pi/agent/APPEND_SYSTEM.md
```

If `~/.pi/agent/APPEND_SYSTEM.md` already has content, append the output to it instead of overwriting:

```bash
curl -fsSL https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md \
  | awk '/^---$/{n++; next} n>=2' >> ~/.pi/agent/APPEND_SYSTEM.md
```
