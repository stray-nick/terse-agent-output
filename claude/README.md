# Claude Code

One file:

- `terse.md` — the terse style packaged as a Claude Code output style (Claude frontmatter: `name`, `description`, `keep-coding-instructions`). The OMP-specific TTSR enforcement section is removed; Claude Code has no stream rules.

Same shape/language rules and the same three fixes as the OMP/Pi style.

## Install

```bash
curl -L -o ~/.claude/output-styles/terse.md https://github.com/stray-nick/terse-agent-output/releases/latest/download/claude-terse.md
```

Then select it with `/output-style Terse`, or set it in your settings.
