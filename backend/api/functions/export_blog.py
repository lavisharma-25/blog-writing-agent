from io import BytesIO
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.models import schema
from backend.core.settings import settings
from backend.utils.metadata_utils import read_metadata
from backend.services.converter_service.html_converter import md_to_html


async def export_blog(request: schema.ExportBlogRequest) -> StreamingResponse:
    """Export a blog in the specified format (Markdown, HTML, PDF, or DOCX)."""

    blog_metadata = await read_metadata(request.blog_id)

    blog_path = settings.OUTPUT_DIR / blog_metadata["filename"]
    blog_data = blog_path.read_text(encoding="utf-8")

    filename = blog_metadata["filename"].rsplit(".", 1)[0]

    if request.output_format == "md":
        content = blog_data.encode("utf-8")
        media_type = "text/markdown"
        download_name = f"{filename}.md"

    elif request.output_format == "html":
        data = await md_to_html(blog_data)
        content = data.encode("utf-8")
        media_type = "text/html"
        download_name = f"{filename}.html"

    # elif request.output_format == "pdf":
    #     pdf_bytes = pdf_converter(blog_data)      # returns bytes
    #     content = pdf_bytes
    #     media_type = "application/pdf"
    #     download_name = f"{filename}.pdf"

    # elif request.output_format == "docx":
    #     docx_bytes = docx_converter(blog_data)    # returns bytes
    #     content = docx_bytes
    #     media_type = (
    #         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    #     )
    #     download_name = f"{filename}.docx"

    else:
        raise HTTPException(status_code=400, detail="Invalid output format.")

    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"'
        },
    )