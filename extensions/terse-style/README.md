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

OMP loads local extensions from `~/.omp/agent/settings.json` using absolute paths (same mechanism as its built-in extensions).

```bash
# 1. Copy the extension
cp -r extensions/terse-style ~/.omp/agent/extensions/terse-style

# 2. Register the absolute path in OMP's settings
python3 - <<'EOF'
import json, os
p = os.path.expanduser("~/.omp/agent/settings.json")
d = json.load(open(p)) if os.path.exists(p) else {}
ext = d.setdefault("extensions", [])
path = os.path.expanduser("~/.omp/agent/extensions/terse-style/index.ts")
if path not in ext:
    ext.append(path)
    json.dump(d, open(p, "w"), indent=2)
print(f"registered {path}")
EOF
```

To disable without uninstalling, remove the `~/.omp/agent/extensions/terse-style/index.ts` entry from `~/.omp/agent/settings.json`. To uninstall, delete the entry and the `~/.omp/agent/extensions/terse-style/` directory.

**Note:** `omp plugin install` refuses third-party local packages (safety gate on arbitrary code). The settings.json registration above is the native mechanism OMP uses for local extensions — it is how OMP's own built-in extensions are loaded.

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
