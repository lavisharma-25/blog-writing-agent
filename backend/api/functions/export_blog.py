from io import BytesIO
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.services.blog_service import export_blog_data
from backend.models.schema.export import ExportBlogRequest


def export_blog(request: ExportBlogRequest) -> StreamingResponse:
    try:
        content, media_type, download_name = export_blog_data(
            blog_id=request.blog_id,
            output_format=request.output_format,
        )

        return StreamingResponse(
            BytesIO(content),
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{download_name}"'
            },
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc