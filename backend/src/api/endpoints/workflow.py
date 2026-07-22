from fastapi import APIRouter, status

from backend.src.models.schema import WorkflowResponse
from backend.src.api.functions.workflow import execute_workflow

router = APIRouter()

router.post("/run", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)(execute_workflow)