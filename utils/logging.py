"""Logging helpers that attach request identifiers to log records."""

import logging

from flask import g, has_request_context, request

__all__ = ["init_app", "RequestIdFilter"]


def _current_request_id():
    try:
        if has_request_context():
            return getattr(g, "request_id", None) or request.headers.get("X-Request-ID")
    except Exception:
        pass
    return None


class RequestIdFilter(logging.Filter):
    """Logging filter that injects a request id into log records when available.

    Records will have a `request_id` attribute (or '-') so formatters can include it.
    """

    def filter(self, record):
        try:
            record.request_id = _current_request_id() or "-"
        except Exception:
            record.request_id = "-"
        return True


def init_app(app, level=None, logfile=None, max_bytes=10 * 1024 * 1024, backup_count=5):
    """Backward-compatible wrapper for middleware observability registration."""
    from app.middleware.observability import register_observability

    register_observability(
        app,
        level=level,
        logfile=logfile,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
