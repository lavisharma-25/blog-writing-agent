from functools import lru_cache
from langgraph.graph import StateGraph, START, END

from backend.models.state import State
from backend.graph.nodes.planner_node import planner_node
from backend.graph.nodes.refiner_node import refiner_node
from backend.graph.nodes.researcher_node import researcher_node
from backend.graph.nodes.router_node import router_node
from backend.graph.nodes.writer_node import writer_node
from backend.graph.routers import route_next, fanout

def build_workflow():
    # State Graph
    graph = StateGraph(State)

    # Nodes
    graph.add_node("router_node", router_node)
    graph.add_node("researcher_node", researcher_node)
    graph.add_node("planner_node", planner_node)
    graph.add_node("writer_node", writer_node)
    graph.add_node("refiner_node", refiner_node)

    # Edges
    graph.add_edge(START, "router_node")
    graph.add_conditional_edges(
        "router_node", route_next, {
            "research": "researcher_node",
            "orchestrator": "planner_node"
        }
    )
    graph.add_edge("researcher_node", "planner_node")
    graph.add_conditional_edges("planner_node", fanout, ["writer_node"])
    graph.add_edge("writer_node", "refiner_node")
    graph.add_edge("refiner_node", END)

    return graph.compile()

@lru_cache(maxsize=1)
def get_workflow():
    return build_workflow()