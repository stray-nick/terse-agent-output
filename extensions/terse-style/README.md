# terse-style extension

Injects the [terse output style](../../omp/terse.md) into the system prompt. When the extension is enabled, the rules apply to every response. When disabled or uninstalled, they do not.

One file (`index.ts`), no dependencies, works in both Pi and OMP.

## Install

### Pi

Install from the remote GitHub URL (no repo clone needed):

```bash
pi install "git:github.com/stray-nick/terse-agent-output/extensions/terse-style@v0.2.0"
```

Then enable it: `pi config` → terse-agent-output → terse-style → enable. Or add `+extensions/terse-style/index.ts` to `~/.pi/agent/settings.json` manually:

```bash
python3 - <<'EOF'
import json, os
p = os.path.expanduser("~/.pi/agent/settings.json")
d = json.load(open(p)) if os.path.exists(p) else {}
ext = d.setdefault("extensions", [])
entry = "+extensions/terse-style/index.ts"
if entry not in ext:
    ext.append(entry)
    json.dump(d, open(p, "w"), indent=2)
print(f"enabled {entry}")
EOF
```

With the repo cloned: `pi install extensions/terse-style` installs from the local path, then enable the same way. To disable without uninstalling, remove the `+` prefix from the entry in `~/.pi/agent/settings.json` (change it to `-`), or use `pi config` and toggle it off. To uninstall, remove the entry and delete `~/.pi/agent/extensions/terse-style/`.

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
