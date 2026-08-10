from backend.models import schema
from backend.models.state import State
from backend.core.logging import logger
from backend.graph.prompt import load_prompt
from backend.services.llm_service import llm


def planner_node(state: State) -> dict:

    logger.info("Planner node started")

    evidence = state.evidence or []
    
    logger.debug("Planner received %d evidence items", len(evidence))
    
    planner_prompt = load_prompt(agent="planner")

    messages = planner_prompt.format_messages(
        topic=state.topic,
        mode=state.mode or "closed_book",
        evidence=[e.model_dump() for e in evidence]
    )

    planner_llm = llm.with_structured_output(schema.Plan, method="json_mode")

    plan = planner_llm.invoke(messages)

    logger.debug("Planner generated plan: %s", plan.model_dump())

    logger.info("Planner node completed with %d tasks", len(plan.tasks))

    logger.info("Dispatching writer node tasks")
    
    return {"plan": plan}