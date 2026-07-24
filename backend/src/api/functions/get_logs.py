from datetime import datetime
from fastapi import HTTPException

from backend.src.core.settings import settings
from backend.src.models.schema import GetLogsRequest


def get_logs(request: GetLogsRequest):
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
        request (GetLogsRequest):
            Request object containing the input value used to determine
            the operation to perform.

    Returns:
        dict:
            - For file listing:
                {
                    "status": "success",
                    "files": list[str]
                }

            - For log file content:
                {
                    "status": "success",
                    "file_name": str,
                    "content": list[str]
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

        return {
            "status": "success",
            "files": files,
        }

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

        return {
            "status": "success",
            "files": files,
        }

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

    return {
        "status": "success",
        "file_name": file_path.name,
        "content": logs,
    }