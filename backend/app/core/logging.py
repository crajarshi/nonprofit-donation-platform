import logging
import sys
from typing import Any, Dict
from pathlib import Path
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    *,
    log_path: Path = None,
    level: str = "INFO",
    rotation: str = "20 MB",
    retention: str = "1 month",
    format: str = LOGURU_FORMAT
) -> None:
    """
    Configure logging with loguru.
    
    Args:
        log_path: Path to log file
        level: Minimum log level to record
        rotation: When to rotate log files
        retention: How long to keep log files
        format: Log message format
    """
    # Remove default loguru handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        level=level,
        format=format
    )

    # Add file handler if path is provided
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            level=level,
            format=format,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Update external loggers
    for name in logging.root.manager.loggerDict:
        if name.startswith("uvicorn."):
            logging.getLogger(name).handlers = []


def get_logging_config(log_path: Path = None) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_path: Path to log file
        
    Returns:
        Logging configuration dictionary
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_path) if log_path else "app.log",
                "maxBytes": 20_000_000,  # 20MB
                "backupCount": 5,
            } if log_path else None,
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "INFO"},
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    } 