import logging
from pathlib import Path

_LOG_DIR = Path("/logs")
_FMT = "%(asctime)s | %(levelname)s | user-service | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"
_LOGGERS = ("root", "uvicorn", "uvicorn.error", "uvicorn.access", "fastapi")


def setup_logging() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    handler = logging.FileHandler(_LOG_DIR / "user-service.log", encoding="utf-8")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    for name in _LOGGERS:
        logger = logging.getLogger(None if name == "root" else name)
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            logger.addHandler(handler)
        if name == "root":
            logger.setLevel(logging.INFO)
