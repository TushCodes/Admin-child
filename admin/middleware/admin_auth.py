"""Admin authentication middleware.

The Flask-Admin views still expose their own access checks, but this middleware
provides one standard gate for admin URL spaces before requests reach handlers.
"""

from flask import current_app, redirect, request, url_for

from ..controllers.responses import json_error
from ..utils.content_negotiation import wants_json_response

ADMIN_AUTH_EXEMPT_PATHS = ("/admin", "/admin/login")
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


def register_admin_auth_middleware(app):
    """Register middleware that protects admin endpoints consistently."""

    @app.before_request
    def enforce_admin_authentication():
        path = request.path.rstrip("/") or "/"
        if not _is_admin_path(path) or _is_exempt_path(path):
            return None

        from ..auth import is_admin_authenticated

        if is_admin_authenticated():
            return None

        internal_token = (
            current_app.config.get("ADMIN_DASHBOARD_API_TOKEN")
            or current_app.config.get("SECRET_KEY")
            or ""
        )
        supplied_token = request.headers.get("X-Internal-Dashboard-API", "")
        is_dashboard_api_path = path.startswith("/admin/api/")
        if (
            is_dashboard_api_path
            and internal_token
            and supplied_token
            and supplied_token == internal_token
        ):
            return None

        if wants_json_response(request):
            return json_error("Authentication required", 401)

        return redirect(url_for("admin.login", next=request.url))
