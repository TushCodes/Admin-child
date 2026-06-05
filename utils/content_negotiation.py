"""Shared HTTP content-negotiation helpers."""

from __future__ import annotations

from flask import request as current_request


def wants_json_response(req=None) -> bool:
    """Return True when *req* should receive a JSON response.

    The helper centralizes the app's existing JSON-vs-HTML decisions for
    middleware and error handlers. API paths and JSON request bodies always get
    JSON responses; otherwise JSON is selected only when the Accept header
    explicitly prefers JSON over HTML.
    """
    req = req or current_request

    if req.path.startswith("/api/"):
        return True

    content_type = req.content_type or ""
    if req.is_json or content_type.startswith("application/json"):
        return True

    accept = req.accept_mimetypes
    if not accept:
        return False

    best = accept.best_match(["application/json", "text/html"])
    if best == "application/json":
        return accept["application/json"] >= accept["text/html"]

    # Preserve support for vendor JSON media types such as application/problem+json
    # when they are the explicit best match supplied by the client.
    best_raw = accept.best or ""
    return best_raw.endswith("+json") or best_raw == "application/json"
