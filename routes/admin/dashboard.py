"""Legacy dashboard route shim redirecting to Flask-Admin home."""

from flask import redirect, url_for
from app.admin import admin_bp
from app.admin.auth import require_admin


@admin_bp.route("/admin/dashboard", methods=["GET"])
@require_admin
def dashboard():
    """Backward-compatible dashboard URL."""
    return redirect(url_for("admin.index"))
