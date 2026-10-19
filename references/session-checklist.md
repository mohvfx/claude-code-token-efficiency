# Session checklist

Paste as-is into a team `CLAUDE.md`, or walk through it before diagnosing a bill.

## Before — choose, then leave it alone

- [ ] **Model at the right level.** Generalist for everyday work, big model reserved for subtle bugs and unfamiliar
      territory, small model for mechanical changes and questions about code already in context.
- [ ] **`/effort` at the default.** The middle level is almost always enough; higher levels are the motivated
      exception.
- [ ] **`/context`** to see what is actually loaded (system prompt, tools, `CLAUDE.md`, skills, MCP) and drop what
      isn't needed.
- [ ] **`/mcp`** to switch off servers unused in this session. Prefer a CLI (`gh`, `aws`) where one exists: nothing is
      loaded upfront.
- [ ] **`CLAUDE.md` cleaned up**: only the universal. Anything specific goes into a skill.

## During — what you put into the conversation

- [ ] **Mention files you already know** with `@path/file.ts`: the content is injected before sending, saving a tool
      call round trip.
- [ ] **Quiet command output.** A runner printing 400 lines of passing tests pollutes every subsequent request.
      Compact reporter, `--quiet`, `-q`. Very large output is spilled to a file automatically, but anything under that
      threshold stays in the conversation.
- [ ] **The 2-3 daily commands in `CLAUDE.md`**, written exactly as they must be run.
- [ ] **Noisy digging → subagent.** Logs, an entire repo, a full test run: the subagent reads all of it in its own
      context and returns only the conclusion.
- [ ] **Don't change model or effort** mid-session. Editing files or switching permission mode is safe; `CLAUDE.md` is
      only re-read at session start anyway.

## After — keep the session focused

- [ ] **`/clear` on every new task.** The most valuable and most forgotten action.
- [ ] **`/compact` before stepping away**, while the cache is warm. `/compact` accepts hints about what to keep and
      prioritise.
- [ ] **Coming back tomorrow?** `/compact` the night before. `claude --resume` after the cache expires re-reads
      everything at full price.
- [ ] **`/rewind`** to drop the last few turns when that's enough — lighter than a compact.
- [ ] **Rename before clearing** if you plan to return: the session stays reachable through `/resume`.

## Subagents — when and how

Useful when the main task does not need the detail of the intermediate steps.

- Own context: a small system prompt, `CLAUDE.md`, and the task. The final report comes back, the rest is discarded.
- **Not free**: its own input and output tokens, its own cache with a short window. The total for one subagent job can
  be temporarily higher.
- The win is elsewhere: the main conversation stays small, so **every following turn is cheaper**, and the context
  window doesn't fill up with logs.
- It can run a different model than the session, with its own effort level.
