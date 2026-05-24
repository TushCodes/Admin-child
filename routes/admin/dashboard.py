"""Admin dashboard route (thin)."""

from flask import render_template
from app.admin import admin_bp
from app.admin.auth import require_admin


@admin_bp.route("/admin/dashboard", methods=["GET"])
@require_admin
def dashboard():
    """Admin dashboard – protected landing page after login."""
    return render_template("admin/dashboard.html")
