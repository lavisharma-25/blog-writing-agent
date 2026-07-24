from fastapi import APIRouter

from backend.src.api.functions.get_logs import get_logs

router = APIRouter()

router.post("/logs")(get_logs)