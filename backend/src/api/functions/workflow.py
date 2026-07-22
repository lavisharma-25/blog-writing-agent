from fastapi import HTTPException, status

from backend.src.graph.builder import workflow
from backend.src.models.schema import (WorkflowRequest, WorkflowResponse)


def run_workflow(topic: str) -> dict:
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


async def execute_workflow(request: WorkflowRequest):
    """
    Execute the blog writing workflow.
    """
    try:
        result = run_workflow(request.topic)

        return WorkflowResponse(
            success=True,
            data=result,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(exc)}",
        ) from exc