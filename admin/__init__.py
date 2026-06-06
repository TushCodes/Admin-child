"""Admin panel package and blueprint definitions."""

from pathlib import Path

from flask import Blueprint, current_app, redirect, url_for

ADMIN_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = ADMIN_ROOT / "frontend" / "templates"
STATIC_FOLDER = ADMIN_ROOT / "frontend" / "static"

admin_bp = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    static_url_path="/admin-assets",
)


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


def create_app(*args, **kwargs):
    """Create the standalone admin app when Flask is pointed at `admin`."""
    from .app import create_app as create_standalone_app

    return create_standalone_app(*args, **kwargs)
