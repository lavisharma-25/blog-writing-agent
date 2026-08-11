from backend.core.settings import settings
from backend.utils.metadata_utils import read_metadata
from backend.services.converter_service.html_converter import md_to_html
# from backend.services.converter_service.pdf_converter import pdf_converter
# from backend.services.converter_service.docx_converter import docx_converter


def read_blog_data(blog_id: str) -> dict:
    blog_metadata = read_metadata(blog_id)

    blog_filename = blog_metadata.get("filename")
    blog_path = settings.OUTPUT_DIR / blog_filename

    if not blog_path.exists():
        raise FileNotFoundError("Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    return {
        "blog_id": blog_metadata.get("blog_id"),
        "filename": blog_metadata.get("filename"),
        "title": blog_metadata.get("title"),
        "markdown": blog_data,
    }


def list_blog_data() -> list[dict]:
    blogs = []

    metadata_files = sorted(
        settings.OUTPUT_DIR.glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    for path in metadata_files:
        blog_id = path.stem
        metadata = read_metadata(blog_id)

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

    metadata_path = settings.OUTPUT_DIR / f"{blog_id}.json"
    blog_metadata = read_metadata(blog_id)

    blog_filename = blog_metadata.get("filename")
    blog_path = settings.OUTPUT_DIR / blog_filename

    if not blog_path.exists():
        raise FileNotFoundError("Blog not found.")

    blog_path.unlink()

    if metadata_path.exists():
        metadata_path.unlink()

    return {
        "filename": blog_path.name,
        "metadata": str(metadata_path),
    }


def export_blog_data(blog_id: str, output_format: str) -> tuple[bytes, str, str]:
    blog_metadata = read_metadata(blog_id)

    blog_filename = blog_metadata["filename"]
    blog_path = settings.OUTPUT_DIR / blog_filename
    blog_data = blog_path.read_text(encoding="utf-8")

    filename = blog_filename.rsplit(".", 1)[0]

    if output_format == "md":
        content = blog_data.encode("utf-8")
        media_type = "text/markdown"
        download_name = f"{filename}.md"

    elif output_format == "html":
        html_data = md_to_html(blog_data)
        content = html_data.encode("utf-8")
        media_type = "text/html"
        download_name = f"{filename}.html"

    # elif output_format == "pdf":
    #     pdf_bytes = pdf_converter(blog_data)
    #     content = pdf_bytes
    #     media_type = "application/pdf"
    #     download_name = f"{filename}.pdf"

    # elif output_format == "docx":
    #     docx_bytes = docx_converter(blog_data)
    #     content = docx_bytes
    #     media_type = (
    #         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    #     )
    #     download_name = f"{filename}.docx"

    else:
        raise ValueError("Invalid output format.")

    return content, media_type, download_name