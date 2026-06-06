"""JSON APIs that expose admin dashboard data to trusted callers."""

import logging

from flask import current_app, request
from sqlalchemy.exc import DatabaseError, OperationalError

from app.admin import admin_bp
from app.admin.auth import is_admin_authenticated
from app.controllers.responses import json_error, json_success
from app.admin.controllers.serializers import serialize_consignment, serialize_lead
from app.admin.models import Consignment, Lead
from app.admin.services.pod_storage import send_pod_file_response

logger = logging.getLogger(__name__)


def _configured_internal_token():
    """Return the token accepted for same-application dashboard API calls."""
    return (
        current_app.config.get("ADMIN_DASHBOARD_API_TOKEN")
        or current_app.config.get("SECRET_KEY")
        or ""
    )


def _is_authorized_dashboard_api_request():
    """Allow logged-in admins or trusted internal server-side callers."""
    if is_admin_authenticated():
        return True

    expected_token = _configured_internal_token()
    supplied_token = request.headers.get("X-Internal-Dashboard-API", "")
    return bool(expected_token and supplied_token and supplied_token == expected_token)


def _require_dashboard_api_access():
    if not _is_authorized_dashboard_api_request():
        return json_error("Authentication required.", 401)
    return None


@admin_bp.route("/admin/api/dashboard-data", methods=["GET"])
def dashboard_data_api():
    """Return the consignment and lead data shown/stored in the admin dashboard."""
    access_error = _require_dashboard_api_access()
    if access_error:
        return access_error

    try:
        consignments = Consignment.query.order_by(Consignment.id.asc()).all()
        leads = Lead.query.order_by(Lead.id.asc()).all()
        return json_success(
            {
                "data": {
                    "consignments": [
                        serialize_consignment(consignment)
                        for consignment in consignments
                    ],
                    "leads": [serialize_lead(lead) for lead in leads],
                }
            }
        )
    except (OperationalError, DatabaseError):
        logger.exception("Database error while loading dashboard API data")
        return json_error("Unable to load dashboard data.", 503)
    except Exception:
        logger.exception("Unexpected error while loading dashboard API data")
        return json_error("Unable to load dashboard data.", 500)


@admin_bp.route("/admin/api/consignments/<consignment_number>", methods=["GET"])
def dashboard_consignment_api(consignment_number):
    """Return one consignment from dashboard data for tracking lookups."""
    access_error = _require_dashboard_api_access()
    if access_error:
        return access_error

    number = (consignment_number or "").strip().upper()
    if not number:
        return json_error("Consignment number required.", 400)

    try:
        consignment = Consignment.query.filter_by(consignment_number=number).first()
        if not consignment:
            return json_error("Consignment not found.", 404)

        return json_success({"data": serialize_consignment(consignment)})
    except (OperationalError, DatabaseError):
        logger.exception("Database error while loading consignment %s", number)
        return json_error("Unable to load consignment data.", 503)
    except Exception:
        logger.exception("Unexpected error while loading consignment %s", number)
        return json_error("Unable to load consignment data.", 500)


@admin_bp.route("/admin/api/consignments/<consignment_number>/pod", methods=["GET"])
def dashboard_consignment_pod_api(consignment_number):
    """Return the POD file for one consignment through the admin API."""
    access_error = _require_dashboard_api_access()
    if access_error:
        return access_error

    number = (consignment_number or "").strip().upper()
    if not number:
        return json_error("Consignment number required.", 400)

    try:
        consignment = Consignment.query.filter_by(consignment_number=number).first()
        if not consignment or not getattr(consignment, "pod_image", None):
            return json_error("No POD found.", 404)

        try:
            return send_pod_file_response(consignment.pod_image)
        except ValueError:
            return json_error("Invalid POD path.", 400)
        except FileNotFoundError:
            return json_error("POD file missing.", 404)
    except (OperationalError, DatabaseError):
        logger.exception("Database error while loading POD for consignment %s", number)
        return json_error("Unable to load POD data.", 503)
    except Exception:
        logger.exception("Unexpected error while loading POD for consignment %s", number)
        return json_error("Unable to load POD data.", 500)
