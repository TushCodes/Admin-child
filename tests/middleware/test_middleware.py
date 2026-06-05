from flask import request


def test_request_and_security_headers_are_applied(client):
    response = client.get("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
    assert "X-Response-Time-ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_admin_middleware_redirects_html_requests_to_login(client):
    response = client.get("/admin/dashboard")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_middleware_returns_json_for_json_requests(client):
    response = client.get("/flask-admin/", headers={"Accept": "application/json"})

    assert response.status_code == 401
    assert response.get_json() == {
        "success": False,
        "message": "Authentication required",
    }


def test_error_handlers_use_shared_json_negotiation(client):
    json_response = client.get("/missing", headers={"Accept": "application/json"})
    html_response = client.get("/missing", headers={"Accept": "text/html"})

    assert json_response.status_code == 404
    assert json_response.get_json() == {"error": "Resource not found"}
    assert html_response.status_code == 404
    assert html_response.mimetype == "text/html"


def test_wants_json_response_helper_negotiates_common_request_types(app):
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


def test_cors_middleware_allows_configured_frontend_origin(client):
    response = client.options(
        "/contact",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]


def test_database_middleware_commits_contact_writes(app, client):
    response = client.post(
        "/contact",
        data={
            "name": "Middleware User",
            "email": "middleware@example.com",
            "phone": "+1 555 0100",
            "subject": "Middleware",
            "message": "Please save through middleware.",
        },
    )

    assert response.status_code == 302
    from app.models import Lead

    with app.app_context():
        assert Lead.query.filter_by(email="middleware@example.com").count() == 1
