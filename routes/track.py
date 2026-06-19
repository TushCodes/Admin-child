"""Public shipment tracking routes and proof-of-delivery download handling."""

import logging
import re
from flask import Blueprint, render_template, request
from app.controllers.responses import json_error
from services.dashboard_api import (
    DashboardAPIError,
    fetch_consignment,
    fetch_consignment_pod_response,
)

logger = logging.getLogger(__name__)

track_bp = Blueprint("track", __name__)

CONSIGNMENT_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9]{1,16}$")


@track_bp.route("/track", methods=["GET", "POST"])
def track_page():
    """Show the tracking form and display a matching consignment when found."""
    consignment = None
    error_message = None

    if request.method == "POST":
        number = (request.form.get("consignment_number") or "").strip().upper()

        if not number:
            error_message = "Please enter a consignment number."
            logger.warning("Rejected empty consignment lookup request")
        elif not CONSIGNMENT_NUMBER_PATTERN.fullmatch(number):
            error_message = "Invalid consignment number format."
            logger.warning("Rejected invalid consignment number: %s", number)
        else:
            logger.info("Track lookup received for consignment %s", number)
            try:
                consignment = fetch_consignment(number)

                if consignment:
                    logger.info("Shipment found for consignment %s", number)
                else:
                    logger.info("Shipment not found for consignment %s", number)
                    error_message = (
                        "Consignment not found. Please check the number and try again."
                    )
            except DashboardAPIError as error:
                if error.status_code == 404:
                    logger.info("Shipment not found for consignment %s", number)
                    error_message = (
                        "Consignment not found. Please check the number and try again."
                    )
                else:
                    logger.error(
                        "Dashboard API error while tracking %s: %s", number, error
                    )
                    error_message = (
                        "Unable to load tracking data. Please try again later."
                    )
            except Exception:
                logger.exception("Unexpected error while tracking %s", number)
                error_message = "An unexpected error occurred. Please try again."

    return render_template(
        "track/track.html",
        consignment=consignment,
        error_message=error_message,
    )


@track_bp.route(
    "/track/pod/<consignment_number>", methods=["GET"], endpoint="consignment_pod"
)
def consignment_pod(consignment_number):
    """Serve the POD for a consignment identified by number without signed URLs."""
    try:
        number = (consignment_number or "").strip().upper()
        if not number:
            return json_error("Consignment number required.", 400)

        try:
            return fetch_consignment_pod_response(number)
        except DashboardAPIError as error:
            if error.status_code == 404:
                return json_error("No POD found.", 404)
            logger.error("Dashboard API error while serving POD %s: %s", number, error)
            return json_error("Unable to load POD data.", 503)
    except Exception:
        logger.exception("Failed to serve POD for consignment %s", consignment_number)
        return json_error("Failed to serve POD.", 500)
