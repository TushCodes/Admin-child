"""Admin authentication middleware.

The Flask-Admin views still expose their own access checks, but this middleware
provides one standard gate for admin URL spaces before requests reach handlers.
"""

from flask import redirect, request, url_for

from app.controllers.responses import json_error

ADMIN_AUTH_EXEMPT_PATHS = ("/admin/login",)
ADMIN_AUTH_PREFIXES = ("/admin", "/flask-admin")


def _is_admin_path(path: str) -> bool:
    return any(
        path == prefix or path.startswith(f"{prefix}/")
        for prefix in ADMIN_AUTH_PREFIXES
    )


def _is_exempt_path(path: str) -> bool:
    return any(
        path == exempt or path.startswith(f"{exempt}/")
        for exempt in ADMIN_AUTH_EXEMPT_PATHS
    )


def _wants_json_response() -> bool:
    return (
        request.path.startswith("/api/")
        or "application/json" in (request.accept_mimetypes.best or "")
        or (request.content_type or "").startswith("application/json")
        or request.is_json
    )


def register_admin_auth_middleware(app):
    """Register middleware that protects admin endpoints consistently."""

    @app.before_request
    def enforce_admin_authentication():
        path = request.path.rstrip("/") or "/"
        if not _is_admin_path(path) or _is_exempt_path(path):
            return None

        from app.admin.auth import is_admin_authenticated

        if is_admin_authenticated():
            return None

        if _wants_json_response():
            return json_error("Authentication required", 401)

        return redirect(url_for("admin.login", next=request.url))
