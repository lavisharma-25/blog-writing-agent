# How to Evaluate an AI Research Agent for Hallucination and Source Quality

## Define Hallucination and Source Quality for AI Research Agents

Before you can measure hallucination, you need a working definition. The arXiv survey on LLM-based agent hallucinations distinguishes two types: **intrinsic hallucinations**, where the agent contradicts the provided context, and **extrinsic hallucinations**, where it generates information unsupported by any source ([Source](https://arxiv.org/html/2509.18970v1)). In research agents, both manifest as common failure modes: fabricated citations, misattributed claims, and reliance on outdated or irrelevant sources ([Source](https://www.getmaxim.ai/articles/the-state-of-ai-hallucinations-in-2025-challenges-solutions-and-the-maxim-ai-advantage)).

Source quality is equally important. Evaluate each source against four criteria: **authority** (who published it), **relevance** (does it address the query), **recency** (is it current), and **verifiability** (can the claim be independently checked) ([Source](https://www.braintrust.dev/articles/ai-hallucination-evaluations-metrics-methods-2026)). These criteria directly impact trust — a well-cited but weak source can still produce misleading output.

Crucially, hallucination is not binary. Treat it as a spectrum from fully grounded to partially hallucinated, where some claims are supported and others are not ([Source](https://deepeval.com/docs/metrics-hallucination)). Finally, Apple's research warns that automatic detection metrics are themselves unreliable — the "mirage of hallucination detection" — so you must validate your evaluation pipeline before trusting its results ([Source](https://machinelearning.apple.com/research/hallucination-detection)).

## Build an Evaluation Harness with Golden Datasets and Metrics

A golden dataset is the backbone of any evaluation harness. Start with test cases that exercise three distinct tasks:

- **Summarization**: queries like "Summarize the key findings of the 2025 AI hallucination report" with a reference summary and 2–3 supporting sources.
- **QA**: questions with a specific expected answer and the source documents that support it.
- **Citation generation**: queries that require the agent to produce claims with explicit source attributions.

Each test case should include the query, expected output, reference sources, and a scoring rubric.

Once the dataset is ready, implement a runner script that invokes the agent on each case, records the output, retrieved sources, and metadata (latency, token usage, model version), and stores everything as structured JSON:

```python
import json
from typing import Dict, List

def run_harness(agent, golden_dataset: List[Dict]) -> List[Dict]:
    results = []
    for case in golden_dataset:
        output, sources, meta = agent.run(case["query"])
        results.append({
            "case_id": case["id"],
            "query": case["query"],
            "output": output,
            "retrieved_sources": sources,
            "expected_sources": case["reference_sources"],
            "metadata": meta,
        })
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    return results
```

With results in hand, compute three core metrics:

- **Faithfulness (groundedness)**: the fraction of claims in the output that are supported by the retrieved context.
- **Answer relevance**: how well the output addresses the query, often scored with an LLM-as-a-judge.
- **Source precision/recall**: whether the cited sources are correct and complete relative to the reference set.

Here is a minimal faithfulness scorer that checks each claim against the retrieved context:

```python
def faithfulness_score(output: str, context: str) -> float:
    claims = extract_claims(output)  # split into atomic claims
    if not claims:
        return 1.0
    supported = sum(1 for c in claims if is_entailed(c, context))
    return supported / len(claims)
```

`extract_claims` splits the output into atomic statements; `is_entailed` can use an NLI model or an LLM judge to verify each claim against the context.

Finally, validate the harness by running it on a known-good agent (e.g., a tuned RAG pipeline) and a known-bad agent (e.g., one that ignores retrieval). The good agent should score higher on faithfulness and source precision; the bad agent should score low. If the harness fails to discriminate, refine your metrics or dataset before trusting any future results.

## Use LLM-as-a-Judge for Scalable Hallucination Detection

Manual scoring doesn't scale. An LLM-as-a-judge systematically detects hallucinations by comparing the agent's output against the retrieved context, giving you a structured, repeatable signal for every run.

### 1. Design a rubric-based judge prompt

Build a judge prompt with a 1-5 scale where 5 means every claim is fully supported by the context and 1 means the output is largely fabricated. The prompt must instruct the judge to check each claim in the output against the context, and flag any claim that is unsupported, contradicted, or fabricated. Rubric-based scoring is a standard pattern in agent evaluation frameworks ([Source](https://galileo.ai/blog/agent-evaluation-framework-metrics-rubrics-benchmarks)).

### 2. Compare judge models against human judgments

Don't trust a single judge model. Run the same prompt with GPT-4o, Claude, and Llama, then measure agreement with human annotations using Cohen's kappa. A kappa above 0.7 indicates substantial agreement; below that, your judge is unreliable. Apple's research shows that many hallucination metrics can be misleading when evaluated in isolation, so human calibration is essential ([Source](https://machinelearning.apple.com/research/hallucination-detection)).

### 3. Mitigate bias with chain-of-thought

Judges exhibit position bias and overfit to rubric phrasing. Use chain-of-thought prompting to force the judge to reason step-by-step before assigning a score, and sample multiple times (e.g., 3–5 runs) to reduce variance ([Source](https://www.braintrust.dev/articles/ai-hallucination-evaluations-metrics-methods-2026)).

### 4. Handle "not applicable" cases

When the agent produces output with no retrieved context (e.g., a general knowledge question), faithfulness scoring is meaningless. Datadog recommends adapting the rubric to mark these cases as N/A rather than forcing a low score, which would unfairly penalize the model ([Source](https://www.datadoghq.com/blog/ai/llm-hallucination-detection)).

### 5. Integrate into your evaluation harness

Wire the judge into the evaluation harness from Task 2 as a scoring function that runs after each agent response. Store the judge's score, the chain-of-thought reasoning, and the kappa results in your logs so you can track drift over time.

## Evaluate Source Quality with Lateral Reading and Fact-Checking

Source quality is the foundation of any hallucination evaluation. A research agent can produce fluent, confident text, but if the sources it cites are fabricated or low-authority, the output is untrustworthy. Here's how to measure source quality systematically.

**1. Implement lateral reading.** For every cited source, verify its existence, authority, and relevance by opening new tabs and checking the publication, the author, and the claim itself. This "lateral reading" technique is recommended by university research guides for verifying AI-generated content ([Source](https://guides.library.tamucc.edu/AI/lateralreadingAI)). USC's IT services similarly advise fact-checking AI outputs by cross-referencing claims against independent sources ([Source](https://itservices.usc.edu/2025/10/20/using-ai-for-research-fact-check)).

**2. Automate the cross-referencing.** Manual lateral reading doesn't scale. Use automated fact-checking tools that cross-reference claims against databases of reliable sources. Bluebash describes AI agents for fact-checking that verify claims against authoritative sources and flag discrepancies ([Source](https://www.bluebash.co/services/artificial-intelligence/ai-agents/fact-checking)). You can also add hallucination metrics from frameworks like DeepEval and promptfoo to flag unsupported claims programmatically ([Source](https://deepeval.com/docs/metrics-hallucination), [Source](https://www.promptfoo.dev/docs/guides/prevent-llm-hallucinations)).

**3. Score and aggregate.** For each source, assign a score based on domain authority, publication date, and citation count. Aggregate these into a composite source quality score per output. This rubric-based approach aligns with agent evaluation frameworks that recommend scoring and aggregation ([Source](https://galileo.ai/blog/agent-evaluation-framework-metrics-rubrics-benchmarks)).

**4. Calibrate with human review.** Automated scores are noisy. Run a human reviewer on a subset of outputs (e.g., 10–20%) to validate the automated scores and correct assumptions. This hybrid approach is common in production agent evaluation ([Source](https://www.algolia.com/blog/ai/ai-agent-evaluation-frameworks-metrics-testing-strategies)).

**5. Know the limits.** Automated fact-checking struggles with niche, domain-specific claims. Apple's research on hallucination detection warns that evaluation metrics themselves can be misleading ([Source](https://machinelearning.apple.com/research/hallucination-detection)). For specialized domains, you'll need domain-specific source validation pipelines.

## Implement RAG Grounding Checks to Verify Faithfulness

RAG grounding is the alignment between an agent's output and the retrieved context it was given. In a research agent, every claim sentence should trace back to a retrieved document; if it doesn't, you're looking at a hallucination. Firecrawl and Decagon both define grounding this way — the output is faithful only if it is entailed by the retrieved context.

Three metrics quantify grounding for RAG:

- **Context relevance** — how well the retrieved chunks match the user's query.
- **Faithfulness** — whether each claim in the output is supported by the retrieved context.
- **Context utilization** — how much of the retrieved context the agent actually used.

A practical grounding check compares the output against the retrieved context using either semantic similarity or an LLM-as-a-judge. Semantic similarity scores both the output sentence and the context, then flags any sentence whose cosine similarity falls below a threshold. LLM-as-a-judge is more robust: you prompt a judge model to verify whether each claim is entailed by the context ([Source](https://www.datadoghq.com/blog/ai/llm-hallucination-detection)).

Two edge cases trip up naive grounding checks. First, the agent may use external knowledge not present in the retrieved context. This isn't necessarily a hallucination, but it breaks the grounding check — flag it and require either expanding the context or rejecting the claim. Second, the retrieved context may be incomplete. When chunks are truncated or missing key passages, the agent is forced to guess; the check should emit a "context insufficiency" signal rather than a false hallucination.

DeepEval's hallucination metric is a solid reference implementation. It uses an LLM to extract claims from the output, then checks each claim against the retrieved context with a separate entailment prompt, returning a score between 0 and 1 ([Source](https://deepeval.com/docs/metrics-hallucination)). You can plug it into your evaluation pipeline directly, and it handles the edge cases above by distinguishing between unsupported claims and insufficient context.

## Run Benchmarks and Custom Evals for Agent Comparison

**Select 2–4 complementary benchmarks.** No single benchmark covers everything a research agent does. Evidently AI's roundup of agent benchmarks highlights options like GAIA for general reasoning, SWE-bench for tool use, and WebArena for web-based retrieval ([Source](https://www.evidentlyai.com/blog/ai-agent-benchmarks)). Galileo's agent evaluation framework similarly recommends pairing benchmarks with rubric-based scoring to cover both objective and subjective dimensions ([Source](https://galileo.ai/blog/agent-evaluation-framework-metrics-rubrics-benchmarks)). Choose 2–4 that map to your agent's core workflows: reasoning, tool use, and retrieval.

**Create custom evals on your own domain data.** Benchmarks measure generic capability, but they won't reflect your specific domain, citation style, or user queries. Build a small eval set from real queries with ground-truth answers and expected source citations. Use it to measure hallucination rate and source quality in realistic scenarios. The InfoQ article on evaluating AI agents emphasizes that production evals must be grounded in the actual tasks your agent performs, not just academic benchmarks ([Source](https://www.infoq.com/articles/evaluating-ai-agents-lessons-learned)).

**Combine benchmark scores with custom eval results.** Benchmarks give you a baseline for comparing models and versions; custom evals tell you whether the agent works in your context. Track both in a single dashboard and weight them by your priorities to get a holistic view of performance.

**Use best practices for metrics.** The InfoQ article identifies task completion accuracy and grounding faithfulness as key metrics for agent evaluation ([Source](https://www.infoq.com/articles/evaluating-ai-agents-lessons-learned)). Task completion accuracy measures whether the agent finished the research task correctly; grounding faithfulness checks whether every claim in the output is supported by the cited source. Use both, plus a factual consistency score for hallucination detection.

**Set up regression testing.** Run your evals on every change to the agent's prompts, model, or retrieval layer. If a change drops benchmark scores or grounding faithfulness below a threshold, block the merge. This ensures new changes don't degrade source quality over time.

## Debug and Monitor Hallucination in Production

**1. Log everything for post-hoc analysis.** A research agent's failures are rarely visible in the final answer alone. Log every input, output, retrieved source, and intermediate reasoning step so you can reconstruct what actually happened. Structured logs with trace IDs let you replay a user complaint back to the exact retrieval path and model call that produced it. As the InfoQ review of agent evaluation practices notes, observability is the foundation for any meaningful evaluation effort ([Source](https://www.infoq.com/articles/evaluating-ai-agents-lessons-learned)).

**2. Trace the decision flow.** Use tracing tools like LangSmith or OpenTelemetry to visualize each step: which tool was invoked, which sources were retrieved, and how the model reasoned over them. A trace turns a black-box hallucination into a pinpointed failure—for example, the retriever returned a stale document, or the model ignored a conflicting source. This aligns with agent evaluation frameworks that treat tracing as a core debugging practice ([Source](https://www.algolia.com/blog/ai/ai-agent-evaluation-frameworks-metrics-testing-strategies)).

**3. Detect hallucinations in real time.** Beyond post-hoc analysis, add live detection using semantic entropy—measuring the model's uncertainty across multiple sampled outputs—or LLM-as-a-judge checks that compare claims against retrieved sources ([Source](https://www.getmaxim.ai/articles/the-state-of-ai-hallucinations-in-2025-challenges-solutions-and-the-maxim-ai-advantage)). Frameworks like DeepEval provide built-in hallucination metrics you can wire directly into your pipeline ([Source](https://deepeval.com/docs/metrics-hallucination)).

**4. Build a monitoring dashboard.** Track hallucination rate, source quality scores, and user feedback over time. A single dashboard lets you spot regressions immediately after a model or prompt change. The Algolia agent evaluation guide stresses combining automated metrics with qualitative user feedback for a complete picture ([Source](https://www.algolia.com/blog/ai/ai-agent-evaluation-frameworks-metrics-testing-strategies)).

**5. Establish a reproduce-and-fix workflow.** When a hallucination is reported, use your logs to reproduce the exact trace, identify the failing step, and fix it—whether that means improving retrieval, adding a fact-check step, or updating the prompt. The promptfoo guide on preventing hallucinations recommends this loop as the most reliable way to reduce errors over time ([Source](https://www.promptfoo.dev/docs/guides/prevent-llm-hallucinations)).

## Consider Cost and Performance Trade-offs in Evaluation

Evaluation isn't free. Every LLM-as-judge call costs tokens, and human review costs hours. Before you build an evaluation pipeline, estimate both sides. For a sample of 1,000 agent outputs, a judge model at $0.01 per call costs $10; a human reviewer at 5 minutes per output costs roughly 83 hours. The right choice depends on how much accuracy you need per dollar.

**Use sampling to control spend.** You don't need to evaluate every output at the same depth. A practical tiered approach:

- **High-confidence detection:** Sample 5–10% of outputs with a cheap judge to catch obvious hallucinations.
- **Critical cases:** Run full evaluation on outputs that are user-facing, high-stakes, or flagged by the cheap judge as borderline.

This keeps your false-negative rate low where it matters without paying for full evaluation on routine outputs.

**Optimize judge prompts for token efficiency.** A verbose rubric with multiple examples can double your token cost per call. Use a concise rubric: a single paragraph defining what counts as a hallucination, plus a binary or 1–5 scale. Test the concise version against the verbose one on a small labeled set — you'll often find accuracy holds within 1–2% while token usage drops 30–50%.

**Compare judge model sizes.** A large model (e.g., GPT-4-class) may catch subtle source mismatches, but a smaller model (e.g., GPT-4o-mini or a fine-tuned 7B) can be 10–20x cheaper. Run both on a 200-sample benchmark. If the small model's agreement with human labels is within 5%, the cost savings usually justify it for high-volume evaluation.

**Mind production impact.** Running evaluations inline adds latency to your agent's response path. Schedule batch evaluations during off-peak hours, or run them asynchronously in a background queue. For real-time checks, cache judge results by source-output hash to avoid duplicate calls.

## Build a Continuous Evaluation Pipeline for Your Agent

A one-time evaluation tells you where your agent stands today. A continuous pipeline tells you whether it's getting better or silently degrading. Here's how to wire your eval suite into the development workflow.

### Gate merges with CI/CD checks

Add the evaluation suite as a required step in your CI pipeline. On every pull request, run the full hallucination and source-quality checks against a fixed baseline. If the hallucination rate degrades beyond a threshold (for example, a 2% increase) or source accuracy drops, block the merge. This turns evaluation from a manual chore into an automated quality gate that catches regressions before they reach production.

### Test against a realistic staging environment

Production-like data matters. Set up a staging environment that mirrors your production traffic — the same document types, query patterns, and retrieval sources. Run the agent suite there before every deployment. This surfaces issues that unit tests miss, such as retrieval drift, source formatting changes, or degraded citation quality under realistic load.

### Grow the eval set from real usage

Your initial test suite is a starting point, not a ceiling. Automatically mine user feedback and production logs for signals: queries where users flagged a result, corrected a source, or abandoned the agent mid-task. Add those as new eval cases. Over time, the suite reflects the real distribution of user behavior, not just your initial assumptions.

### Re-evaluate on a schedule

Benchmarks and source data evolve. Schedule periodic re-evaluation — weekly or monthly — against updated benchmarks and refreshed source corpora. This keeps your metrics relevant and surfaces drift before it reaches end users.

### Document and share results

Finally, make the evaluation process transparent. Document the metrics, thresholds, and methodology. Share results with stakeholders so they can see how the agent improves over time. Trust is built on evidence, not promises.

A continuous evaluation harness turns hallucination detection from a one-off audit into a living process — one that keeps your agent honest as it evolves.
