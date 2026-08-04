from backend.src.core.settings import settings
from backend.src.utils.metadata_utils import read_metadata


async def list_blogs():
    blogs = []
    for path in sorted(settings.OUTPUT_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):

        blog_id = path.stem

        metadata = read_metadata(blog_id)

        blogs.append(
            {
                "blog_id": blog_id,
                "filename": metadata.get("filename"),
                "title": metadata.get("title"),
                "user_query": metadata.get("topic"),
                "created_at": metadata.get("created_at") or None
            }
        )

    return {"success": True, "blogs": blogs}


# import asyncio
# import json

# test = asyncio.run(list_blogs())

# print(json.dumps(test, indent=2))