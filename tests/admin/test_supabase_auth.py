"""Tests for Supabase-backed admin authentication."""

from types import SimpleNamespace


def test_supabase_authentication_stores_session_metadata(app, monkeypatch):
    """Successful Supabase sign-ins are normalized and stored in Flask session."""
    from app.admin import auth

    class FakeSupabaseAuth:
        def sign_in_with_password(self, payload):
            assert payload == {"email": "owner@example.com", "password": "secret"}
            return SimpleNamespace(
                user=SimpleNamespace(email="owner@example.com", id="user-123"),
                session=SimpleNamespace(
                    access_token="access-token",
                    refresh_token="refresh-token",
                    expires_at=4_102_444_800,
                ),
            )

    monkeypatch.setenv("ADMIN_AUTH_PROVIDER", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_AUTH_KEY", "anon-key")
    monkeypatch.setattr(
        auth,
        "_get_supabase_client",
        lambda: SimpleNamespace(auth=FakeSupabaseAuth()),
    )

    auth_result = auth.authenticate_admin("owner@example.com", "secret")

    assert auth_result is not None
    assert auth_result.provider == "supabase"
    assert auth_result.username == "owner@example.com"
    assert auth_result.user_id == "user-123"

    with app.test_request_context("/"):
        auth.login_admin(auth_result=auth_result)
        assert auth.is_admin_authenticated() is True


def test_local_development_fallback_still_supports_admin_login(app, monkeypatch):
    """Local development remains usable when Supabase is not configured."""
    from app.admin import auth

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("ADMIN_AUTH_PROVIDER", "local")
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-pass")

    auth_result = auth.authenticate_admin("admin", "admin-pass")

    assert auth_result is not None
    assert auth_result.provider == "local"
    assert auth_result.username == "admin"
