import logging
from flask import render_template, request
from app.utils.response import json_error, json_success
from sqlalchemy.exc import DatabaseError, OperationalError, ProgrammingError

from app import limiter
from app.admin import admin_bp
from app.admin.auth import require_admin
from app.services.consignment_service import validate_and_normalize_rows, apply_consignment_changes
from app.services.pod_storage import store_pod_bytes as _store_pod_bytes, delete_pod_file as _delete_pod_file
from app.utils.errors import is_missing_column_error as _is_missing_column_error
from app.services.logistics import (
    normalize_consignment_number,
    normalize_indian_pincode,
    normalize_status,
)

logger = logging.getLogger(__name__)


def _get_consignment_handles():
    from app.admin import consignment_controller

    return consignment_controller.Consignment, consignment_controller.db


# `_is_missing_column_error` is imported from `app.utils.errors` to centralize
# database schema-related error detection.


@admin_bp.route("/admin/consignments", methods=["GET"], endpoint="consignments_panel")
@require_admin
def consignments_panel():
    try:
        # Delegate DB and data-shaping logic to the controller.
        from app.admin.consignment_controller import get_panel_rows

        rows, total, large = get_panel_rows()
        if large:
            logger.info("consignments_panel: large table detected (total=%d); rendering empty sample and deferring to API", total)

        return render_template(
            "admin/consignments.html",
            consignments=rows,
        )
    except ProgrammingError as error:
        try:
            # Attempt rollback on DB programming errors; controller used DB directly.
            Consignment, db = _get_consignment_handles()
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session after programming error")
        if _is_missing_column_error(error):
            logger.exception("Schema mismatch loading admin panel")
            return render_template(
                "admin/consignments.html",
                consignments=[],
                error="Database schema needs an update. Missing consignment fields.",
            )

        logger.exception("Database error loading admin panel")
        return render_template(
            "admin/consignments.html",
            consignments=[],
            error="Unable to load data. Please try again.",
        )
    except (OperationalError, DatabaseError):
        logger.exception("Database error loading admin panel")
        return render_template(
            "admin/consignments.html",
            consignments=[],
            error="Unable to load data. Please try again.",
        )
    except Exception:
        logger.exception("Unexpected error in admin panel")
        return render_template(
            "admin/consignments.html",
            consignments=[],
            error="An unexpected error occurred.",
        )


@admin_bp.route("/admin/consignments/list", methods=["GET"], endpoint="consignments_list_api")
@require_admin
def consignments_list_api():
    try:
        # Delegate DB access + pagination to controller helper
        from app.admin.consignment_controller import get_list_rows

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "", type=str).strip()
        sort_by = request.args.get("sort_by", "id", type=str)
        sort_order = request.args.get("sort_order", "asc", type=str)

        rows, paginated = get_list_rows(page=page, per_page=per_page, search=search, sort_by=sort_by, sort_order=sort_order)

        return render_template(
            "admin/consignments.html",
            consignments=rows,
        )

    except ProgrammingError as error:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session after programming error in API")
        if _is_missing_column_error(error):
            logger.exception("Schema mismatch in consignments API")
            return json_error("Database schema needs an update. Missing consignment fields.", 500)

        logger.exception("Database error in consignments API")
        return json_error("Unable to load data. Please try again.", 500)
    except (OperationalError, DatabaseError):
        try:
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session after DB error in API")
        logger.exception("Database error in consignments API")
        return json_error("Database connection error. Please try again.", 500)
    except Exception:
        logger.exception("Unexpected error in consignments API")
        return json_error("An unexpected error occurred.", 500)


@admin_bp.route("/admin/consignments/save", methods=["POST"], endpoint="consignments_save")
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
                logger.exception("Failed to rollback DB session after validation errors")
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
                logger.exception("Failed to rollback DB session after value error in save")
            return json_error(str(error), 400)

        return json_success({
            "message": "Sheet saved successfully.",
            "deleted_count": deleted_count,
            "total": total,
        })

    except Exception:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session after unexpected error in save")
        logger.exception("Unexpected error in admin save")
        return json_error("An unexpected error occurred. Please try again.", 500)
