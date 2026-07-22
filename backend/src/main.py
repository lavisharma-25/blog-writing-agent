# from backend.src.graph.builder import workflow

# try:
#     def run_workflow(topic: str):
#         out = workflow.invoke(
#             {
#                 "topic": topic,
#                 "mode": "",
#                 "needs_research": False,
#                 "queries": [],
#                 "evidence": [],
#                 "plan": None,
#                 "sections": [],
#                 "final": "",
#             }
#         )

#         return out
    
#     # print(run_workflow("Write a blog on Loop Engineering in Agentic AI"))
#     print(run_workflow("Tell me about Model Harness Engineering in detail"))
    

# except Exception as e:
#     print(e)
#     print(vars(e))

# ============================================================================

from fastapi import FastAPI

from backend.src.api.routers import api_router
from backend.src.core.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(api_router, prefix="/api/v1")