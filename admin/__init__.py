"""Admin blueprint routes that keep legacy admin URLs working."""

from importlib import import_module

from pathlib import Path

ADMIN_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = ADMIN_ROOT / "frontend" / "templates"
STATIC_FOLDER = ADMIN_ROOT / "frontend" / "static"

from flask import Blueprint, redirect, url_for, current_app

admin_bp = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    static_url_path="/admin-assets",
)


def _install_legacy_module_aliases():
    """Map old DB/model import paths to modules now housed under admin/."""
    import sys

    legacy_targets = {
        "app.models": "app.admin.models",
        "app.models.base": "app.admin.models.base",
        "app.models.consignment": "app.admin.models.consignment",
        "app.models.lead": "app.admin.models.lead",
        "app.models.track": "app.admin.models.track",
        "app.db": "app.admin.db",
        "app.db.config": "app.admin.db.config",
        "app.db.maintenance": "app.admin.db.maintenance",
        "app.db.seed": "app.admin.db.seed",
        "app.db.session": "app.admin.db.session",
    }
    for legacy_name, target_name in legacy_targets.items():
        sys.modules.setdefault(legacy_name, import_module(target_name))


_install_legacy_module_aliases()


def _register_route_modules():
    """Import route modules for blueprint registration side effects."""
    import_module("app.admin.routes.admin.auth_routes")
    import_module("app.admin.api.dashboard")


def register_admin_routes():
    """Import route modules before registering the admin blueprint."""
    _register_route_modules()


@admin_bp.route("/admin/dashboard", methods=["GET"])
def dashboard():
    """Compatibility route: serve the Flask-Admin index at `/admin/dashboard`.

    Instead of a redirect (which would change the browser URL to `/flask-admin/`),
    invoke the Flask-Admin index view function directly and return its response
    so the client remains on `/admin/dashboard` (tests expect this URL).
    """
    view = current_app.view_functions.get("flask_admin.index")
    if view:
        return view()

    # Fallback to a redirect if the Flask-Admin index isn't available for some reason.
    return redirect(url_for("flask_admin.index"))


@admin_bp.route("/admin/consignments", methods=["GET"])
def consignments():
    """Compatibility route: serve the Flask-Admin consignments list at `/admin/consignments`.

    This mirrors the behavior for `/admin/dashboard` and allows legacy links
    and tests to visit `/admin/consignments` while the real admin view is
    registered under `consignments_admin.index_view`.
    """
    # Redirect to the Flask-Admin managed consignments view. Rendering the
    # view function in-place can cause Flask-Admin's internal URL building to
    # resolve relative endpoints incorrectly, so use a redirect which preserves
    # Flask-Admin's expected endpoint context.
    return redirect(url_for("consignments_admin.index_view"))
