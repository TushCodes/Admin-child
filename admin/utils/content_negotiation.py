"""Admin-local HTTP content-negotiation helpers."""

from __future__ import annotations

from flask import request as current_request


def wants_json_response(http_request=None) -> bool:
    """Return True when *http_request* should receive a JSON response."""
    http_request = http_request or current_request

    if http_request.path.startswith("/api/") or http_request.path.startswith("/admin/api/"):
        return True

    content_type = http_request.content_type or ""
    if http_request.is_json or content_type.startswith("application/json"):
        return True

    accept = http_request.accept_mimetypes
    if not accept:
        return False

    best = accept.best_match(["application/json", "text/html"])
    if best == "application/json":
        return accept["application/json"] >= accept["text/html"]

    best_raw = accept.best or ""
    return best_raw.endswith("+json") or best_raw == "application/json"
