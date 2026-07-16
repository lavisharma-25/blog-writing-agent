from langgraph.types import Send

from backend.models.state import State


def fanout(state: State):
    return [
        Send(
            "writer_node",
            {
                "task": task.model_dump(),
                "topic": state.topic,
                "mode": state.mode,
                "plan": state.plan.model_dump(),
                "evidence": [e.model_dump() for e in (state.evidence or [])],
            },
        )
        for task in state.plan.tasks
    ]


def route_next(state: State) -> str:

    print("============ Routing ============")

    return "research" if state.needs_research else "orchestrator"