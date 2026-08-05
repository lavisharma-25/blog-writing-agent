import json
from typing import Any
from datetime import datetime

from backend.src.core.settings import settings


async def read_metadata(blog_id: str) -> dict[str, Any]:
    
    path = settings.OUTPUT_DIR / f"{blog_id}.json"

    if not path.exists():
        print(f"Metadata file does not exist for blog_id {blog_id}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


async def write_metadata(blog_id: str, metadata: dict[str, Any]) -> None:

    payload = {
        "blog_id": blog_id,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        **metadata,
    }

    path = settings.OUTPUT_DIR / f"{blog_id}.json"
    
    path.write_text(
        json.dumps(payload, indent=2, default=str),
        encoding="utf-8",
    )
