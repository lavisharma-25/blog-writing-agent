# How ChatGPT Optimizes Its Agent Loop Harness, API, and Inference

## The Agent Loop as a While Loop: Core Architecture

A production agent is, at its core, a while loop: build the prompt, call the model, execute any tool calls, append the results, and repeat until the model produces a final assistant message. OpenAI’s Codex architecture follows this pattern directly, treating each loop iteration as a chance to emit either narrative text or tool calls before the loop terminates. ([Source](https://openai.com/index/unrolling-the-codex-agent-loop)) The loop is the backbone of every agent, so optimizing it means knowing exactly where to intervene. ([Source](https://www.braintrust.dev/blog/agent-while-loop))

The three optimization layers map cleanly onto that loop:

- **Harness** — orchestration: tool selection, context construction, guardrails, and task decomposition. Levers include reducing unnecessary tool calls and compressing context.
- **API** — transport and state: how model calls are made, tool-call mechanics, conversation history, streaming, and retries. Levers include state management and latency reduction.
- **Inference** — model computation: the actual reasoning and token generation. Levers include model choice, sampling parameters, and reasoning effort. ([Source](https://blogs.oracle.com/developers/the-agent-loop-decoded-three-levels-every-agent-engineer-must-know))

The same loop can be implemented with different trade-offs. The OpenAI Agents SDK abstracts the loop behind `Runner.run` with `runSingleTurn`, handling tool dispatch, handoffs, and conversation state for you. A hand-rolled `while` loop using the Responses API gives full control over state and error handling, but forces you to manage the same mechanics yourself. The SDK wins on velocity; the manual loop wins on observability and control.

The main cost drivers are clear: token count, number of round trips, retries, and failed tool calls. Each wasted iteration multiplies latency and cost. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop))

Finally, in coding agents the real deliverable is often the code written or edited, not the final assistant message. Optimizing the loop around artifact quality, rather than chat output, is what separates a useful agent from a demo. ([Source](https://www.zenml.io/llmops-database/building-production-ready-ai-agents-openai-codex-cli-architecture-and-agent-loop-design))

## Harness Optimization: Stop Resending What the Server Already Has

The harness is the orchestration layer that owns the agent loop. In ChatGPT and Codex, it does not rebuild the full prompt on every iteration. Instead, it keeps an incremental conversation state and sends only the new turns to the model. This avoids resending what the server already has and cuts both latency and token cost. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop)) ([Source](https://openai.com/index/unrolling-the-codex-agent-loop))

A minimal Python harness loop looks like this:

```python
from openai import OpenAI

client = OpenAI()

def run_agent(tools, initial_messages, max_steps=5):
    messages = list(initial_messages)  # incremental state, not full rebuild

    for _ in range(max_steps):
        response = client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            tools=tools,
        )

        output = response.output
        messages.append({"role": "assistant", "content": output})

        tool_calls = [item for item in output if item.type == "function_call"]
        if not tool_calls:
            return messages  # stop condition: no more tool calls

        for call in tool_calls:
            result = execute_tool(call.name, call.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.call_id,
                "content": result,
            })

    return messages
```

The key is that `messages` grows by appending tool results, and the model is called again only when a tool call is present. No full prompt reconstruction is needed.

Tool outputs are the main context killer. The Level 3 agent loop design recommends offloading large outputs to external storage and passing back references, plus compacting older turns into summaries. ([Source](https://blogs.oracle.com/developers/the-agent-loop-decoded-three-levels-every-agent-engineer-must-know)) This keeps the context window small and reduces per-iteration cost.

Retries are often the largest cost driver. A deterministic validator gate between steps—schema checks, regex assertions, or simple business rules—can catch failed tool calls before the harness spends another inference pass. ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)) Cost-per-successful-task is dominated by retries, so fail fast with code, not with another model call.

Finally, expose only relevant tools. Semantic tool discovery selects a small subset of tools based on the current task, shrinking the prompt and reducing the model's decision complexity. ([Source](https://pub.towardsai.net/harness-in-ai-agents-765ff91ccaeb)) The harness should be the gatekeeper for what the model sees, not a passive relay of every available tool.

### API Optimization: Use Responses API Features to Cut Round Trips

The first decision in an agent loop is which API surface to build on. Chat Completions is stateless: every iteration resends the full conversation, tool schemas, and any server-side context. The Responses API is designed for tool calling and server-side state, so the client can avoid re-transmitting unchanged context and let the server track conversation state across turns ([Source](https://developers.openai.com/blog/openai-for-developers-2025)). For agent loops, that difference is not cosmetic—it directly reduces per-iteration payload size and round-trip overhead.

One of the most effective API-level optimizations is **predicted outputs**. When an agent edits a file, most of the output is known: the unchanged code prefix. Predicted outputs let you supply that prefix, and the model only generates the delta, skipping the expensive regeneration of known tokens. In Codex-style editing tasks, this significantly reduces latency because the API avoids re-sampling tokens the harness already knows ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop)). The same technique applies to any loop where a large portion of the response is deterministic.

Another major win is replacing synchronous HTTP calls with a **persistent WebSocket connection**. Instead of opening a connection per tool call, the agent maintains a long-lived channel and streams state across the loop lifecycle. OpenAI reports that this approach made its agents 40% faster by eliminating connection setup and per-request overhead ([Source](https://daily.dev/posts/how-chatgpt-optimizes-its-agent-loop-harness-api-and-inference-tubtaum7v)). Combined with server-side state, a persistent connection keeps the loop tight.

You still need to decide **when to own the loop**. If you need fine-grained control over tool execution, retries, and human-in-the-loop checkpoints, use the Responses API directly and implement the while loop yourself. If you want managed tool execution, tracing, and built-in evals, the Agents SDK can run the loop for you ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)). The trade-off is control versus convenience.

Finally, measure **round-trip time per iteration**. Instrument each step: request serialization, network time, time-to-first-token, and total inference time. If API overhead dominates, predicted outputs and persistent connections will help. If inference dominates, focus on model selection and prompt/harness efficiency ([Source](https://www.braintrust.dev/blog/agent-while-loop)). Without this measurement, you are optimizing the wrong layer.

## Inference Optimization: Avoid Recomputation with Caching and Batching

Inference is often the largest cost in an agent loop. ChatGPT’s production design shows that the fastest token is the one you don’t recompute. The ByteByteGo breakdown highlights three levers: prompt caching, KV cache reuse, and batching. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop))

First, implement prompt caching. Agent loops repeatedly send the same system prompt, tool definitions, and few-shot examples. Caching that stable prefix avoids reprocessing it on every iteration. In ChatGPT’s loop, this can yield zero-inference latency for a subset of calls because the model does not need to recompute the prompt representation. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop))

Second, reuse the KV cache across multi-turn turns. When the conversation prefix is unchanged, the key-value cache from the previous step can be reused instead of recomputed. This is especially effective in agent loops where each tool result appends a small delta to a long conversation. ([Source](https://openai.com/index/unrolling-the-codex-agent-loop))

Third, batch independent agent runs. If you are running multiple agents or parallel tool calls, grouping them into a single inference batch improves GPU utilization and lowers per-request cost. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop))

Fourth, route by difficulty. Simple tool calls and structured extraction can be handled by a smaller, cheaper model, while frontier models are reserved for complex reasoning and planning. This keeps average cost down without sacrificing quality on hard steps. ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop))

