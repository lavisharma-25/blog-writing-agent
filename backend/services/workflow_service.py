import re
import uuid
from typing import Any
from datetime import datetime

from pydantic import BaseModel

from backend.core.logging import logger
from backend.graph.builder import get_workflow
from backend.models.schema.workflow import WorkflowRequest
from backend.utils.metadata_utils import write_metadata


def _to_plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()

    if isinstance(value, list):
        return [_to_plain(item) for item in value]

    if isinstance(value, dict):
        return {key: _to_plain(item) for key, item in value.items()}

    return value


def _get_plan_title(result: dict[str, Any]) -> str:
    plan = result.get("plan")

    if isinstance(plan, BaseModel):
        return str(getattr(plan, "blog_title"))

    if isinstance(plan, dict):
        return str(plan["blog_title"])

    raise ValueError("Workflow result is missing a blog title.")


def _filename_from_title(title: str) -> str:
    clean_title = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
    clean_title = re.sub(r'[<>:"/\\|?*]', "", clean_title)

    return clean_title.lower().replace(" ", "_") + ".md"


def build_initial_state(topic: str) -> dict[str, Any]:
    return {
        "topic": topic,
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "sections": [],
        "final": "",
    }


def run_workflow(topic: str) -> dict[str, Any]:
    state = build_initial_state(topic)

    workflow = get_workflow()
    return workflow.invoke(state)


def generate_blog_data(request: WorkflowRequest) -> dict[str, Any]:
    result = run_workflow(request.topic)
    logger.debug("Workflow result: %s", result)

    plain_result = _to_plain(result)
    logger.debug("Plain workflow result: %s", plain_result)

    title = _get_plan_title(result)
    logger.debug("Title: %s", title)

    filename = _filename_from_title(title)
    logger.debug("Filename: %s", filename)

    created_at = datetime.now().isoformat(timespec="seconds")
    blog_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4()}"

    write_metadata(
        blog_id,
        {
            "title": title,
            "filename": filename,
            "created_at": created_at,
            "topic": request.topic,
            "audience": request.audience,
            "tone": request.tone,
            "blog_kind": request.blog_kind,
            "research_mode": request.research_mode,
            "include_images": request.include_images,
            "output_format": request.output_format,
            "mode": plain_result.get("mode"),
            "needs_research": plain_result.get("needs_research"),
            "queries": plain_result.get("queries", []),
            "sources": plain_result.get("evidence", []),
        },
    )

    return {
        **plain_result,
        "blog_id": blog_id,
        "filename": filename,
    }