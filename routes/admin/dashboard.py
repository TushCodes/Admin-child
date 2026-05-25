"""Admin dashboard route."""

from flask import render_template
from app.admin import admin_bp
from app.admin.auth import require_admin


@admin_bp.route("/admin/dashboard", methods=["GET"])
@require_admin
def dashboard():
    """Render the custom admin dashboard."""
    return render_template("admin/dashboard.html")
