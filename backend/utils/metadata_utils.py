import re
import json
from typing import Any

from backend.core.logging import logger
from backend.core.settings import settings


def get_blog_dir(blog_id: str):
    return settings.OUTPUT_DIR / blog_id


def get_blog_path(blog_id: str):
    return get_blog_dir(blog_id) / "blog.md"


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

    blog_dir = get_blog_dir(blog_id)
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    path = get_metadata_path(blog_id)

    path.write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )


def clean_title_text(title: str) -> str:
    clean_title = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
    clean_title = re.sub(r'[<>:"/\\|?*]', "", clean_title)
    return clean_title.strip() or "Untitled Blog"


def safe_title_name(title: str) -> str:
    clean_title = clean_title_text(title)
    clean_title = clean_title.lower().replace(" ", "_")
    return clean_title or "blog"