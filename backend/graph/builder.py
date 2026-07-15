from langgraph.graph import StateGraph, START, END

from backend.models.state import State
from backend.graph.nodes import (planner_node, fanout, writer_node, refiner_node)


# ==========================================================================
# State Graph
# ==========================================================================
graph = StateGraph(State)

# ==========================================================================
# Nodes
# ==========================================================================
graph.add_node("planner_node", planner_node)
graph.add_node("writer_node", writer_node)
graph.add_node("refiner_node", refiner_node)

# ==========================================================================
# Edges
# ==========================================================================
graph.add_edge(START, "planner_node")
graph.add_conditional_edges("planner_node", fanout, ["writer_node"])
graph.add_edge("writer_node", "refiner_node")
graph.add_edge("refiner_node", END)

# ==========================================================================
# Workflow
# ==========================================================================
workflow = graph.compile()

from openrouter.errors import TooManyRequestsResponseError

try:
    out = workflow.invoke(
        # {"topic": "Write a blog on Self Attention", "sections": []}
        {"topic": "Write a blog on Loop Engineering", "sections": []}
    )
    print(out)

except TooManyRequestsResponseError as e:
    print(e)
    print(vars(e))