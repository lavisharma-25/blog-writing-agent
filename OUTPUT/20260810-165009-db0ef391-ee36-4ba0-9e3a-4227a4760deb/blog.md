# How AI Agents Work and How to Build One with LangChain

## What Is an AI Agent? Core Architecture

An AI agent is not a single model call. It is a system that combines four components: a model for reasoning, tools for actions, memory for state, and an executor/orchestrator that runs the control loop ([Source](https://learn.microsoft.com/en-us/agents/architecture/components-of-agent-architecture)). The model decides what to do next; tools let it affect the outside world; memory carries context across steps; the orchestrator decides when to stop and how to sequence actions. IBM describes this as agentic architecture: a design where an AI system can take goal-directed actions rather than just generate text ([Source](https://www.ibm.com/think/topics/agentic-architecture)).

This is the key difference from a plain LLM pipeline. A standard chain sends a prompt to a model and returns one completion. An agent instead emits tool calls, observes the results, and decides the next action, repeating until the task is done. The model is still the brain, but the loop around it is what makes it an agent.

Common architecture patterns include:

- **Reactive single-agent loops:** one agent iteratively calls tools until it reaches an answer.
- **Workflow orchestration:** a central controller routes tasks to specialized agents or steps.
- **Distributed multi-agent collaboration:** multiple agents communicate and coordinate to solve a problem ([Source](https://dev.to/aws/we-need-to-talk-about-ai-agent-architectures-4n49)).

Autonomy is the main risk. To keep control, insert human-in-the-loop review at decision points: before a tool executes, after a tool returns, or before the final answer is delivered ([Source](https://www.ibm.com/think/topics/agentic-architecture)). That turns an autonomous loop into a supervised one without removing the agent's flexibility.

## Choosing the Right Stack: LangChain, LangGraph, and LangSmith

The classic `AgentExecutor` is a simple loop: the model decides, calls a tool, and repeats until it has an answer. It is easy to understand, but it hides the agent's state and makes checkpointing, human-in-the-loop interruption, and resumption awkward ([Source](https://www.aurelio.ai/learn/langchain-agent-executor), [Source](https://reference.langchain.com/python/langchain-classic/agents/agent_types/AgentType)). LangGraph replaces that loop with an explicit graph: nodes represent model calls and tool executions, edges define control flow, and a shared state object is passed between nodes. Durable state and interruption are first-class concepts, so you can pause an agent, persist its state, and resume later ([Source](https://www.langchain.com/langchain)).

That is why current LangChain docs steer new projects toward LangGraph APIs such as `create_agent` and `create_react_agent` instead of `AgentExecutor` ([Source](https://docs.langchain.com/oss/python/deepagents/rag), [Source](https://www.langchain.com/langchain)). The graph is inspectable, resumable, and testable, which matters in production.

For observability, add LangSmith. It traces every node and tool call, lets you build evaluation datasets, and runs regression tests before you change prompts, models, or tools ([Source](https://www.langchain.com/langchain)).

A practical decision rule:

- Start with `create_deep_agent` for rapid prototyping and built-in deep-agent behavior ([Source](https://docs.langchain.com/oss/python/deepagents/rag)).
- Move to `create_agent` when you need fine-grained control over tools, prompts, and model selection ([Source](https://www.langchain.com/langchain)).
- Drop down to raw LangGraph state machines when you need bespoke control flow, branching, cycles, or human-in-the-loop gates ([Source](https://www.langchain.com/langchain)).

Example project types:

- Simple Q&A: a single tool-calling loop with one or two tools.
- Multi-step research: a graph that plans, searches, reads, and synthesizes.
- RAG-guided agents: retrieval-augmented generation with agentic tool selection ([Source](https://docs.langchain.com/oss/python/deepagents/rag)).
- Multi-agent teams: multiple specialized agents coordinated by a supervisor ([Source](https://www.langchain.com/langchain)).

## The Core Agent Loop: ReAct and Tool Calling

Most LLM agents are not "smart" on their own—they run a loop. The classic ReAct pattern frames that loop as explicit steps:

- **Thought**: the model reasons about the user request and what info is missing.
- **Action**: the model selects a tool and supplies arguments.
- **Observation**: the tool executes and returns a result appended to the conversation.
- **Repeat** until the model has enough context to emit a **Final Answer**.

Here is a minimal implementation using native tool calling with LangChain v1 and `bind_tools`:

```python
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # call a weather API...
    return f"Weather in {city}: 72°F, sunny"

def get_time(city: str) -> str:
    """Get the current local time for a city."""
    return f"Time in {city}: 12:30 PM"

tools = [get_weather, get_time]

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What's the weather in Paris?"),
]

response = llm.bind_tools(tools).invoke(messages)

if response.tool_calls:
    for tc in response.tool_calls:
        # execute each tool based on the model's request
        result = globals()[tc["name"]](**tc["args"])
        messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
    response = llm.bind_tools(tools).invoke(messages)

# Once there are no tool_calls, the content is the final answer
if not response.tool_calls:
    final_answer = response.content
```

Tools are plain callable functions with a name and description. LangChain's `@tool` decorator uses the function signature and docstring to generate the JSON schema, and the model selects the right tool primarily from those descriptions.

LangGraph formalizes this loop into a `StateGraph` with two nodes: the **agent** node (which calls the model with `bind_tools`) and a **tools** node (which executes each tool call). A conditional edge routes back to the agent when `tool_calls` exist, or to `END` when the model returns a final answer. This transforms the hand-written loop above into a persistent, resumable graph.

Use ReAct-style prompting when your model does not support native function calling, such as older or open models that expect explicit "Thought/Action/Observation" text. Prefer native tool calling when available—it is lower latency, more reliable, and avoids brittle formatting.

## Implement a Minimal LangChain Agent in Python

You can build a working tool-using agent with LangChain and LangGraph in under 50 lines of Python. The current v1 approach uses LangGraph's graph primitives, not the deprecated `AgentExecutor`.

First, create a virtual environment and install the required packages:

```bash
pip install -U langchain langgraph langchain-openai python-dotenv
```

Create a `.env` file with your OpenAI API key, then load it with `python-dotenv`.

Define a simple tool. The docstring and type hints are what make it usable by the model:

```python
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Return current weather for a city."""
    return f"Weather in {city}: 72F, sunny"

llm = ChatOpenAI(model="gpt-4o-mini").bind_tools([get_weather])
```

The key step is binding the tool to the model with `.bind_tools([get_weather])`. This tells the model it can emit a tool call for `get_weather` when needed.

Next, assemble the agent graph. The agent node calls the model, and the tools node executes any requested tool calls:

```python
class AgentState(TypedDict):
    messages: list

def call_model(state):
    return {"messages": [llm.invoke(state["messages"])]}

def should_continue(state):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode([get_weather]))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, ["tools", END])
builder.add_edge("tools", "agent")

agent = builder.compile()
```

The flow is straightforward:

- `START` → `agent`: the model decides what to do.
- `agent` → `tools`: if the model emitted a tool call, execute it.
- `tools` → `agent`: always return the tool result to the model so it can produce a final answer.
- `agent` → `END`: when no more tool calls are needed.

Finally, invoke the compiled graph with a sample request:

```python
result = agent.invoke({"messages": [{"role": "user", "content": "What's the weather in Paris?"}]})
print(result["messages"][-1].content)
```

The printout should be a natural-language answer that includes the tool result, e.g., "The weather in Paris is 72F and sunny." This confirms the full loop worked: the model requested the tool, LangGraph executed it, and the model incorporated the result into its final answer.

That's the core architecture behind every LangChain agent: a model, one or more tools, and a graph loop that decides when to call them.

## Managing Memory and State Across Conversations

Agents are not stateless functions. Memory and state are core components of agent architecture: the system must preserve conversation history, user context, and intermediate decisions across calls ([Source](https://learn.microsoft.com/en-us/agents/architecture/components-of-agent-architecture)). In LangGraph, you implement this with a checkpointer and by modeling the graph state explicitly.

First, define a `State` reducer that uses `messages` as the source of truth. The `add_messages` reducer appends new messages and deduplicates by ID when nodes return them:

```python
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def chat_node(state: AgentState):
    # In a real agent, invoke the LLM, decide on tools,
    # and return the new assistant message.
    return {"messages": [{"role": "assistant", "content": "Hello!"}]}

builder = StateGraph(AgentState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

# MemorySaver is in-memory; use a RedisSaver or another persistent
# checkpoint backend for production.
graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "user-123"}}
graph.invoke(
    {"messages": [{"role": "user", "content": "My name is Ada."}]},
    config,
)
```

Compiling the graph with a checkpointer lets LangGraph store state at each step and associate it with the `thread_id` in `config` ([Source](https://www.langchain.com/langchain)). To resume a conversation, pass the same `thread_id` on the next invocation; the graph builds on the messages already in state.

Long conversations can consume too many tokens, so compress history with `trim_messages` or a summarization step:

```python
from langchain_core.messages import trim_messages

trimmer = trim_messages(
    strategy="last",
    max_tokens=2000,
    token_counter=llm.get_num_tokens_from_messages,
)
```

You can also summarize older turns into a rolling summary. Both approaches keep the `messages` state bounded while retaining useful context.

For long-term knowledge like user preferences or domain facts, do not rely on the raw message list. Persist durable facts in a vector store or key-value database and expose them as retrieval tools the agent can call when needed ([Source](https://docs.langchain.com/oss/python/langchain/tools)).

Finally, verify resumption by running a second turn with the same thread ID:

```python
graph.invoke(
    {"messages": [{"role": "user", "content": "What is my name?"}]},
    config,
)
```

If memory is wired correctly, the agent will answer from the earlier turn.

## Debugging and Observability with LangSmith

Observability is not optional when building agents. LangSmith, the observability platform in the LangChain ecosystem, provides tracing and evaluation to help you understand and improve agent behavior. ([Source](https://www.langchain.com/langchain))

First, enable tracing by setting environment variables:

```bash
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=my-agent
LANGCHAIN_API_KEY=...
```

Set these in your environment or in a `.env` file. Once tracing is on, every agent run is recorded as a trace. Open a run trace in LangSmith to inspect each model call, tool invocation, and token usage. This lets you pinpoint the exact step where an unexpected output occurs. For example, you can see whether the model chose the wrong tool, passed a malformed argument, or received an unexpected tool result. ([Source](https://docs.langchain.com/oss/python/langchain/tools))

To make traces easier to filter, add custom metadata and tags through the config parameter:

```python
agent.invoke(
    {"messages": [("user", "query")]},
    config={"metadata": {"session": "experiment-1", "prompt_version": "v2"}}
)
```

This allows you to group traces by experiment, prompt version, or any other dimension you care about. You can then compare traces across runs to see how changes affect behavior.

Next, craft a LangSmith dataset of expected tool calls and answers. Include both happy paths and edge cases. Use this dataset to run regression evals after every prompt or tool change. This catches regressions before they reach production and gives you confidence that your agent still behaves as expected. ([Source](https://www.langchain.com/langchain))

Finally, when a run fails, use the footer on the failed run to copy the raw prompt or tool output. This gives you an offline reproduction case for debugging without needing to re-run the agent. You can paste the exact inputs into a local script to iterate faster.

By combining traces, metadata, and evals, you can systematically improve agent behavior and avoid shipping broken agents.

## Edge Cases and Failure Modes in Production Agents

Production agents fail in predictable ways. Harden them before they reach users.

**Cap ReAct steps.** LangGraph's `recursion_limit` stops runaway loops. Set it in the invocation config, and wrap `llm.invoke` with a counter to enforce a separate step budget. This prevents infinite ReAct cycles and controls cost.

```python
config = {"recursion_limit": 10}
result = graph.invoke(initial_state, config)
```

**Handle parser failures.** LLM output may not match the expected tool-call schema. Use `handle_parsing_errors` in `create_react_agent` to catch exceptions and retry with a corrected prompt. Pass a function that appends the error message to the conversation so the model can self-correct.

**Validate tool arguments.** Never trust the model's arguments. Validate against a schema before execution. Use allowlists for permitted commands and deny destructive shell commands or external writes. For example, reject any tool call containing `rm`, `DROP`, or writes outside a sandbox.

**Add human approval for high-risk tools.** Use LangGraph's `interrupt` before a sensitive tool node. The graph pauses, a human reviews the pending call, and resumes with `Command(resume=...)`. This gives you a checkpoint for destructive or irreversible actions.

**Detect repeated observations.** If the agent calls the same tool with the same inputs and receives the same result, it is likely stuck. Track a hash of `(tool, inputs, observation)` in state. After N repeats, inject a prompt that forces a new strategy or ask the user for clarification.

These five guards turn a demo agent into a production system. They do not eliminate all failures, but they make failures visible, bounded, and recoverable.

## Performance, Cost, and Scaling Considerations

Agent quality doesn't require unbounded latency. You can cut token spend and keep response times low by profiling, matching model tier, caching, streaming, and revisiting architecture only when data justifies it.

- **Profile token usage.** Trace system prompts, tool schemas, and conversation history through the agent loop. Tool schemas are often the biggest hidden cost; simplify descriptions to only what the model needs for selection and argument generation. The architecture of agent components shows where these tokens are spent ([Source](https://learn.microsoft.com/en-us/agents/architecture/components-of-agent-architecture)).

- **Select model tiers by subtask.** Use fast, small models for classification, extraction, and routing. Reserve large models for tool selection and multi-step reasoning. LangChain's agent type configuration gives you this flexibility without changing your tools ([Source](https://reference.langchain.com/python/langchain-classic/agents/agent_types/AgentType)).

- **Cache deterministic outputs.** Wrap read-only tools such as database lookups with a TTL cache, and cache exact LLM completions when prompts and tool results repeat. This removes duplicate work and avoids paying for identical token sequences.

- **Stream and end early.** Send tokens to the UI as they are generated, and terminate the agent loop as soon as the final answer is clear. Every saved loop iteration reduces both cost and perceived latency.

- **Profile before adding multi-agent teams.** A multi-agent system adds orchestrator prompts, context duplication, and coordination overhead. If profiling shows a single agent is the bottleneck, one agent is the right answer. Multi-agent only pays off when measured latency or quality demands it ([Source](https://www.ibm.com/think/topics/agentic-architecture)).

Use these levers to scale usage without scaling your bill.
