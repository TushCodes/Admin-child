"""Observability middleware registration."""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.utils.logging import RequestIdFilter


def register_observability(
    app, level=None, logfile=None, max_bytes=10 * 1024 * 1024, backup_count=5
):
    """Register request-aware logging setup for the application."""
    log_level = level or app.config.get("LOG_LEVEL", "INFO")
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(log_level)

    log_format = "%(asctime)s %(levelname)s [%(name)s] %(request_id)s %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Clear existing root handlers to avoid duplicate logs in some environments.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(log_level)
    stream.setFormatter(formatter)
    stream.addFilter(RequestIdFilter())
    root.addHandler(stream)

    configured_logfile = logfile or app.config.get("LOG_FILE")
    if configured_logfile:
        file_handler = RotatingFileHandler(
            configured_logfile, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIdFilter())
        root.addHandler(file_handler)

    # Mirror handlers onto the Flask app logger and set its level.
    app.logger.handlers = root.handlers
    app.logger.setLevel(log_level)


def register_observability_middleware(*args, **kwargs):
    """Backward-compatible alias for register_observability()."""
    return register_observability(*args, **kwargs)
