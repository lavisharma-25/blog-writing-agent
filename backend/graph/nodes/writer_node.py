from backend.models import schema
from backend.core.logging import logger
from backend.graph.prompt import load_prompt
from backend.services.llm_service import llm


def writer_node(payload: dict) -> dict:

    task = payload["task"]
    topic = payload["topic"]
    plan = payload["plan"]
    mode = payload.get("mode", "closed_book")
    
    logger.info("Writer node started for task_id=%s", task["id"])

    logger.debug("Writing task title=%s topic=%s mode=%s", task["title"], topic, mode)

    bullets_text = "\n- " + "\n- ".join(task["bullets"])

    evidence = [schema.EvidenceItem(**e) for e in payload.get("evidence", [])]

    evidence_text = ""
    if evidence:
        logger.debug("Writer received %d evidence items", len(evidence))
        evidence_text = "\n".join(
            f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}".strip()
            for e in evidence[:20]
        )
    else:
        logger.debug("Writer received no evidence items")
    
    writer_prompt = load_prompt(agent="writer")

    messages = writer_prompt.format_messages(
        blog_title=plan["blog_title"],
        audience=plan["audience"],
        tone=plan["tone"],
        blog_kind=plan["blog_kind"],
        constraints=plan["constraints"],
        topic=topic,
        mode=mode,
        title=task["title"],
        goal=task["goal"],
        target_words=task["target_words"],
        tags=task["tags"],
        requires_research=task["requires_research"],
        requires_citations=task["requires_citations"],
        requires_code=task["requires_code"],
        bullets=bullets_text,
        evidence=evidence_text
    )

    section_md = llm.invoke(messages).content.strip()

    logger.info("Writer node completed for task_id=%s", task["id"])

    logger.debug("Writer output length for task_id=%s: %d characters", task["id"], len(section_md))

    return {"sections": [(task["id"], section_md)]}