from importlib import import_module

from flask import Blueprint

admin_bp = Blueprint("admin", __name__)


def _register_route_modules():
    """Import route modules for blueprint registration side effects."""
    import_module("app.routes.admin.auth_routes")


_register_route_modules()
