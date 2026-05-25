"""Admin leads routes."""

from flask import redirect, render_template, url_for
from app.admin import admin_bp
from app.admin.auth import require_admin
from app.models import Lead, db


@admin_bp.route("/admin/leads", methods=["GET"], endpoint="leads_panel")
@require_admin
def leads_panel():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template("admin/leads.html", leads=leads, error=None)


@admin_bp.route("/admin/leads/reject-empty-phone", methods=["POST"])
@require_admin
def reject_empty_phone_leads():
    Lead.query.filter((Lead.phone.is_(None)) | (Lead.phone == "")).delete(
        synchronize_session=False
    )
    db.session.commit()
    return redirect(url_for("admin.leads_panel"))
