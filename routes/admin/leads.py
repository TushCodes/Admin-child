"""Legacy leads routes shimmed to Flask-Admin views."""

from flask import redirect, url_for
from app.admin import admin_bp
from app.admin.auth import require_admin


@admin_bp.route("/admin/leads", methods=["GET"], endpoint="leads_panel")
@require_admin
def leads_panel():
    return redirect(url_for("leads_admin.index_view"))


@admin_bp.route("/admin/leads/reject-empty-phone", methods=["POST"])
@require_admin
def reject_empty_phone_leads():
    return redirect(url_for("leads_admin.index_view"))
