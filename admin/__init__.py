"""Admin panel package and blueprint definitions."""

from pathlib import Path

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
    """Serve the Flask-Admin dashboard at the legacy `/admin/dashboard` URL."""
    view = current_app.view_functions.get("flask_admin.index")
    if view:
        return view()
    return redirect(url_for("flask_admin.index"))


@admin_bp.route("/admin/consignments", methods=["GET"])
def consignments():
    """Redirect legacy consignment links to the Flask-Admin consignment view."""
    return redirect(url_for("consignments_admin.index_view"))
