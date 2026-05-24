"""Admin leads routes (thin) using leads_controller for data operations."""

import logging
from flask import render_template, flash, redirect, url_for
from app.admin import admin_bp
from app.admin.auth import require_admin
from app.controllers.leads_controller import get_leads, delete_empty_phone_leads
from app.utils.db import transaction

logger = logging.getLogger(__name__)


@admin_bp.route("/admin/leads", methods=["GET"], endpoint="leads_panel")
@require_admin
def leads_panel():
    try:
        rows = get_leads()
        return render_template("admin/leads.html", leads=rows)
    except Exception as e:
        logger.error("Unexpected error loading leads panel: %s", e)
        return render_template(
            "admin/leads.html", leads=[], error="An unexpected error occurred."
        )


@admin_bp.route("/admin/leads/reject-empty-phone", methods=["POST"])
@require_admin
def reject_empty_phone_leads():
    try:
        from app.models import db

        with transaction(db):
            deleted_count = delete_empty_phone_leads(db)

        flash(f"Rejected {deleted_count} lead(s) with empty phone numbers.", "success")
        logger.info(
            "Rejected %s lead(s) with empty phone numbers from admin panel",
            deleted_count,
        )
    except Exception as e:
        logger.error("Failed to reject blank-phone leads: %s", e, exc_info=True)
        flash("Unable to reject blank-phone leads right now.", "error")

    return redirect(url_for("admin.leads_panel"))
