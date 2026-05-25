import logging
from flask import render_template, request
from app.controllers.responses import json_error, json_success
from app.controllers.serializers import serialize_consignment

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
    Consignment, _ = _get_consignment_handles()
    consignments = Consignment.query.order_by(Consignment.id.asc()).all()
    return render_template(
        "admin/consignments.html",
        consignments=[serialize_consignment(row) for row in consignments],
    )


@admin_bp.route(
    "/admin/consignments/list", methods=["GET"], endpoint="consignments_list_api"
)
@require_admin
def consignments_list_api():
    Consignment, _ = _get_consignment_handles()

    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(1, min(100, int(request.args.get("per_page", 10))))
    except (TypeError, ValueError):
        per_page = 10

    search = (request.args.get("search") or "").strip()
    sort_by = (request.args.get("sort_by") or "id").strip()
    sort_order = (request.args.get("sort_order") or "asc").strip().lower()

    from app.services.consignment_repo import list_paginated

    rows, total, _, _, _ = list_paginated(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    payload_rows = [
        {
            "id": row.id,
            "consignment_number": row.consignment_number,
            "status": row.status,
            "pickup_pincode": row.pickup_pincode,
            "pickup_address": row.pickup_address,
            "pickup_tag": row.pickup_tag,
            "pickup_date": row.pickup_date,
            "drop_pincode": row.drop_pincode,
            "drop_address": row.drop_address,
            "drop_tag": row.drop_tag,
            "drop_date": row.drop_date,
            "eta": row.eta,
            "pod_image": row.pod_image,
        }
        for row in rows
    ]

    return json_success({"rows": payload_rows, "total": total})


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
