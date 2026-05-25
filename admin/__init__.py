from flask import Blueprint
from flask import redirect, url_for
from importlib import import_module
from werkzeug.routing import BuildError

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["GET"], endpoint="index")
def _admin_index():
    """Provide a stable `admin.index` endpoint.

    Many parts of the codebase call `url_for('admin.index')` expecting the
    Flask-Admin home. If Flask-Admin failed to initialize or registered under
    a different endpoint, attempting to build that URL raises a BuildError and
    surfaces as a 500. To be robust, try to redirect to Flask-Admin's
    `flask_admin.index` if present, otherwise fall back to the admin login.
    """
    try:
        return redirect(url_for("flask_admin.index"))
    except BuildError:
        return redirect(url_for("admin.login"))

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
