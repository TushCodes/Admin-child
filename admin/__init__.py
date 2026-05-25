from flask import Blueprint
from flask import redirect, url_for
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

# Import canonical route modules so the blueprint gets its routes registered.
# Doing this here keeps the admin package self-contained while avoiding
# legacy modules that were previously present under app.admin.
from app.routes.admin import (
    auth_routes,
    dashboard,
    backup,
    leads,
    consignment_routes_panel,
    consignment_routes_exports,
    consignment_routes_pod,
)  # noqa: E402, F401 (side-effect imports)
# controllers should not be re-exported from the package; routes import
# controller helpers directly from app.controllers.consignment_controller.
