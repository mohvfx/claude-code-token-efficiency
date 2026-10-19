# Cache rules: what breaks the prefix and what doesn't

## The rule

The server only reuses the part that is **strictly identical from the very first token**. One differing token →
everything after it is recomputed at full price.

Practical consequence: commands that rewrite the start of the conversation (`/compact`, `/clear`) break the cache **by
construction**. That is not a bug, it is the price of a shorter context.

## Invalidation table

| Action | Cache | Why |
|---|---|---|
| `/model` | **breaks** | the cache is the model's own internal state; another model has nothing to reuse |
| `/effort` | **breaks** | effort sits in the prefix of the request — except on Fable 5.1 |
| `/compact` | **breaks** | the conversation is replaced by a summary: new prefix |
| `/clear` | **breaks** | new conversation |
| `/resume` after a pause | **breaks** | TTL expired → one full re-read |
| `/rewind` | **breaks** | truncates the prefix |
| Editing a file | intact | Claude Code side, never in the request |
| Switching permission mode | intact | outside the request |
| Editing `CLAUDE.md` | intact | read once at session start → applies from the next `/clear` |
| Adding a skill or an MCP server | intact mid-session | picked up on subsequent requests |

## TTL (time to live)

| Context | Window |
|---|---|
| Main conversation, on a plan | ~1 hour |
| Main conversation, API billing or a cloud provider | ~5 minutes |
| Subagents | 5 minutes, everywhere |

Every new request **resets the timer**. As long as you keep working without pausing, the cache stays warm.

Both windows are configurable (`promptCacheTtl` for the main conversation, an equivalent setting for subagents). But it
is not free:

- writing into the **5 minute** window costs 1.25× the input price;
- writing into the **1 hour** window costs 2×.

So if you work in short bursts with pauses of a few minutes, the short window is cheaper: you are not paying for time
you never use. The long window only pays off if you step away often (meetings, lunch, long builds) and come back to
**the same** session.

## Classic traps

**1. Switching models "to see".** The most expensive trap. A mid-session model change forces a full re-read of the
conversation with no cache. If you really must switch: `/compact` **first**, then `/model`.

**2. Compacting on return instead of before leaving.** `/compact` re-reads the whole conversation to write the summary.
While the cache is warm that read is nearly free; an hour later it is full price.

**3. Resuming an old session the next day.** `claude --resume` sends the whole conversation and none of it is cached.
Acceptable once if the context is indispensable — but better to `/compact` the night before and resume a summary.

**4. Letting one session run the whole project.** The model never removes anything. Without `/clear`, task 1 is still
present during task 3: the cost of every turn grows with nothing to flag it.

**5. Confusing "cached" with "free".** Cache reads are billed at ~0.1×, not 0×. A huge but warm context is still a
permanent cost.

## Signals to watch

- **Cache reads as a share of input**: should be by far the largest chunk. Low → a broken prefix somewhere.
- **Input per session over time**: should climb during a task and **drop back** at every `/clear`. A line that only
  climbs means an endless session.
- **Cost by model and by person**: surfaces the big model left on for everything.
