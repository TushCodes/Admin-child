import logging
from flask import flash, redirect, request, send_file, url_for
from app.controllers.responses import json_error

from app.admin import admin_bp
from app.admin.auth import require_admin
from app.services.consignment_importer import (
    import_from_workbook,
    generate_import_template_bytes,
    export_rows_to_workbook_bytes,
)
from app.services.logistics import (
    normalize_consignment_number,
    normalize_indian_pincode,
    normalize_status,
)
from app.services.pdf_export import generate_consignment_pdf

logger = logging.getLogger(__name__)


def _get_consignment_handles():
    from app.controllers.consignment_controller import Consignment, db

    return Consignment, db


@admin_bp.route(
    "/admin/consignments/import", methods=["POST"], endpoint="consignments_import_excel"
)
@require_admin
def consignments_import_excel():
    Consignment, db = _get_consignment_handles()
    upload = request.files.get("file")
    if not upload or not upload.filename:
        flash("Please choose an Excel file (.xlsx).", "danger")
        return redirect(url_for("admin.consignments_panel"))

    filename = upload.filename.lower()
    if not filename.endswith(".xlsx"):
        flash("Only .xlsx files are supported.", "danger")
        return redirect(url_for("admin.consignments_panel"))

    try:
        added_count, skipped_count = import_from_workbook(
            upload,
            Consignment=Consignment,
            db=db,
            normalize_consignment_number=normalize_consignment_number,
            normalize_status=normalize_status,
            normalize_indian_pincode=normalize_indian_pincode,
        )

        flash(
            f"Import completed. Added: {added_count}, skipped duplicates: {skipped_count}.",
            "success",
        )
        return redirect(url_for("admin.consignments_panel"))
    except ValueError as error:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session after import error")
        flash(str(error), "danger")
        return redirect(url_for("admin.consignments_panel"))
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            logger.exception(
                "Failed to rollback DB session after unexpected import error"
            )
        logger.exception("Unexpected error in Excel import")
        flash("Failed to import Excel file.", "danger")
        return redirect(url_for("admin.consignments_panel"))


@admin_bp.route(
    "/admin/consignments/export.xlsx",
    methods=["GET"],
    endpoint="consignments_export_excel",
)
@require_admin
def consignments_export_excel():
    try:
        Consignment, _db = _get_consignment_handles()
        rows = Consignment.query.order_by(Consignment.id.asc()).all()
        output = export_rows_to_workbook_bytes(rows)

        return send_file(
            output,
            as_attachment=True,
            download_name="internal_consignments.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception:
        logger.exception("Excel export failed")
        return json_error("Failed to export Excel.")


@admin_bp.route(
    "/admin/consignments/export.pdf",
    methods=["GET"],
    endpoint="consignments_export_pdf",
)
@require_admin
def consignments_export_pdf():
    try:
        Consignment, _db = _get_consignment_handles()
        rows = Consignment.query.order_by(Consignment.id.asc()).all()
        output = generate_consignment_pdf(rows)

        return send_file(
            output,
            as_attachment=True,
            download_name="internal_consignments.pdf",
            mimetype="application/pdf",
        )
    except Exception:
        logger.exception("PDF export failed")
        return json_error("Failed to export PDF.")


@admin_bp.route(
    "/admin/consignments/import-template.xlsx",
    methods=["GET"],
    endpoint="consignments_import_template_excel",
)
@require_admin
def consignments_import_template_excel():
    try:
        output = generate_import_template_bytes()

        return send_file(
            output,
            as_attachment=True,
            download_name="internal_consignments_import_template.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception:
        logger.exception("Template export failed")
        return json_error("Failed to generate import template.")
