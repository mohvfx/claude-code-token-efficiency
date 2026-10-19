---
name: claude-code-token-efficiency
description: "Diagnose and reduce Claude Code token spend, and configure sessions that stay cheap without getting worse. Use whenever the user asks why Claude Code is expensive, how prompt caching works, whether to change model or effort mid-session, when to /clear vs /compact vs /resume, how to write CLAUDE.md or decide skill vs MCP vs CLI, why a session gets slower or costlier over time, how to use subagents, or how to set Claude Code up for a whole team (managed settings, telemetry, spend limits). Also use to audit a repository or a user's Claude Code setup: CLAUDE.md bloat, noisy test commands, idle MCP servers, cache-breaking habits. Trigger terms: tokens, token cost, prompt cache, cache TTL, prefix, /compact, /context, /effort, /model, subagent, CLAUDE.md, skills vs MCP, managed settings, OpenTelemetry, spend report, usage credits, Claude Code efficiency. Push this skill even when the user only says 'my bill went up' or 'this session is slow', without naming tokens."
license: MIT
compatibility: "Python 3.9+ for scripts/audit.py (standard library only). Nothing else required; the guidance applies to any Claude Code install."
metadata:
  version: "1.0"
  source: "Claude Code Workshop — 'Maximizing the value of Claude Code' (Anthropic), ~26 min"
  source_confidence: "single primary source, transcribed end-to-end"
  volatility: "pricing multipliers and cache TTLs change; verify against current docs before quoting them as fact"
---

# Claude Code — token and cache efficiency

## The core idea

> "Efficient doesn't mean fewer tokens. It means the ones you use go toward what you actually asked for."

The unit of cost is the token, and **a prompt is never a request**: every send carries the system prompt, the tool
definitions, the environment, `CLAUDE.md`, the names of skills and MCP servers, and then your message. What follows is
the tool → result → next-turn loop, where the context only ever grows.

So the goal is not to "use Claude less". It is to keep **the prefix identical, the context relevant, and the model at
the right level**.

## The 6 non-negotiables

1. **Pick model + effort + MCP servers at the start**, then leave them alone. Any change mid-session invalidates the
   prefix and re-reads the whole conversation at full price.
2. **Never reach for a bigger model by reflex.** The model multiplies *every* other cost: it is the first thing to
   check when the bill drifts.
3. **Anything that enters the conversation stays there** until `/clear`: command output, files read, logs. Filter at
   the source (`--reporter=dot`, `--quiet`) rather than hoping the model forgets.
4. **Task-specific instructions belong in a skill, not in `CLAUDE.md`.** `CLAUDE.md` is only what serves *every* task.
   A skill loads nothing but its name and description until the model actually calls it.
5. **`/compact` before you step away, not when you come back.** Compacting re-reads the whole conversation: cheap
   while the cache is warm, full price once it has expired.
6. **One session, one task.** `/clear` between tasks, or you pay for task 1 during task 3.

## Diagnostic procedure

Apply in this order. Do not jump to "you should compact more" before ruling out the model.

| Symptom | Likely cause | Action |
|---|---|---|
| Bill rising with no change in usage | big model left as default | check `model` / `availableModels`, drop one level |
| Wrong answers, concepts misunderstood | the model didn't know | go up a model |
| File skipped, test not run, task abandoned halfway | effort too low | raise `/effort` |
| Model does far more than asked (explores the whole repo) | effort too high | lower `/effort` |
| Session getting slower and pricier over time | context accumulating | `/clear` between tasks, `/compact` before pausing |
| Low cache share in `/usage` | prefix broken | stop changing model/effort mid-session |
| First message after resuming is very expensive | TTL expired | compact the night before; otherwise accept one full re-read |
| Context polluted by logs | verbose output | quiet reporter, or a subagent |

The heuristic that resolves most bad settings: **model = "it didn't know"**, **effort = "it didn't try hard enough"**.

## Auditing an existing setup

```bash
python scripts/audit.py <repo-path>          # markdown report
python scripts/audit.py <repo-path> --json   # for a pipeline
```

The script is heuristic and dependency-free: it measures `CLAUDE.md` size, counts declared MCP servers, local skills,
and flags noisy test scripts and telemetry. It does **not** score content quality.

Expected output when reporting back:

1. **3 numbers**: estimated prefix tokens, MCP server count, skill count.
2. **The 3 highest-leverage fixes**, ranked by order of magnitude, not as promises.
3. **A concrete diff** where one is possible (a `CLAUDE.md` to split, a script to quiet down).
4. **What is uncertain**: token figures are `chars / 4`, not a tokenizer.

Never present an estimate as a measurement. Say "roughly", and point at `/context` for the real number.

## What not to do

- Invent prices, TTLs, or flag names. The multipliers (0.1× / 1.25× / 2×) are stable; the prices are not.
- Recommend `/compact` in the middle of a task without a reason: that is context loss, not a free optimisation.
- Suggest switching models "to compare" mid-session: that is exactly what breaks the cache.
- Treat `CLAUDE.md` as project documentation. It is a prefix you pay for on every request.
- Propose a subagent for a trivial task: it has its own cache and its own (short-TTL) cost.

## References

Load only what the question actually needs.

- `references/mental-model.md` — how a request is built, the token types, why output costs the most.
- `references/cache-rules.md` — the prefix rule, the full invalidation table, TTLs, traps.
- `references/session-checklist.md` — before / during / after checklist, ready to paste into a `CLAUDE.md`.
- `references/team-admin.md` — managed settings, OpenTelemetry, spend limits, warning signals.
- `references/source-notes.md` — provenance, timestamps, what is dated or uncertain.
- `assets/memo-claude-code-tokens.html` — printable A4 memo (French; a `.pdf` sits alongside).

## Provenance

Derived from a ~26 minute Anthropic workshop, transcribed end to end. Single source: be careful with the numbers, the
general mechanisms hold up. Check `references/source-notes.md` before quoting any specific figure.
