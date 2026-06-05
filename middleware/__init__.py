"""Application middleware registration."""

from app.middleware.admin_auth import register_admin_auth_middleware
from app.middleware.cors import register_cors_middleware
from app.middleware.database import register_database_middleware
from app.middleware.error_handling import register_error_handlers
from app.middleware.observability import register_observability
from app.middleware.request_context import register_request_context_middleware
from app.middleware.security_headers import register_security_headers_middleware

__all__ = ["register_middleware"]


def register_middleware(app):
    """Register all application-wide middleware in standard execution order."""
    register_request_context_middleware(app)
    register_observability(app)
    register_cors_middleware(app)
    register_database_middleware(app)
    register_admin_auth_middleware(app)
    register_security_headers_middleware(app)
    register_error_handlers(app)
