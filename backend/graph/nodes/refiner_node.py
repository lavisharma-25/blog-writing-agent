import re

from backend.models.state import State
from backend.core.logging import logger
from backend.core.settings import settings


def refiner_node(state: State) -> dict:

    logger.info("Refiner node started")
    
    title = state.plan.blog_title
    title = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
    title = re.sub(r'[<>:"/\\|?*]', "", title)

    logger.debug("Refiner sanitized title: %s", title)

    ordered_sections = [md for _, md in sorted(state.sections, key=lambda x: x[0])]

    logger.debug("Refiner received %d sections", len(ordered_sections))

    if not ordered_sections:
        logger.warning("Refiner received no sections")

    body = "\n\n".join(ordered_sections).strip()

    final_md = f"# {title}\n\n{body}\n"
    
    filename = title.lower().replace(" ", "_") + ".md"
    output_path = settings.OUTPUT_DIR / filename
    output_path.write_text(final_md, encoding="utf-8")

    logger.info("Saved markdown to: %s", output_path.resolve())
    
    logger.debug("Final markdown length: %d characters", len(final_md))

    logger.info("Refiner node completed")

    return {"final": final_md}