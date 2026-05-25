from importlib import import_module

from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

def _register_route_modules():
    """Import route modules for blueprint registration side effects."""
    for module in (
        "app.routes.admin.auth_routes",
        "app.routes.admin.dashboard",
        "app.routes.admin.backup",
        "app.routes.admin.leads",
        "app.routes.admin.consignment_routes_panel",
        "app.routes.admin.consignment_routes_exports",
        "app.routes.admin.consignment_routes_pod",
    ):
        import_module(module)


_register_route_modules()
