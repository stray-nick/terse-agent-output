# terse-style extension

Injects the [terse output style](../../omp/terse.md) into the system prompt. When the extension is enabled, the rules apply to every response. When disabled or uninstalled, they do not.

One file (`index.ts`), no dependencies, works in both Pi and OMP.

## Install

### Pi

From the repo root:

```bash
pi install extensions/terse-style
```

That's it — `pi install` registers the extension in `~/.pi/agent/settings.json` and enables it. To disable without uninstalling, remove the `+` prefix from the `extensions/terse-style/index.ts` entry in `~/.pi/agent/settings.json` (change it to `-`), or use `pi config` and toggle it off.

Uninstall: remove the entry from `~/.pi/agent/settings.json` and delete `~/.pi/agent/extensions/terse-style/`.

### OMP

The extension works in **interactive OMP sessions** — OMP loads extensions from `~/.omp/agent/settings.json` the same way as its built-in extensions, and the `before_agent_start` hook fires in interactive sessions.

For **scripted `omp -p` runs**, OMP refuses third-party extensions in print mode (safety gate on arbitrary code). Use the rules file install instead:

```bash
curl -L -o ~/.omp/agent/rules/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/terse.md
```

The rules file has `alwaysApply: true` and works in both interactive and print mode. The extension is the Pi delivery mechanism; the rules file is the OMP delivery mechanism for scripted use.

## Verify

```bash
# Pi — should produce a terse, result-first response
pi -p --provider fireworks --model "fireworks:accounts/fireworks/routers/glm-5p2-fast" "Tell me how to fix the typo in README.md. Do not ask me questions."

# OMP — same prompt through the anthropic profile
omp --profile anthropic -p --model claude-sonnet-5 "Tell me how to fix the typo in README.md. Do not ask me questions."
```

With the extension enabled, the response leads with the answer and has no preamble. With it disabled, the response is the model's natural (usually longer, hedging) style.

## What it does

`index.ts` hooks `before_agent_start` and appends the terse style body to the system prompt, then returns it. The style body is inlined in the file (extracted from `omp/terse.md` without its frontmatter). There is no state, no network access, no side effects beyond the prompt injection.