Finally, measure the savings. Track cache hit rate and tokens-per-step across loop iterations. These metrics tell you whether your caching and batching changes are actually reducing inference compute. ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop))

## Edge Cases and Failure Modes: Loops That Spin, Thrash, or Lie

ChatGPT’s production harness and OpenAI’s Codex agent loop are both built around a while loop that calls tools until a task is complete ([Source](https://openai.com/index/unrolling-the-codex-agent-loop)) ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop)). In practice, that loop can spin, thrash, or even lie about progress. Add safeguards before shipping.

- **Detect infinite loops by capping max iterations and adding progress checks.** A model that says “I’m making progress” is not a reliable termination signal. Self-assessment can help, but it is not sufficient; the harness must enforce hard limits and detect repeated tool calls that do not change state ([Source](https://techtalkwithsriks.medium.com/notorious-agent-loops-c4cc05b859b5)).

- **Handle tool-call failures gracefully with retry budgets and deterministic validators.** If a tool returns an error, letting the model re-plan from scratch can burn tokens and repeat the same mistake. Instead, validate tool inputs and outputs with deterministic code, and retry only within a fixed budget ([Source](https://dev.to/kuldeep_paul/best-practices-for-ensuring-ai-agent-performance-and-reliability-4ok0)).

- **Watch for context bloat from repeated tool outputs.** As the loop accumulates logs, the model can lose important state or start acting on stale data. Use compaction and offloading to summarize or move older tool outputs out of the active context before the model degrades ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop)) ([Source](https://blogs.oracle.com/developers/the-agent-loop-decoded-three-levels-every-agent-engineer-must-know)).

- **Add human-in-the-loop approval gates for destructive or high-cost tool calls.** The OpenAI Agents SDK supports this pattern, and it is a practical safeguard for actions like deleting resources or making external requests ([Source](https://github.com/openai/openai-agents-python/issues/378)).

- **Debug with traces and evals.** Capture each loop iteration, add human feedback, and preserve expected behavior in regression evals so a future prompt or model change does not silently reintroduce a failure mode ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)).

## Performance and Cost Budgeting: Measure Cost-per-Successful-Task

Track **cost-per-successful-task**, not raw cost per request. The numerator includes all retries, failed tool calls, and wasted tokens; the denominator is completed tasks that actually satisfy the user. Traces are the raw material for this calculation—without per-step logs of tool calls and token spend, most optimization effort is guesswork. ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop))

Start from the latency SLA and allocate budget before optimizing. For a 500ms SLA, use roughly:

- 100ms for retrieval and context assembly
- 300ms for inference
- 100ms for post-processing and validation

This split exposes the real bottleneck. If retrieval already takes 250ms, no prompt compression or model swap will make the loop fit the SLA.

The cheapest lever is usually **deterministic validation**, not cheaper inference. Schema checks, regexes, and rule-based precondition gates can reject invalid tool arguments before the model pays for a failed round trip. A deterministic gate costs microseconds and can eliminate an entire retry loop; a cheaper model only reduces per-call cost, and it may increase retry frequency if output quality drops. ([Source](https://blogs.oracle.com/developers/the-agent-loop-decoded-three-levels-every-agent-engineer-must-know))

Before rolling out a change, A/B test it gradually. Run a new harness or prompt variant against the current version on a small traffic slice, compare success rate, latency, and user feedback, and only then expand the rollout. ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop))

Finally, use traces and evals to build a ranked change list: group failures by root cause, estimate wasted tokens and retries per failure mode, and order fixes by projected impact on cost-per-successful-task. Give that ranked list to Codex, or a similar agent harness, and let it implement the next pass while you keep measuring. ([Source](https://openai.com/index/unrolling-the-codex-agent-loop))

## Putting It Together: A Reference Agent Loop with Optimizations

A production agent is still a while loop: the model emits a tool call, the harness executes it, and the result is appended to context ([Source](https://www.braintrust.dev/blog/agent-while-loop)). ChatGPT’s production system adds targeted optimizations at three layers instead of changing that shape ([Source](https://blog.bytebytego.com/p/how-chatgpt-optimizes-its-agent-loop)).

Start with the Responses API and a stable system prompt. Cache the prompt prefix so repeated turns do not re-process the same instructions and tool schemas ([Source](https://developers.openai.com/blog/openai-for-developers-2025)). Use predicted outputs when the model’s reply is structurally predictable—for example, when extracting a JSON tool call—to cut round-trip latency. Offload large tool outputs into the harness instead of echoing them back into history, which keeps the context window small and reduces cost. Finally, wrap each tool execution with a validator gate that rejects malformed results before they cause another model call.

| Optimization | Layer | Primary metric |
|---|---|---|
| Prompt caching | API | latency, cost |
| Predicted outputs | API/inference | latency |
| Tool output offloading | Harness/inference | cost, latency |
| Validator gate | Harness | reliability |

A naive loop appends every raw command and output, re-prompting the same context on every iteration. It also spends extra turns recovering from schema-invalid or partially failed tool calls. The optimized loop reuses cached prefixes, prevents bad tool outputs from entering context, and keeps the working set small. The result is fewer model round trips, fewer input tokens, and a lower cost per successful task because failed paths are caught before they escalate.

When you find yourself hand-writing retry budgets, session state, and approval flows, it is time to move from a hand-rolled loop to the OpenAI Agents SDK. The SDK provides durable orchestration, tracing, and human-in-the-loop hooks ([Source](https://github.com/openai/openai-agents-python/issues/378)) while still allowing you to keep API-level optimizations such as prompt caching.

Production checklist:

- **Max iterations**: hard cap prevents runaway loops.
- **Retry budget**: limit transient tool failures.
- **Human approval**: escalate irreversible actions ([Source](https://github.com/openai/openai-agents-python/issues/378)).
- **Tracing**: instrument each iteration to diagnose token and latency hotspots ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)).
- **Evals**: run offline regression tests before changing harness, API, or inference settings ([Source](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)).
