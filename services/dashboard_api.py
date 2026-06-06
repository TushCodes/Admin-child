"""Website-side client helpers for reading shipment data through the admin API."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from urllib.parse import quote, urljoin

import requests
from flask import Response, current_app

logger = logging.getLogger(__name__)


class DashboardAPIError(Exception):
    """Raised when the admin API cannot return usable data."""

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


def _admin_api_headers(accept="application/json"):
    return {
        "Accept": accept,
        "X-Internal-Dashboard-API": _internal_api_token(),
    }


def _admin_api_url(path):
    base_url = (current_app.config.get("ADMIN_DASHBOARD_API_BASE_URL") or "").strip()
    if not base_url:
        return None
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _request_dashboard_api(path):
    """Call the configured admin API and return decoded JSON."""
    url = _admin_api_url(path)
    if url:
        response = requests.get(url, headers=_admin_api_headers(), timeout=10)
    else:
        response = current_app.test_client().get(path, headers=_admin_api_headers())

    try:
        payload = (
            response.get_json() if hasattr(response, "get_json") else response.json()
        )
    except ValueError as error:
        raise DashboardAPIError("Admin API returned invalid JSON.") from error

    if response.status_code >= 400:
        message = "Admin API request failed."
        if isinstance(payload, dict):
            message = payload.get("message") or message
        raise DashboardAPIError(message, status_code=response.status_code)

    if not isinstance(payload, dict) or not payload.get("success"):
        raise DashboardAPIError("Admin API returned an unsuccessful response.")

    return payload


def fetch_consignment(consignment_number):
    """Fetch one consignment by number through the admin API."""
    number = (consignment_number or "").strip().upper()
    if not number:
        return None

    payload = _request_dashboard_api(
        f"/admin/api/consignments/{quote(number, safe='')}"
    )
    return _objectify(payload.get("data"))


def fetch_consignment_pod_response(consignment_number):
    """Fetch one consignment POD through the admin API and return a Flask response."""
    number = (consignment_number or "").strip().upper()
    if not number:
        raise DashboardAPIError("Consignment number required.", status_code=400)

    path = f"/admin/api/consignments/{quote(number, safe='')}/pod"
    url = _admin_api_url(path)
    if url:
        response = requests.get(
            url,
            headers=_admin_api_headers(accept="*/*"),
            timeout=10,
        )
        if response.status_code >= 400:
            raise DashboardAPIError("Admin API POD request failed.", response.status_code)
        return Response(
            response.content,
            status=response.status_code,
            mimetype=response.headers.get("content-type"),
        )

    response = current_app.test_client().get(path, headers=_admin_api_headers("*/*"))
    if response.status_code >= 400:
        raise DashboardAPIError("Admin API POD request failed.", response.status_code)
    return response
