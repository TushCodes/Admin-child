import logging
from flask import redirect, request, url_for
from app.controllers.responses import json_error, json_success

from app import limiter
from app.admin import admin_bp
from app.admin.auth import require_admin
from app.services.consignment_service import (
    validate_and_normalize_rows,
    apply_consignment_changes,
)
from app.services.pod_storage import (
    store_pod_bytes as _store_pod_bytes,
    delete_pod_file as _delete_pod_file,
)
from app.services.logistics import (
    normalize_consignment_number,
    normalize_indian_pincode,
    normalize_status,
)

logger = logging.getLogger(__name__)


def _get_consignment_handles():
    from app.controllers.consignment_controller import Consignment, db

    return Consignment, db


@admin_bp.route("/admin/consignments", methods=["GET"], endpoint="consignments_panel")
@require_admin
def consignments_panel():
    return redirect(url_for("consignments_admin.index_view"))


@admin_bp.route(
    "/admin/consignments/list", methods=["GET"], endpoint="consignments_list_api"
)
@require_admin
def consignments_list_api():
    return redirect(url_for("consignments_admin.index_view"))


@admin_bp.route(
    "/admin/consignments/save", methods=["POST"], endpoint="consignments_save"
)
@limiter.limit("25 per minute")
@require_admin
def consignments_save():
    Consignment, db = _get_consignment_handles()
    payload = request.get_json(silent=True) or {}
    rows = payload.get("rows", [])
    deleted_ids = payload.get("deleted_ids", [])

    if not isinstance(rows, list) or not isinstance(deleted_ids, list):
        return json_error("Invalid request payload.", 400)

    try:
        validated_rows, validated_deleted_ids, errors = validate_and_normalize_rows(
            rows,
            deleted_ids,
            normalize_consignment_number,
            normalize_status,
            normalize_indian_pincode,
        )

        if errors:
            try:
                db.session.rollback()
            except Exception:
                logger.exception(
                    "Failed to rollback DB session after validation errors"
                )
            return json_error("Validation failed.", 400, errors=errors)

        try:
            deleted_count, total = apply_consignment_changes(
                validated_rows,
                validated_deleted_ids,
                Consignment=Consignment,
                db=db,
                store_pod_bytes_func=_store_pod_bytes,
                delete_pod_file_func=_delete_pod_file,
            )
        except ValueError as error:
            try:
                db.session.rollback()
            except Exception:
                logger.exception(
                    "Failed to rollback DB session after value error in save"
                )
            return json_error(str(error), 400)

        return json_success(
            {
                "message": "Sheet saved successfully.",
                "deleted_count": deleted_count,
                "total": total,
            }
        )

    except Exception:
        try:
            db.session.rollback()
        except Exception:
            logger.exception(
                "Failed to rollback DB session after unexpected error in save"
            )
        logger.exception("Unexpected error in admin save")
        return json_error("An unexpected error occurred. Please try again.", 500)
