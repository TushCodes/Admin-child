"""Client helpers for reading shipment data through the dashboard API."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from urllib.parse import quote, urljoin

import requests
from flask import current_app

logger = logging.getLogger(__name__)


class DashboardAPIError(Exception):
    """Raised when the dashboard API cannot return usable data."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def _internal_api_token():
    return (
        current_app.config.get("ADMIN_DASHBOARD_API_TOKEN")
        or current_app.config.get("SECRET_KEY")
        or ""
    )


def _objectify(value):
    """Convert API dictionaries to attribute-friendly objects for templates."""
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _objectify(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_objectify(item) for item in value]
    return value


def _request_dashboard_api(path):
    """Call the configured dashboard API and return decoded JSON."""
    headers = {
        "Accept": "application/json",
        "X-Internal-Dashboard-API": _internal_api_token(),
    }
    base_url = (current_app.config.get("ADMIN_DASHBOARD_API_BASE_URL") or "").strip()

    if base_url:
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        response = requests.get(url, headers=headers, timeout=10)
    else:
        response = current_app.test_client().get(path, headers=headers)

    try:
        payload = (
            response.get_json() if hasattr(response, "get_json") else response.json()
        )
    except ValueError as error:
        raise DashboardAPIError("Dashboard API returned invalid JSON.") from error

    if response.status_code >= 400:
        message = "Dashboard API request failed."
        if isinstance(payload, dict):
            message = payload.get("message") or message
        raise DashboardAPIError(message, status_code=response.status_code)

    if not isinstance(payload, dict) or not payload.get("success"):
        raise DashboardAPIError("Dashboard API returned an unsuccessful response.")

    return payload


def fetch_consignment(consignment_number):
    """Fetch one consignment by number through the dashboard API."""
    number = (consignment_number or "").strip().upper()
    if not number:
        return None

    payload = _request_dashboard_api(
        f"/admin/api/consignments/{quote(number, safe='')}"
    )
    return _objectify(payload.get("data"))
