"""Request lifecycle middleware.

This module owns cross-cutting request context concerns so they are registered
in one predictable place instead of being mixed into route modules.
"""

import time
import uuid

from flask import g, request

REQUEST_ID_HEADERS = ("X-Request-ID", "X-RequestID")


def _resolve_request_id() -> str:
    """Return the inbound request id, or generate a new correlation id."""
    for header in REQUEST_ID_HEADERS:
        request_id = request.headers.get(header)
        if request_id:
            return request_id
    return str(uuid.uuid4())


def register_request_context_middleware(app):
    """Register request correlation and timing middleware."""

    @app.before_request
    def set_request_context():
        g.request_id = getattr(g, "request_id", None) or _resolve_request_id()
        g.request_started_at = time.perf_counter()

    @app.after_request
    def add_request_context_headers(response):
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers.setdefault("X-Request-ID", request_id)

        started_at = getattr(g, "request_started_at", None)
        if started_at is not None:
            duration_ms = (time.perf_counter() - started_at) * 1000
            response.headers.setdefault("X-Response-Time-ms", f"{duration_ms:.2f}")

        return response
