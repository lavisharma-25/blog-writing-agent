import json
from typing import Any

from backend.core.logging import logger
from backend.core.settings import settings


def get_blog_dir(blog_id: str):
    return settings.OUTPUT_DIR / blog_id


def get_metadata_path(blog_id: str):
    return get_blog_dir(blog_id) / "metadata.json"


def read_metadata(blog_id: str) -> dict[str, Any]:

    path = get_metadata_path(blog_id)

    if not path.exists():
        logger.warning("Metadata file does not exist for blog_id %s", blog_id)
        return {}
    
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error("Failed to decode metadata file for blog_id %s", blog_id)
        return {}


def write_metadata(blog_id: str, metadata: dict[str, Any]) -> None:

    payload = {
        "blog_id": blog_id,
        **metadata,
    }
    
    path = get_metadata_path(blog_id)

    path.write_text(
        json.dumps(payload, indent=2, default=str),
        encoding="utf-8",
    )
