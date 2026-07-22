import uvicorn

from backend.src.core.settings import settings


if __name__ == "__main__":

    base_url = f"http://{settings.HOST}:{settings.PORT}"

    print(f"🚀 Server : {base_url}")
    print(f"📖 Docs   : {base_url}/docs")
    print(f"📄 ReDoc  : {base_url}/redoc")

    uvicorn.run(
        "backend.src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
