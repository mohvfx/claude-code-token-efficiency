# Provenance and reliability

## Source

The workshop **"Maximizing the value of Claude Code"** (Claude Code Workshop, Anthropic). A **26 min 35 s** video,
transcribed end to end to produce this skill. The talk is given by someone on the Anthropic team.

Two things to keep in mind:

1. **Single source.** This is a workshop, not documentation. The general mechanisms described are sound and internally
   consistent; none of them were cross-checked against a second source at the time of writing.
2. **The post that shared the video framed it as "an engineer running 100+ self-learning agents".** That appears
   nowhere in the video. Do not build on that framing.

## What comes from the video

| Topic | Approximate timestamp |
|---|---|
| A prompt = system prompt + tools + env + `CLAUDE.md` + skills/MCP + message | 02:23 |
| The three token types, and why output costs the most | 04:53 – 06:39 |
| The prefix and automatic caching | 06:45 |
| Model choice (generalist / expert / mechanical) | 08:04 – 08:53 |
| Context: `@files`, `/context`, `CLAUDE.md` vs skills, MCP vs CLI | 08:57 – 11:59 |
| Command output staying in the conversation | 11:59 – 13:05 |
| Effort, and the "didn't know" vs "didn't try hard enough" heuristic | 13:05 – 14:31 |
| Long sessions, `/compact`, `/rewind`, `/clear`, renaming before clearing | 14:36 – 15:53 |
| What breaks the prefix (model, effort) and what doesn't | 15:53 – 17:35 |
| TTL, 5 min / 1 h write cost, subagents at 5 min | 17:41 – 18:34 |
| The four "in practice" reflexes | 18:39 – 19:22 |
| Subagents: context, report, dedicated model and effort | 19:56 – 21:12 |
| Managed settings, telemetry, caps, auto-continue | 21:12 – 24:24 |
| The three takeaways | 24:30 – 26:09 |

## What is my own addition

Do not attribute these to the video:

- **`scripts/audit.py`**: a heuristic written for this skill. The video provides the reasoning, not an audit tool. The
  1,200 / 3,000 token thresholds for `CLAUDE.md` are my choice, not an Anthropic recommendation.
- **The diagnostic table** in `SKILL.md`: a structured restatement of the model/effort heuristic and the session
  advice, not a slide.
- **The `high` / `warn` / `info` severity levels** in the script.

## What is likely to change

- **Price multipliers** (0.1× / 1.25× / 2×) and the plan / API distinction.
- **TTLs**: ~1 h on a plan, ~5 min on API, 5 min for subagents.
- **Flag and command names**: `/effort`, `promptCacheTtl`, `allowedMcpServers`, the OpenTelemetry variables.
- **Model names** cited in the video (including the claim about a model that does not break the cache on an effort
  change).

Rule: state a **mechanism** as fact, state a **figure** as a dated estimate. Verify against the online documentation
before using any of it to arbitrate a budget.

## What this skill does not cover

- The real cost of a session: it is read from `/usage` and, for teams, from OpenTelemetry. No offline estimate
  replaces that.
- Per-model, per-token pricing.
- Anthropic's other products (API, Claude.ai, other tools) beyond what the workshop mentions in passing.
