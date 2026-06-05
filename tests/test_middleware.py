import importlib.util
import os
import sys
from pathlib import Path

from flask import request

ROOT = Path(__file__).resolve().parents[1]


def _load_app(tmp_path):
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'middleware.db'}"
    os.environ.setdefault("RATELIMIT_STORAGE_URI", "memory://")

    spec = importlib.util.spec_from_file_location("app", str(ROOT / "__init__.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = module
    spec.loader.exec_module(module)
    return module.create_app()


def test_request_and_security_headers_are_applied(tmp_path):
    app = _load_app(tmp_path)

    response = app.test_client().get("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
    assert "X-Response-Time-ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_admin_middleware_redirects_html_requests_to_login(tmp_path):
    app = _load_app(tmp_path)

    response = app.test_client().get("/admin/dashboard")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_middleware_returns_json_for_json_requests(tmp_path):
    app = _load_app(tmp_path)

    response = app.test_client().get(
        "/flask-admin/", headers={"Accept": "application/json"}
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "success": False,
        "message": "Authentication required",
    }


def test_error_handlers_use_shared_json_negotiation(tmp_path):
    app = _load_app(tmp_path)
    client = app.test_client()

    json_response = client.get("/missing", headers={"Accept": "application/json"})
    html_response = client.get("/missing", headers={"Accept": "text/html"})

    assert json_response.status_code == 404
    assert json_response.get_json() == {"error": "Resource not found"}
    assert html_response.status_code == 404
    assert html_response.mimetype == "text/html"


def test_wants_json_response_helper_negotiates_common_request_types(tmp_path):
    app = _load_app(tmp_path)
    from app.utils.content_negotiation import wants_json_response

    with app.test_request_context("/api/example", headers={"Accept": "text/html"}):
        assert wants_json_response(request) is True

    with app.test_request_context(
        "/admin/dashboard", headers={"Accept": "application/json"}
    ):
        assert wants_json_response(request) is True

    with app.test_request_context("/admin/dashboard", headers={"Accept": "text/html"}):
        assert wants_json_response(request) is False

    with app.test_request_context(
        "/admin/dashboard",
        method="POST",
        data='{"ok": true}',
        content_type="application/json",
    ):
        assert wants_json_response(request) is True
