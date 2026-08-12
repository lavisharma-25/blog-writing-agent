from fastapi import HTTPException, status

from backend.services.workflow_service import generate_blog_data
from backend.models.schema.workflow import WorkflowRequest, WorkflowResponse


def generate_blog(request: WorkflowRequest) -> WorkflowResponse:
    try:
        return WorkflowResponse(
            status="success",
            data=generate_blog_data(request),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog generation failed: {str(exc)}",
        ) from exc