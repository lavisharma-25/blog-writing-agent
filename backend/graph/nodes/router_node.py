from backend.models.state import State
from backend.core.logging import logger
from backend.graph.prompt import load_prompt
from backend.services.llm_service import llm
from backend.models.schema.nodes import RouterDecision


def router_node(state: State) -> dict:

    logger.info("Router node started")
    
    logger.debug("Routing topic: %s", state.topic)

    router_prompt = load_prompt(agent="router")

    messages = router_prompt.format_messages(topic=state.topic)

    router_llm = llm.with_structured_output(RouterDecision, method="json_mode")

    decision = router_llm.invoke(messages)

    logger.debug("Router decision: %s", decision.model_dump())

    logger.info(
        "Router node completed with mode=%s needs_research=%s queries=%d",
        decision.mode,
        decision.needs_research,
        len(decision.queries),
    )

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode,
        "queries": decision.queries
    }