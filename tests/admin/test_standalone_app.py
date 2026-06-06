"""Tests for running the admin folder as a standalone Flask app."""

import importlib


def test_standalone_admin_app_registers_admin_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("SECRET_KEY", "standalone-test-secret")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'admin.db'}")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")

    standalone = importlib.import_module("admin.app")
    app = standalone.create_app()
    client = app.test_client()

    root_response = client.get("/")
    assert root_response.status_code == 200
    assert b"Gram SCS" in root_response.data
    assert b"Enter Admin Panel" in root_response.data

    missing_response = client.get("/not-a-real-page")
    assert missing_response.status_code == 200
    assert b"not-a-real-page" in missing_response.data

    admin_root_response = client.get("/admin")
    assert admin_root_response.status_code == 302
    assert admin_root_response.headers["Location"] == "/admin/login"

    login_response = client.get("/admin/login")
    assert login_response.status_code == 200

    dashboard_response = client.get("/admin/dashboard")
    assert dashboard_response.status_code == 302
    assert "/admin/login" in dashboard_response.headers["Location"]

    assert client.get("/health").status_code == 200
    assert client.get("/health/db").status_code == 200
