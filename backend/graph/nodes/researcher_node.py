from typing import List

from backend.models.state import State
from backend.core.logging import logger
from backend.graph.prompt import load_prompt
from backend.services.llm_service import get_llm
from backend.models.schema.nodes import EvidencePack
from backend.services.web_search_service import tavily_search


def researcher_node(state: State) -> dict:

    logger.info("Researcher node started")

    queries = state.queries or []
    max_results = 6
    raw_results: List[dict] = []

    logger.debug("Starting Tavily search for %d queries", len(queries))

    for query in queries:
        logger.debug("Searching Tavily for query: %s", query)
        raw_results.extend(tavily_search(query, max_results=max_results))
    
    logger.debug("Tavily search returned %d raw results", len(raw_results))

    if not raw_results:
        logger.warning("Researcher node found no results")
        return {"evidence": []}

    researcher_prompt = load_prompt(agent="researcher")

    messages = researcher_prompt.format_messages(raw_results=raw_results)

    llm = get_llm()
    researcher_llm = llm.with_structured_output(EvidencePack, method="json_mode")
    
    response = researcher_llm.invoke(messages)

    # Deduplicate by URL
    dedup = {}
    for e in response.evidence:
        if e.url:
            dedup[e.url] = e
    
    logger.debug("Researcher selected %d evidence items", len(dedup))

    logger.info("Researcher node completed")

    return {"evidence": list(dedup.values())}