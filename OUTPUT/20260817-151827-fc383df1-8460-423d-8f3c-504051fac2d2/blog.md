# The State of Agentic AI in 2025 Challenges, Frameworks, and What Comes Next

## Defining Agentic AI and Cutting Through the Hype

Agentic AI is not just another label for an LLM with plugins. It is a class of autonomous systems that can define a plan, call external tools and APIs, coordinate with other agents, and pursue a multi-step goal with limited human supervision. The critical difference is loop control: the system decides when it has enough information to act, when to revisit a failed step, and when to ask for help.

A useful way to separate “AI agents” from “agentic AI” comes from the conceptual taxonomy in arXiv 2505.10468. In that framing, a single-turn assistant that generates text—even with retrieval or function calling—remains a reactive tool. An agentic system operates over an extended horizon: it maintains state, iterates on incomplete information, and executes a sequence of actions before returning a final result. Conflating those levels is a common source of deployment disappointment.

The market numbers help ground the debate. Agentic AI is projected to grow from $4.35B in 2025 to $103.28B by 2034. ([Source](https://www.readytensor.ai/agentic-ai-2025)) Adoption data from SS&C Blue Prism shows a similar momentum gap: 29% of organizations have already adopted agentic AI, while 38% are actively planning to do so. ([Source](https://www.blueprism.com/the-state-of-ai-report)) However, scaling remains hard. Analyst projections from Bain and Gartner align on the bottleneck: 40% of enterprise applications will embed task-specific agents by the end of 2026, yet only about 23% of organizations are scaling agentic AI today. ([Source](https://www.bain.com/insights/state-of-the-art-of-agentic-ai-transformation-technology-report-2025)) The distance between pilot interest and production scale is the defining constraint of this cycle.

What about the hype? A chatbot that can call tools is not automatically an agentic system. Many products labeled “agents” are little more than a prompt template plus function calling. They lack planning, memory, and an autonomous loop that decides what to do next. Without those components, the system still behaves one step at a time and cannot recover from ambiguity or chain actions toward a longer-term objective. Teams evaluating agentic platforms should hold them against those criteria rather than accepting the word “agent” on the box.

## Why Most Agentic AI Pilots Stall: Data, Reliability, and Governance

Agentic AI demos are impressive; production rollouts are not. Across enterprise pilots, the blocker is rarely the underlying model. It is a stack of systemic problems: data quality, reliability, governance, and cost.

**Data quality is the first tripwire.** Sendbird’s analysis of agentic AI challenges identifies lack of clean, accessible data as a major driver of agent failure. Agents are unforgiving consumers: they take contradictory schemas, stale records, and scattered permissions at face value, then propagate those errors into tool calls and downstream actions. ([Source](https://sendbird.com/blog/agentic-ai-challenges)) A pilot that works on a curated dataset will fail the moment it touches operational data.

**Reliability failures are more varied than model accuracy.** OpenOcean’s 2025 review notes that many agent deployments get stuck because they are nondeterministic and difficult to validate. ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next)) The recurring failure modes are:

- **Hallucinated tool arguments:** the model invokes an API with invented IDs or malformed parameters.
- **Infinite loops:** the agent re-plans with no termination condition and burns tokens on repeated attempts.
- **Partial state corruption:** a multi-step transaction fails midway, leaving records half-updated.
- **Nondeterministic output:** the same input yields different action sequences, which makes regression testing nearly impossible.

IBM’s 2025 reality check reinforces this: agent behavior remains fragile outside tightly scoped demos. ([Source](https://www.ibm.com/think/insights/ai-agents-2025-expectations-vs-reality))

**Governance is built for humans, not agents.** Legacy IAM is designed around human identity: usernames, groups, session tokens, and interactive login. Agents operate service-to-service. They need machine identities, least-privilege scopes, and audit trails that can reconstruct which agent, using what permission, called which API. Most IAM systems cannot express that relationship, so teams often grant over-broad access just to keep a pilot alive. Berkeley’s research on adoption identifies governance and accountability as core organizational barriers to agentic systems. ([Source](https://cmr.berkeley.edu/2025/08/adoption-of-ai-and-agentic-systems-value-challenges-and-pathways))

**Pilot-to-production is an organizational problem before it is a technical one.** The pattern CapTech identifies—weak sponsorship and unrealistic success expectations—shows up across enterprise transformation efforts. If leaders expect agents to “just work” without workflow redesign, the pilot stalls no matter how strong the model is. ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next)) The root issue is mistaking technology readiness for organizational readiness.

**Cost is the hidden scaling limit.** Multi-step agents pay a token tax at every planning iteration, tool call, and retry. A demo may complete in one prompt; production often requires dozens. Estimate per-task LLM cost before scaling: `per_task_cost = (input_tokens × input_price + output_tokens × output_price) × expected_steps × retry_factor`. Without that estimate, a pilot can look successful and still be economically non-viable at scale. ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next))

## Core Architectural Patterns for Goal-Driven Agents

Choosing an agent architecture is less about chasing the newest framework and more about matching the pattern to the reliability and risk profile of your workflow. Most production systems in 2025 fall into one of four families ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison)):

