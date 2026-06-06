"""Admin-local helpers for consistent JSON success and error responses."""

from flask import jsonify


def json_error(message, code=500, **extra):
    """Return a standard JSON error response tuple (body, status)."""
    body = {"success": False, "message": message}
    if extra:
        body.update(extra)
    return jsonify(body), code


def json_success(payload=None, code=200):
    """Return a standard JSON success response tuple (body, status)."""
    if payload is None:
        body = {"success": True}
    elif isinstance(payload, dict):
        body = {"success": True, **payload}
    else:
        body = {"success": True, "data": payload}
    return jsonify(body), code
