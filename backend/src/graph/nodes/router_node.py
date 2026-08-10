from backend.src.models import schema
from backend.src.models.state import State
from backend.src.core.logging import logger
from backend.src.graph.prompt import load_prompt
from backend.src.services.llm_service import llm


def router_node(state: State) -> dict:

    logger.info("Router node started")
    
    logger.debug("Routing topic: %s", state.topic)

    router_prompt = load_prompt(agent="router")

    messages = router_prompt.format_messages(topic=state.topic)

    router_llm = llm.with_structured_output(schema.RouterDecision, method="json_mode")

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