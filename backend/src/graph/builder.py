from langgraph.graph import StateGraph, START, END

from backend.src.graph import nodes
from backend.src.graph import routers
from backend.src.models.state import State


# ==========================================================================
# State Graph
# ==========================================================================
graph = StateGraph(State)

# ==========================================================================
# Nodes
# ==========================================================================
graph.add_node("router_node", nodes.router_node)
graph.add_node("researcher_node", nodes.researcher_node)
graph.add_node("planner_node", nodes.planner_node)
graph.add_node("writer_node", nodes.writer_node)
graph.add_node("refiner_node", nodes.refiner_node)

# ==========================================================================
# Edges
# ==========================================================================
graph.add_edge(START, "router_node")
graph.add_conditional_edges(
    "router_node", routers.route_next, {
        "research": "researcher_node",
        "orchestrator": "planner_node"
    }
)
graph.add_edge("researcher_node", "planner_node")
graph.add_conditional_edges("planner_node", routers.fanout, ["writer_node"])
graph.add_edge("writer_node", "refiner_node")
graph.add_edge("refiner_node", END)

# ==========================================================================
# Workflow
# ==========================================================================
workflow = graph.compile()