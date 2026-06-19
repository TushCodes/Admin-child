"""Application middleware registration."""

from .cors import register_cors_middleware
from .database import register_database_middleware
from .error_handling import register_error_handlers
from .observability import register_observability
from .request_context import register_request_context_middleware
from .security_headers import register_security_headers_middleware

from app.admin.middleware.admin_auth import register_admin_auth_middleware

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
