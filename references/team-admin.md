# Team side: the admin levers

Same levers as a session, but set once for everyone, in a single file.

## Managed settings

A `settings.json` defined in the admin console (`claude.ai/admin-settings/claude-code`). Every install across the team
picks it up at startup, and **users cannot override it**.

| Setting | Effect | Leverage |
|---|---|---|
| `model` | starting model for everyone | **the strongest** |
| `availableModels` | restricts which models can be selected | prevents the priciest one being the default |
| `effortLevel` | starting effort | avoids "max by reflex" |
| `maxEffortLevel` | per-model ceiling (Enterprise) | upper bound |
| `promptCacheTtl` | team-wide cache window | match the team's actual working rhythm |
| `allowedMcpServers` | allowed servers | prevents a pile of idle servers |
| `env` | environment variables, telemetry included | observability |

Also possible: an organisation-wide `CLAUDE.md` shipped to every machine.

**The most frequent diagnosis**: a team's spend running away almost always traces back to the big model left as the
default. That is one configuration line, and the best effort-to-gain ratio available.

## Observability

- The console **analytics** view: adoption, spend report per user and per model (when usage credits are enabled).
- **OpenTelemetry**: two environment variables in the same managed settings file are enough. Every install reports
  input, output, cache reads and cache writes per person.

Three signals to read:

1. **Cache reads as a share of input, per user.** Should be by far the largest chunk. A low share means a broken
   prefix — typically a mid-session model or effort change.
2. **Input per session over time.** A line that climbs during a task and **drops back** at every `clear` is healthy. A
   line that only climbs indicates an endless session, or resumptions on an expired cache.
3. **Cost by model and per person.** Surfaces who runs the big model for everything.

Each of these maps to one habit, and each fix is a one-line message.

## Limits and caps

- On team plans, the seat's 5-hour and weekly windows are the ceiling: nobody exceeds them by accident.
- To let teams keep working past that, enable usage credits with a spend limit, per organisation, group, or person.
- **Auto-continue at usage limit**: decides whether a session that hit the window waits and then automatically picks
  the task back up. Worth considering for long unattended runs.
