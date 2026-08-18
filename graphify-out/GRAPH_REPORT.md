# Graph Report - G:\Learning\blog-writing-agent  (2026-08-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 154 nodes · 243 edges · 19 communities (18 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8782b817`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 18

## God Nodes (most connected - your core abstractions)
1. `State` - 11 edges
2. `read_metadata()` - 10 edges
3. `generate_blog()` - 9 edges
4. `load_prompt()` - 8 edges
5. `WorkflowRequest` - 7 edges
6. `WorkflowResponse` - 7 edges
7. `export_blog()` - 6 edges
8. `Settings` - 6 edges
9. `ProvidersResponse` - 6 edges
10. `LLMService` - 6 edges

## Surprising Connections (you probably didn't know these)
- `delete_blog()` --references--> `DeleteBlogRequest`  [EXTRACTED]
  backend/src/api/functions/delete_blog.py → backend/src/models/schema/delete.py
- `delete_blog()` --references--> `DeleteBlogResponse`  [EXTRACTED]
  backend/src/api/functions/delete_blog.py → backend/src/models/schema/delete.py
- `export_blog()` --references--> `ExportBlogRequest`  [EXTRACTED]
  backend/src/api/functions/export_blog.py → backend/src/models/schema/export.py
- `generate_blog()` --references--> `WorkflowRequest`  [EXTRACTED]
  backend/src/api/functions/generate_blog.py → backend/src/models/schema/workflow.py
- `generate_blog()` --references--> `WorkflowResponse`  [EXTRACTED]
  backend/src/api/functions/generate_blog.py → backend/src/models/schema/workflow.py

## Import Cycles
- None detected.

## Communities (19 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (13): planner_node(), refiner_node(), researcher_node(), router_node(), writer_node(), load_prompt(), Loads prompts/{agent}/system.md and returns a ChatPromptTemplate. Args: agent:…, fanout() (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (22): DeleteBlogRequest, DeleteBlogResponse, BaseModel, Response payload for deleting a blog., Request payload for deleting a blog., ExportBlogRequest, BaseModel, Request payload for exporting a blog. (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.23
Nodes (9): delete_blog(), Delete a blog and its associated metadata., export_blog(), Export a blog in the specified format (Markdown, HTML, PDF, or DOCX)., list_blogs(), read_blog(), md_to_html(), read_metadata() (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.29
Nodes (10): _filename_from_title(), generate_blog(), _get_plan_title(), Any, Execute the LangGraph workflow. Args: topic: User input topic. Returns:…, Generate a blog and persist metadata for list/read/export endpoints., _run_workflow(), _to_plain() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (9): execute_workflow(), Execute the blog writing workflow., Execute the LangGraph workflow. Args: topic: User input topic. Returns:…, run_workflow(), BaseModel, Response returned after successful workflow execution., Request payload for executing the workflow., WorkflowRequest (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (5): LLMService, Any, ChatGoogleGenerativeAI, ChatOpenAI, ChatOpenRouter

### Community 6 - "Community 6"
Cohesion: 0.28
Nodes (7): get_logs(), Retrieve log files or log content based on the provided value. This function…, LogsRequest, LogsResponse, BaseModel, Response payload for retrieving log files or log content., Request payload for retrieving log files or log content.

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (7): get_settings(), Resolves the effective (model, api_key, base_url) to use for the "openai"…, Application Settings., Returns a cached Settings instance., Create all required application directories., Settings, BaseSettings

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (5): health_check(), Return the current health status of the API., HealthResponse, BaseModel, Response payload for health check.

### Community 9 - "Community 9"
Cohesion: 0.40
Nodes (4): get_providers(), ProvidersResponse, BaseModel, Available provider/model configuration response.

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (6): get_logger(), _log_file(), Return today's log file., Return a configured logger instance., Logger, Path

### Community 11 - "Community 11"
Cohesion: 0.40
Nodes (5): BaseModel, Response returned after reading a blog., Request payload for reading a blog., ReadBlogRequest, ReadBlogResponse

## Knowledge Gaps
- **1 isolated node(s):** `blog-writing-agent`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMService` connect `Community 5` to `Community 0`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `ProvidersResponse` connect `Community 9` to `Community 1`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **What connects `blog-writing-agent` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13105413105413105 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.11396011396011396 - nodes in this community are weakly interconnected._