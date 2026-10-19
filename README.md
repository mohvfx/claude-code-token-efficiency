# claude-code-token-efficiency

A Claude Code / OpenCode skill for **diagnosing and reducing token spend**, and for setting up sessions that stay
cheap without getting worse.

Distilled from the Anthropic workshop *"Maximizing the value of Claude Code"* (~26 min), turned into a procedure
rather than a summary: a diagnostic table, a non-negotiable rules list, checklists, and an audit script.

## Why

> "Efficient doesn't mean fewer tokens. It means the ones you use go toward what you actually asked for."

A prompt is never a request. Every send carries the system prompt, tool definitions, environment, `CLAUDE.md`, skill
and MCP names, and then your message. Everything after that grows the context and is re-charged on every turn.

Most expensive token behaviour is not "too much usage". It is a **broken prefix** or a **context that never gets
cleaned**.

## What's in it

```
SKILL.md                    the procedure: 6 rules, diagnostic table, guardrails
references/
  mental-model.md           how a request is built, the three token types
  cache-rules.md            the prefix rule, invalidation table, TTLs, traps
  session-checklist.md      before / during / after, subagents
  team-admin.md             managed settings, OpenTelemetry, spend caps
  source-notes.md           provenance, timestamps, what is dated or uncertain
scripts/
  audit.py                  heuristic audit of a repo's Claude Code setup
assets/
  memo-claude-code-tokens.html / .pdf    printable A4 memo
```

## Install

Claude Code:

```bash
git clone https://github.com/mohvfx/claude-code-token-efficiency ~/.claude/skills/claude-code-token-efficiency
```

OpenCode:

```bash
git clone https://github.com/mohvfx/claude-code-token-efficiency ~/.config/opencode/skills/claude-code-token-efficiency
```

Or copy the folder anywhere your agent looks for skills.

## Use the audit

```bash
python scripts/audit.py /path/to/repo            # markdown report
python scripts/audit.py /path/to/repo --json     # for a pipeline
python scripts/audit.py /path/to/repo --global   # include user-level skills
```

Standard library only, Python 3.9+. It reports:

| Measure | Value |
|---|---|
| CLAUDE.md files | 1 |
| Estimated prefix (CLAUDE.md only) | ~8394 tokens |
| MCP servers declared | 8 |
| Local skills | 1 |
| Noisy test scripts | 1 |
| Telemetry | not detected |

Then it flags oversized `CLAUDE.md` files, MCP server piles, test scripts that will echo into every later request,
and missing telemetry.

**It measures sizes, not quality.** Tokens are estimated as `characters / 4`, not counted with a tokenizer. A short
`CLAUDE.md` can still be useless; this script cannot tell. For the real numbers, read `/usage` and, on a team, the
OpenTelemetry data.

## Volatility

The mechanisms are stable. The figures — price multipliers, cache TTLs, flag names, model names — are not. They are
dated in `references/source-notes.md`, which also separates what comes from the workshop from what is my own
addition (notably `scripts/audit.py` and the 1,200 / 3,000 token thresholds, which are my choice, not an Anthropic
recommendation).

## Attribution

Derived from a public Anthropic workshop, transcribed and restructured. Not affiliated with or endorsed by Anthropic.
The source video is not redistributed here. See `NOTICE.md`.

## License

MIT — see `LICENSE`.
