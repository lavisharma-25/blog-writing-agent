from __future__ import annotations

import sys
import logging
import colorlog
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

from backend.src.core.settings import settings


# =============================================================================
# Configuration
# =============================================================================

LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

CONSOLE_FORMAT = (
    "%(asctime)s | "
    "%(log_color)s%(levelname)-8s%(reset)s | "
    "%(name)-35s | "
    "%(filename)s:%(lineno)-4d | "
    "%(funcName)-25s | "
    "%(message)s"
)

FILE_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)-35s | "
    "%(filename)s:%(lineno)-4d | "
    "%(funcName)-25s | "
    "%(message)s"
)


# =============================================================================
# Internal Helpers
# =============================================================================

def _log_file() -> Path:
    """Return today's log file."""

    today = datetime.now().strftime("%Y-%m-%d")
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return settings.LOGS_DIR / f"{today}.log"


# =============================================================================
# Logger Factory
# =============================================================================

def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    # -------------------------------------------------------------------------
    # Console Formatter (Colored)
    # -------------------------------------------------------------------------

    console_formatter = colorlog.ColoredFormatter(
        CONSOLE_FORMAT,
        datefmt=DATE_FORMAT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    # -------------------------------------------------------------------------
    # File Formatter
    # -------------------------------------------------------------------------

    file_formatter = logging.Formatter(
        FILE_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # -------------------------------------------------------------------------
    # Console Handler
    # -------------------------------------------------------------------------

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(console_formatter)

    # -------------------------------------------------------------------------
    # File Handler
    # -------------------------------------------------------------------------

    file_handler = RotatingFileHandler(
        filename=_log_file(),
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )

    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger(__name__)