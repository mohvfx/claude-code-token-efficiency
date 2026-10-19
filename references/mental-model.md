# Mental model: what a request actually is

## One prompt, one bundle

When you type `fix the failing test in utils.test.ts`, Claude Code does not send that sentence. It sends:

1. Claude's **system prompt** and the **definitions of the built-in tools** (Read, Edit, Bash, …);
2. the **environment**: working directory, git state at session start;
3. the project's **`CLAUDE.md`** (read once, at session start);
4. the **names and descriptions** of the available skills and MCP servers;
5. **then** your message.

All of it goes out as **a single request**. That is the first thing to internalise: there is never "just the prompt".

## The loop

```
request → the model replies with a tool call
        → the harness runs the tool
        → the result is sent back to the model
        → next turn, longer context
```

Nothing leaves the context during a session. Every tool result, every file read, every line of command output stays
present in **every** subsequent request, and is therefore re-charged on every turn (at cache rates, but not free).

## The three token types

| Type | What it is | Relative cost | Why |
|---|---|---|---|
| **Input** | everything you send | 1× | processed in parallel → GPUs are good at it |
| **Output** | everything the model writes: thinking, tool calls, the answer | **the most expensive** | generated one token at a time; each token is a full pass over the context |
| **Cached** | the prefix identical to the previous request | ~0.1× | the server keeps the internal state it already computed |

Output is not just the final answer: tool calls and reasoning count too. That is why effort — which drives how many
steps the model takes before concluding — has a direct and sometimes counter-intuitive effect on the bill.

## The prefix

The server can only reuse the part of the request that is **strictly identical from the very first token**. That part
is called the **prefix**. The moment a single token differs, everything after it is treated as new and recomputed at
full price.

This is the key to reading everything else: most "costly" token behaviour is really a **broken prefix**.

## The four levers

1. **Tokens in** — what is loaded, what you inject, how long the session runs.
2. **Tokens out** — effort, i.e. how far the model goes before concluding.
3. **Cache share** — keep the prefix identical and the cache warm.
4. **Model** — the per-token price multiplies the other three.

## A useful reference point

In a healthy session, most of the input should be **cache reads**. `/usage` shows the prompt cache line: if it is low,
the problem is not volume, it is a broken prefix.
