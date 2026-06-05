"""HTTP response negotiation helpers shared by middleware and handlers."""

from flask import request


def wants_json_response() -> bool:
    """Return True when the current request should receive a JSON response."""
    return (
        request.path.startswith("/api/")
        or request.accept_mimetypes.accept_json
        or "application/json" in (request.accept_mimetypes.best or "")
        or (request.content_type or "").startswith("application/json")
        or request.is_json
    )
