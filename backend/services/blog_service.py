import shutil

from backend.core.settings import settings
from backend.services.converter_service.html_converter import md_to_html
# from backend.services.converter_service.pdf_converter import pdf_converter
# from backend.services.converter_service.docx_converter import docx_converter
from backend.utils.metadata_utils import get_blog_dir, read_metadata, safe_title_name


def _get_blog_md_path(blog_id: str):
    return get_blog_dir(blog_id) / "blog.md"


def read_blog_data(blog_id: str) -> dict:
    blog_metadata = read_metadata(blog_id)
    blog_path = _get_blog_md_path(blog_id)

    if not blog_path.exists():
        raise FileNotFoundError("Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    return {
        "blog_id": blog_id,
        "filename": blog_metadata.get("filename"),
        "title": blog_metadata.get("title"),
        "markdown": blog_data,
    }


def list_blog_data() -> list[dict]:
    blogs = []

    blog_dirs = sorted(
        [path for path in settings.OUTPUT_DIR.iterdir() if path.is_dir()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    for blog_dir in blog_dirs:
        blog_id = blog_dir.name
        metadata = read_metadata(blog_id)

        if not metadata:
            continue

        blogs.append(
            {
                "blog_id": blog_id,
                "filename": metadata.get("filename"),
                "title": metadata.get("title"),
                "user_query": metadata.get("topic"),
                "created_at": metadata.get("created_at") or None,
            }
        )

    return blogs


def delete_blog_data(blog_id: str) -> dict:
    """ Delete a blog and its associated metadata."""

    blog_dir = get_blog_dir(blog_id)

    if not blog_dir.exists():
        raise FileNotFoundError("Blog not found.")

    shutil.rmtree(blog_dir)

    return {
        "filename": "blog.md",
        "metadata": "metadata.json",
    }


def export_blog_data(blog_id: str, output_format: str) -> tuple[bytes, str, str]:
    blog_metadata = read_metadata(blog_id)
    blog_path = _get_blog_md_path(blog_id)

    if not blog_path.exists():
        raise FileNotFoundError("Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    title = blog_metadata.get("title") or blog_id
    download_stem = safe_title_name(title)


    if output_format == "md":
        content = blog_data.encode("utf-8")
        media_type = "text/markdown"
        download_name = f"{download_stem}.md"

    elif output_format == "html":
        html_data = md_to_html(blog_data)
        content = html_data.encode("utf-8")
        media_type = "text/html"
        download_name = f"{download_stem}.html"

    # elif output_format == "pdf":
    #     pdf_bytes = pdf_converter(blog_data)
    #     content = pdf_bytes
    #     media_type = "application/pdf"
    #     download_name = f"{download_stem}.pdf"

    # elif output_format == "docx":
    #     docx_bytes = docx_converter(blog_data)
    #     content = docx_bytes
    #     media_type = (
    #         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    #     )
    #     download_name = f"{download_stem}.docx"

    else:
        raise ValueError("Invalid output format.")

    return content, media_type, download_name