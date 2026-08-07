from datetime import datetime
from fastapi import HTTPException

from backend.src.models import schema
from backend.src.core.settings import settings


def get_logs(request: schema.LogsRequest) -> schema.LogsResponse:
    """
    Retrieve log files or log content based on the provided value.

    This function supports three modes of operation:

    1. Empty value ("")
       - Returns the list of log files for the current month.

    2. Month value ("YYYY-MM")
       - Returns the list of log files for the specified month.

    3. Log file value ("YYYY-MM-DD")
       - Reads and returns the contents of the corresponding log file
         (e.g., "2026-07-24" -> "2026-07-24.log").

    Args:
        request (schema.LogsRequest):
            Request object containing the input value used to determine
            the operation to perform.

    Returns:
        schema.LogsResponse:
                {
                    "status": "success",
                    "files": List[str],
                    "content": List[str]
                }

    Raises:
        HTTPException:
            404: If the requested log file does not exist.
    """

    logs_dir = settings.LOGS_DIR
    value = request.value.strip()

    # -------------------------------------------------
    # Case 1: Empty payload -> Current month's log files
    # -------------------------------------------------
    if not value:
        current_prefix = datetime.now().strftime("%Y-%m")  # e.g. 2026-07

        files = sorted(
            [f.name for f in logs_dir.glob(f"{current_prefix}-*.log")],
            reverse=True,
        )

        print(files)

        return schema.LogsResponse(
            status="success",
            files=files,
            content=[],
        )

    # -------------------------------------------------
    # Case 2: YYYY-MM -> Return month's log files
    # -------------------------------------------------
    try:
        month_year = datetime.strptime(value, "%Y-%m")
        prefix = month_year.strftime("%Y-%m")  # 2026-07

        files = sorted(
            [f.name for f in logs_dir.glob(f"{prefix}-*.log")],
            reverse=True,
        )

        return schema.LogsResponse(
            status="success",
            files=None if not files else files,
            content=[],
        )

    except ValueError:
        pass

    # -------------------------------------------------
    # Case 3: Read log file
    # -------------------------------------------------
    file_path = logs_dir / f"{value}.log"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Logs file not found."
        )

    with open(file_path, "r", encoding="utf-8") as f:
        logs = [line.rstrip("\n") for line in f if line.strip()]

    return schema.LogsResponse(
        status="success",
        files=[file_path.name],
        content=logs,
    )