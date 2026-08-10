import re
import uuid
from typing import Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException, status

from backend.models import schema
from backend.graph.builder import workflow
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


def _run_workflow(topic: str) -> dict:
    """
    Execute the LangGraph workflow.

    Args:
        topic: User input topic.

    Returns:
        Workflow output.
    """
    try:
        state = {
            "topic": topic,
            "mode": "",
            "needs_research": False,
            "queries": [],
            "evidence": [],
            "plan": None,
            "sections": [],
            "final": "",
        }

        return workflow.invoke(state)

    except Exception as exc:
        raise RuntimeError("Failed to execute workflow.") from exc


async def generate_blog(request: schema.WorkflowRequest) -> schema.WorkflowResponse:
    """Generate a blog and persist metadata for list/read/export endpoints."""

    try:
        result = _run_workflow(request.topic)
        print(f"\nRESULT:\n{result}\n")
        plain_result = _to_plain(result)
        print(f"\nPLAIN RESULT:\n{plain_result}\n")

        title = _get_plan_title(result)
        print(f"\nTITLE:\n{title}\n")
        filename = _filename_from_title(title)
        print(f"\nFILENAME:\n{filename}\n")
        created_at = datetime.now().isoformat(timespec="seconds")
        blog_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4()}"

        await write_metadata(
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

        return schema.WorkflowResponse(
            status="success",
            data={
                **plain_result,
                "blog_id": blog_id,
                "filename": filename,
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog generation failed: {str(exc)}",
        ) from exc
