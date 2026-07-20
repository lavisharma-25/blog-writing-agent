# app.py
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5030)),
        reload=True,
    )