- **Single-agent ReAct loop:** one LLM repeatedly reasons, calls a tool, observes the result, and repeats until the goal is reached. It is simple and works well for bounded tasks, but it can wander or stall when a task needs many steps ([Source](https://blog.sparrow.so/agentic-ai-the-complete-guide-to-architectures-frameworks-and-future-directions-2025)).
- **Planner-executor:** a separate planner decomposes the goal into subtasks and an executor runs them. This improves multi-step reliability, but the plan can become stale when the environment changes mid-execution ([Source](https://www.langchain.com/resources/ai-agent-frameworks)).
- **Hierarchical:** a supervisor agent delegates to nested subagents, each with a narrow mandate. It gives containment and auditability at the cost of latency and more tokens ([Source](https://akka.io/blog/agentic-ai-frameworks)).
- **Swarm/multi-agent orchestration:** multiple specialized agents coordinate through handoffs and shared state. This is flexible and scalable, but observability, security, and debugging become first-class engineering problems ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next)).

Regardless of pattern, every agent needs four core components: a **model** that does reasoning, a **tool registry** that describes available capabilities and their input schemas, **memory** for both short-term context and long-term state, and a **loop controller** that decides when to act, when to re-plan, and when to stop ([Source](https://link.springer.com/article/10.1007/s10462-025-11422-4)).

The central trade-off is freedom versus determinism. Letting an LLM plan freely enables adaptation and creative tool use, but it also makes failure modes harder to predict. Constraining actions with state machines or workflow DSLs makes behavior auditable, repeatable, and easier to test, at the expense of flexibility ([Source](https://blog.sparrow.so/agentic-ai-the-complete-guide-to-architectures-frameworks-and-future-directions-2025)). Practical systems typically put high-blast-radius operations—payments, refunds, external writes—behind explicit state transitions, and leave open-ended reasoning inside those boundaries ([Source](https://link.springer.com/article/10.1007/s10462-025-11422-4)).

Consider a customer-support agent. When a user asks for order status, the loop controller selects `get_order_status`. If the order was returned, the controller invokes `check_return_policy` and stores the policy result in short-term memory. If the item is eligible, the agent calls `initiate_refund` through the tool registry and records the refund ID. The loop stops only when a terminal state—refund submitted, policy rejected, or human handoff—is reached. If manager approval is required, memory persists the pending state so a later session can resume without restarting.

Finally, 2025 learning-paradigm research—especially around reflection and tool-augmented training—has direct engineering implications ([Source](https://link.springer.com/article/10.1007/s10462-025-11422-4)). Reflection and self-correction translate to adding a feedback loop after failed tool calls: the agent re-reads the error, updates its plan, and retries with tighter constraints. Tool-augmented training means capturing successful tool trajectories and fine-tuning the model to choose the right tool with fewer exploratory calls ([Source](https://svitla.com/blog/agentic-ai-trends-2025)). These research advances are not academic; they are the difference between an agent that burns tokens on guesswork and one that converges quickly and safely.

## Framework Landscape: Key Choices in 2025 and 2026

The framework decision is the first architecture bet you’ll make. In 2025–2026, the main choices fall into three categories: graph-native frameworks, role-based orchestration, and first-party SDKs.

- **LangChain/LangGraph** — LangGraph drives execution as an explicit state machine. Best for deterministic, controllable workflows.
- **CrewAI** — A higher-level framework that lets you define agents with roles and goals. Good for rapid multi-agent prototyping.
- **Microsoft Agent Framework** — The union of AutoGen and Semantic Kernel, targeting enterprise applications with prebuilt patterns.
- **OpenAI Agents SDK and Google Agent Development Kit (ADK)** — First-party offerings that prioritize simple agent loops and native integration with their respective model ecosystems. ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison)) ([Source](https://www.langchain.com/resources/ai-agent-frameworks)) ([Source](https://futureagi.substack.com/p/top-5-agentic-ai-frameworks-to-watch))

Scoring across the dimensions that matter:

- **Graph orchestration:** LangGraph leads; Semantic Kernel also supports planner-style graphs, while CrewAI lets you model crew workflows but with less explicit graph control.
- **Multi-agent collaboration:** CrewAI is the quickest path to role-based teams; AutoGen has rich conversation patterns; LangGraph’s graph model requires more manual coordination design.
- **Memory:** LangGraph supports persistent checkpoints; Microsoft Agent Framework provides memory abstractions; first-party SDKs often lean on external stores.
- **Observability:** LangGraph pairs with LangSmith; Microsoft integrates with Application Insights; CrewAI’s telemetry is improving but less mature.
- **Enterprise integration:** Microsoft and Akka-based implementations excel here due to their history in large systems, but LangGraph and CrewAI can be dropped into existing stacks with MCP support. ([Source](https://akka.io/blog/agentic-ai-frameworks)) ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison))

Interoperability and lock-in are now the hardest risks. The industry is converging on open protocols: MCP for tool and context access, and A2A for agent-to-agent communication. Frameworks like LangGraph, CrewAI, and Microsoft Agent Framework all support or are adding MCP, which lets agents consume external tools without rewriting connectors. A2A goes further and enables agents from different vendors to discover and delegate to each other. In practice, this means you can start with one framework and keep the option to route tasks across framework boundaries. Still, each framework imposes model-provider defaults, so decide early whether you are optimizing for portability over a single-vendor experience. ([Source](https://www.langchain.com/resources/ai-agent-frameworks)) ([Source](https://akka.io/blog/agentic-ai-frameworks)) ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison))

Production readiness remains uneven. Before committing, check four things:

- **Telemetry:** Can you trace each agent step, token usage, and cost per run?
- **Evaluation harnesses:** Can you run regression tests against golden datasets?
- **Error handling:** What happens when an LLM call fails or returns malformed JSON?
- **Rate-limit and cost controls:** Does the framework support budgets, max iterations, and retries with backoff?

LangGraph’s ecosystem has the most mature tracing; Microsoft’s framework is strong for enterprise logging; CrewAI and the first-party SDKs are catching up but often require you to build custom guardrails. For independent data on framework behavior, consult the MIT AI Agent Index before committing. ([Source](https://www.ibm.com/think/insights/ai-agents-2025-expectations-vs-reality)) ([Source](https://aiagentindex.mit.edu)) ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next))

Finally, match the framework to the workload. If you need deterministic workflows—approval stages, back-office automation, compliance-heavy processes—prefer a graph DSL like LangGraph or Semantic Kernel. If you are building open-ended research agents that need to plan, explore, and recover from dead ends, choose a dynamic planner pattern like CrewAI’s hierarchical process or AutoGen’s group chat. The two patterns are not interchangeable: a graph forces guardrails into the topology, while a planner trades control for flexibility. ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison)) ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next))

## Build a Minimal Tool-Using Agent and Evaluate It

A minimal agent loop is just three steps: ask the LLM for the next action, execute any requested tool, then feed the result back until the model produces a final answer. You do not need a framework to see where agents break—and once you instrument a raw loop, every framework decision becomes easier to evaluate.

Below is a compact Python implementation that exposes a `get_weather` tool, lets the LLM decide whether to call it, and returns a final answer:

```python
import json
import logging

from openai import OpenAI

client = OpenAI()
MAX_ITERATIONS = 5
MAX_TOOL_ATTEMPTS = 3

def get_weather(city: str) -> dict:
    # Replace with a real API; simulate failures for testing.
    if city.lower() == "fail":
        raise RuntimeError("weather API unavailable")
    return {"city": city, "temp_c": 22.0, "condition": "clear"}

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]

def run_agent(user_query: str) -> str:
    messages = [{"role": "user", "content": user_query}]
    tool_attempts = {}

    for iteration in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            temperature=0,  # minimize nondeterminism during tests
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        logging.info(
            "iteration=%d completion_tokens=%s prompt_tokens=%s tool_calls=%s",
            iteration,
            response.usage.completion_tokens,
            response.usage.prompt_tokens,
            msg.tool_calls,
        )

        if not msg.tool_calls:
            return msg.content or ""

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)

            if tool_attempts.get(name, 0) >= MAX_TOOL_ATTEMPTS:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"error": "max tool attempts exceeded"})
                })
                continue

            try:
                result = get_weather(**args)
                tool_attempts[name] = tool_attempts.get(name, 0) + 1
                payload = json.dumps(result)
            except Exception as exc:
                logging.warning("tool %s failed: %s", name, exc)
                payload = json.dumps({"error": str(exc)})

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": payload,
            })

    raise RuntimeError("max iterations reached")
```

The key guardrails are visible: `MAX_ITERATIONS` stops runaway loops, and `MAX_TOOL_ATTEMPTS` prevents the model from asking for the same tool forever. Retries are handled by converting exceptions into structured tool errors, which the model can use to change its behavior.

- **Instrument everything.** The loop already logs iteration, token usage, and tool calls. For production observability, emit those fields as OpenTelemetry span attributes: `agent.iteration`, `llm.tokens.completion`, `tool.name`, `error.type`. You want to answer: did the tool get called? How long did each step take? Where did the token budget go?
- **Build a small edge-case suite.** Write 10–20 prompts that cover out-of-domain queries, malformed tool output, ambiguous requests, and missing API keys. Keep them in a YAML or JSON file so they become regression tests. Failures should be categorized as wrong tool call, wrong final answer, or loop/timeout.
- **Measure cost per successful task.** Record input/output tokens for each run and add the tool provider cost. Compare against a non-agentic baseline—for example, a prompt that says “answer without tools.” If the agentic path costs 5x more but only improves accuracy by 2%, that complexity may not be justified.
- **Debug nondeterminism deliberately.** Pin `temperature=0` during tests, but remember that APIs can still sample nondeterministically under load. Save the full request/response payloads for every failure. Replaying those payloads lets you separate model regression from tool failures.

A minimal loop like this is a perfect harness. Once it is instrumented and evaluated, you can swap in LangGraph, CrewAI, or a custom orchestration layer and measure the difference—rather than betting on a framework before you have baseline numbers.

## What’s Working in Production: Adoption, ROI, and Industry Signals

Agentic AI adoption is not evenly distributed. ISG’s findings, as summarized in OpenOcean’s 2025 review, show that around 70% of agentic AI use cases and proofs of concept originate in BFSI, retail, and manufacturing. ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next)) Those verticals are not accidental early movers: they run dense, document-heavy processes where the cost of manual handoffs is visible and the ROI of automation can be tracked in hours saved or errors avoided. This concentration is self-reinforcing—as more agents are deployed in these sectors, the patterns, evaluation sets, and compliance wrappers mature, making subsequent projects cheaper and faster.

Bain’s analysis of the agentic wave draws a sharper line between leaders and laggards. Tech-forward enterprises are already capturing measurable ROI, while companies that wait are accumulating integration debt and operational risk. ([Source](https://www.bain.com/insights/state-of-the-art-of-agentic-ai-transformation-technology-report-2025)) The practical implication for engineering leaders is that the competitive window is not about having a demo; it is about having a safe production path for agents that includes data access control, fallback mechanisms, and cost observability. Bain frames this gap as the central dynamic of the agentic era: early movers compound their advantage while late movers face a steeper climb into production.

Financial services shows how quickly the center of gravity is shifting. By early 2026, 52% of institutions were piloting or deploying agentic AI. ([Source](https://www.bain.com/insights/state-of-the-art-of-agentic-ai-transformation-technology-report-2025)) That number matters not just because it is high, but because BFSI is typically conservative; reaching majority adoption signals that compliance, security, and control frameworks have begun to catch up with agent capabilities.

Still, scale remains the exception. Most organizations are in proof-of-concept, not production. The dominant pattern is a single bounded workflow—often in a sandbox or with heavy human supervision—rather than a portfolio of agents operating end-to-end. ([Source](https://cmr.berkeley.edu/2025/08/adoption-of-ai-and-agentic-systems-value-challenges-and-pathways)) The pilot-to-production gap is not primarily a model quality problem; it is an organizational and platform problem. The jump is where the real engineering work begins: integrating with existing systems, handling long-tail edge cases, and designing for auditability.

Where ROI is real today, it clusters around four patterns:

- **Document processing and data extraction** — reducing manual entry and error rates.
- **Customer support triage and deflection** — lowering response latency and routing complex cases to human agents.
- **Compliance workflows** — automatically checking regulatory requirements and generating audit trails.
- **Code generation and maintenance agents** — accelerating routine changes and test writing.

([Source](https://thirdeyedata.ai/data-ai-industry-insights/top-25-agentic-ai-use-cases-in-2025))

These use cases share a common shape: they are bounded, measurable, and safe to run with human-in-the-loop review. That combination—not the sophistication of the underlying model—is what separates production value from pilot theater.

## Security, Identity, and Governance for Agentic Systems

Security is no longer an afterthought in agentic architectures; it is the difference between a pilot and a production system. Across recent industry analyses and academic surveys, identity, access control, and governance are repeatedly named as primary blockers to agentic AI adoption ([Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next), [Source](https://sendbird.com/blog/agentic-ai-challenges), [Source](https://www.ibm.com/think/insights/ai-agents-2025-expectations-vs-reality)). Because agents act autonomously across APIs, data stores, and external services, every security decision must be made before the workflow ships, not after an incident occurs.

### Prefer Service-to-Service Identity Over Human Credentials

Do not authenticate agents with an engineer’s or admin’s IAM account. Use dedicated service identities with short-lived tokens: OAuth2 client credentials, SPIFFE/SVID workloads, or cloud-native workload identity. Set token lifetimes to the duration of the agent’s task, and scope each identity to the APIs the agent is allowed to call. This limits the blast radius if credentials leak and prevents a single compromised agent from inheriting human-level access.

### Enforce Least Privilege at the Tool Boundary

Each agent should receive only the minimal API scopes necessary for its workflow—no broad “read everything” service accounts. Map every tool to the data it actually requires, then encode that mapping in the agent’s identity policy. For example, a support agent that only retrieves order status should not receive permissions to update billing records. Least privilege also simplifies auditing: if a permission is missing, the failure is explicit rather than being silently hidden by overbroad access.

### Make Every Decision Auditable

Build an audit trail that captures every tool call, prompt, decision, and outcome. At minimum, log the agent identity, tool name, sanitized input, output, timestamp, and a correlation ID. This becomes the source of truth for debugging, compliance, and post-incident review. Agentic systems often make opaque decisions; a complete audit trail lets you answer “Why did this agent perform that action?” with evidence instead of speculation.

### Treat External Content as Untrusted Input

Prompt injection and indirect tool misuse are practical threats in multi-agent systems. Content from websites, emails, documents, or user-generated channels should never be concatenated directly into a prompt alongside system-level instructions. Isolate data sources, treat external text as untrusted, and validate tool arguments before execution. This is a security boundary, just as you would treat user input in a web application.

### Add Human Approval Gates for High-Impact Actions

Not every action should be autonomous. Define a policy for human approval when an agent attempts to move money, delete data, or communicate externally. These gates can be implemented as separate approval queues or API callbacks. They create a break-glass control while still allowing agents to complete low-risk portions of a workflow without interruption.

### Test Failure Modes Deliberately

An agent that works when everything is perfect will fail in production. Run drills for revoked credentials, expired sessions, denied permissions, and unexpected tool outputs. Verify that the agent degrades gracefully, reports actionable errors, and does not loop or retry around security controls. Build these tests into CI rather than reserving them for demos.

No framework solves security by itself, but agent frameworks that expose authorization hooks and audit interfaces make these patterns easier to enforce consistently. Organizations that treat security and governance as core agent design constraints—not as a post-deployment checklist—will be the ones able to scale agentic AI beyond internal experiments.

## Future Directions: Benchmarks, Safety, and Multi-Agent Ecosystems

The architectural center of gravity is moving from single agents that complete one task to collaborative multi-agent ecosystems. In production, this means a small group of specialized agents with different responsibilities—planning, tool execution, verification, and exception handling—coordinated by an orchestrator. Framework comparisons make it clear that most products are converging on this pattern, but interoperability is still ad hoc. Agents often expose incompatible schemas, use different authentication models, and treat tool calls as proprietary, so standards for agent discovery, message routing, and shared context are becoming the critical missing layer. ([Source](https://www.moxo.com/blog/agentic-ai-framework-comparison), [Source](https://www.langchain.com/resources/ai-agent-frameworks))

Safety research is following the same system-level turn. At ICLR 2025, agent safety discussions moved beyond bias and toxicity to operational concerns such as containment, audit, and reversibility. MIT's 2025 AI Agent Index is a concrete artifact of this shift: it catalogs prominent agents and their design features—memory, tools, model access—alongside safety characteristics such as sandboxing and monitoring coverage. The result is an evolving baseline that makes it possible to ask not just “is this model safe?” but “did the engineering of this agent build in safeguards before deployment?” ([Source](https://aiagentindex.mit.edu))

Evaluation suites are becoming more realistic. Benchmarks still measure task success, but they increasingly measure plan quality, tool-use correctness, and the ability to recover from failure. The reason is practical: an agent can return a correct final answer after making a series of brittle, opaque decisions, and a benchmark that only checks outcomes will miss the pathology. Survey research on agentic architectures identifies evaluation as a central bottleneck, and several 2025 challenge efforts now score intermediate behavior and recovery paths rather than just final outputs. ([Source](https://link.springer.com/article/10.1007/s10462-025-11422-4), [Source](https://www.readytensor.ai/agentic-ai-2025))

None of this is solved. Long-horizon memory is still externalized into vector stores and context windows; agents do not yet have a reliable way to remember and compose experience across sessions. Continual learning remains an open research problem because updating agents online conflicts with the stability that enterprises need. Self-improvement is promising but currently narrow, and value alignment under uncertainty is harder for agents than for chatbots because an agent's actions have real-world consequences. Enterprise adoption research reinforces the point: trust, governance, security, and cost are the blockers, not model capability. ([Source](https://cmr.berkeley.edu/2025/08/adoption-of-ai-and-agentic-systems-value-challenges-and-pathways), [Source](https://sendbird.com/blog/agentic-ai-challenges))

What should engineering teams plan for? The near-term forecast is deliberately narrow: task-specific agents embedded in 40% of applications by 2026, with horizontal, general-purpose agent platforms arriving only after interoperability and safety patterns stabilize. Until then, the most useful way to approach agentic systems is to design for the missing layer: log every tool call, benchmark failure recovery explicitly, track the cost of long-running agents, and assume that memory is an integration concern rather than a model capability. Those habits—not a specific framework—are what will survive the next market shift. ([Source](https://svitla.com/blog/agentic-ai-trends-2025), [Source](https://www.openocean.vc/articles/the-state-of-agentic-ai-in-2025-whats-working-what-isnt-and-whats-next))
