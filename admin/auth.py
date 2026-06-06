"""Supabase-backed authentication utilities for the admin module.

Environment variables
---------------------
SECRET_KEY                Flask session signing key (required by app config).
SUPABASE_URL              Supabase project URL.
SUPABASE_AUTH_KEY         Preferred key for Supabase Auth sign-ins.
SUPABASE_ANON_KEY         Fallback Supabase anon key for Auth sign-ins.
SUPABASE_KEY              Legacy/shared fallback key already used elsewhere.
ADMIN_AUTH_PROVIDER       ``supabase`` (default when configured) or ``local``.
ADMIN_USERNAME            Local-development fallback username (default: admin).
ADMIN_PASSWORD            Local-development fallback password (default in dev: admin-pass).
ADMIN_PASSWORD_HASH       Local-development fallback password hash.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from flask import session
from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)

ADMIN_SESSION_KEY = "admin_authenticated"
ADMIN_SESSION_USERNAME_KEY = "admin_username"
ADMIN_SESSION_USER_ID_KEY = "admin_user_id"
ADMIN_SESSION_ACCESS_TOKEN_KEY = "admin_supabase_access_token"
ADMIN_SESSION_REFRESH_TOKEN_KEY = "admin_supabase_refresh_token"
ADMIN_SESSION_EXPIRES_AT_KEY = "admin_supabase_expires_at"
ADMIN_SESSION_PROVIDER_KEY = "admin_auth_provider"


@dataclass(slots=True)
class AdminAuthResult:
    """Normalized authentication result stored in the Flask session."""

    provider: str
    username: str
    user_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: int | None = None


class AdminAuthenticationError(Exception):
    """Raised when configured admin authentication cannot be attempted."""


def _is_development() -> bool:
    return os.getenv("FLASK_ENV", "").strip().lower() == "development"


def _get_supabase_auth_key() -> str:
    return (
        os.getenv("SUPABASE_AUTH_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
    )


def is_supabase_auth_configured() -> bool:
    """Return True when the environment can authenticate with Supabase Auth."""
    return bool(os.getenv("SUPABASE_URL", "").strip() and _get_supabase_auth_key())


def get_admin_auth_provider() -> str:
    """Return the configured admin auth provider.

    Supabase is selected automatically when Supabase Auth variables are present.
    Development keeps a local fallback so the login flow remains runnable without
    a cloud project.
    """
    configured = os.getenv("ADMIN_AUTH_PROVIDER", "").strip().lower()
    if configured:
        return configured
    return "supabase" if is_supabase_auth_configured() else "local"


def _get_local_admin_username() -> str:
    return (os.environ.get("ADMIN_USERNAME") or "admin").strip() or "admin"


def _get_local_admin_password_hash() -> str:
    password_hash = (os.environ.get("ADMIN_PASSWORD_HASH") or "").strip()
    password_plain = (os.environ.get("ADMIN_PASSWORD") or "").strip()

    if password_hash:
        return password_hash

    if password_plain or _is_development():
        from werkzeug.security import generate_password_hash

        fallback_password = password_plain or "admin-pass"
        if not password_plain:
            logger.warning(
                "ADMIN_PASSWORD_HASH not set; using development default password (admin-pass)."
            )
        return generate_password_hash(fallback_password)

    raise AdminAuthenticationError(
        "ADMIN_PASSWORD_HASH is required for local admin authentication."
    )


def _authenticate_local(username: str, password: str) -> AdminAuthResult | None:
    if username != _get_local_admin_username():
        return None

    password_plain = (os.environ.get("ADMIN_PASSWORD") or "").strip()
    if password_plain and password == password_plain:
        return AdminAuthResult(provider="local", username=username)

    try:
        if check_password_hash(_get_local_admin_password_hash(), password):
            return AdminAuthResult(provider="local", username=username)
    except Exception:
        logger.exception("Local admin password verification failed")

    return None


def _get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = _get_supabase_auth_key()
    if not supabase_url or not supabase_key:
        raise AdminAuthenticationError(
            "SUPABASE_URL and SUPABASE_AUTH_KEY/SUPABASE_ANON_KEY are required "
            "for Supabase admin authentication."
        )

    try:
        from supabase import create_client
    except ImportError as error:
        raise AdminAuthenticationError("The supabase package is not installed.") from error

    return create_client(supabase_url, supabase_key)


def _read_attr(value: Any, name: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _authenticate_supabase(email: str, password: str) -> AdminAuthResult | None:
    client = _get_supabase_client()
    try:
        response = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception:
        logger.warning("Supabase admin login failed for email: %s", email, exc_info=True)
        return None

    user = _read_attr(response, "user")
    auth_session = _read_attr(response, "session")
    if not user or not auth_session:
        return None

    access_token = _read_attr(auth_session, "access_token")
    refresh_token = _read_attr(auth_session, "refresh_token")
    expires_at = _read_attr(auth_session, "expires_at")
    expires_in = _read_attr(auth_session, "expires_in")
    if expires_at is None and expires_in is not None:
        try:
            expires_at = int(time.time()) + int(expires_in)
        except (TypeError, ValueError):
            expires_at = None

    return AdminAuthResult(
        provider="supabase",
        username=_read_attr(user, "email", email) or email,
        user_id=_read_attr(user, "id"),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=int(expires_at) if expires_at is not None else None,
    )


def authenticate_admin(username: str, password: str) -> AdminAuthResult | None:
    """Authenticate an admin with Supabase Auth, with a dev-only local fallback."""
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        return None

    provider = get_admin_auth_provider()
    if provider == "supabase":
        result = _authenticate_supabase(username, password)
        if result:
            return result
        local_fallback_disabled = (
            os.getenv("SUPABASE_AUTH_DISABLE_LOCAL_FALLBACK", "")
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
        )
        if _is_development() and not local_fallback_disabled:
            logger.info(
                "Falling back to local development admin credentials after "
                "Supabase login failure."
            )
            return _authenticate_local(username, password)
        return None

    if provider == "local":
        return _authenticate_local(username, password)

    raise AdminAuthenticationError(
        f"Unsupported ADMIN_AUTH_PROVIDER={provider!r}; expected 'supabase' or 'local'."
    )


def check_admin_credentials(username: str, password: str) -> bool:
    """Return True when credentials authenticate the admin user."""
    return authenticate_admin(username, password) is not None


def login_admin(
    username: str | None = None, auth_result: AdminAuthResult | None = None
) -> None:
    """Mark the current session as authenticated admin."""
    if auth_result is None:
        auth_result = AdminAuthResult(provider="local", username=username or "")

    session[ADMIN_SESSION_KEY] = True
    session[ADMIN_SESSION_PROVIDER_KEY] = auth_result.provider
    if auth_result.username:
        session[ADMIN_SESSION_USERNAME_KEY] = auth_result.username
    if auth_result.user_id:
        session[ADMIN_SESSION_USER_ID_KEY] = auth_result.user_id
    if auth_result.access_token:
        session[ADMIN_SESSION_ACCESS_TOKEN_KEY] = auth_result.access_token
    if auth_result.refresh_token:
        session[ADMIN_SESSION_REFRESH_TOKEN_KEY] = auth_result.refresh_token
    if auth_result.expires_at:
        session[ADMIN_SESSION_EXPIRES_AT_KEY] = auth_result.expires_at


def logout_admin() -> None:
    """Clear admin authentication state from session."""
    session.pop(ADMIN_SESSION_KEY, None)
    session.pop(ADMIN_SESSION_USERNAME_KEY, None)
    session.pop(ADMIN_SESSION_USER_ID_KEY, None)
    session.pop(ADMIN_SESSION_ACCESS_TOKEN_KEY, None)
    session.pop(ADMIN_SESSION_REFRESH_TOKEN_KEY, None)
    session.pop(ADMIN_SESSION_EXPIRES_AT_KEY, None)
    session.pop(ADMIN_SESSION_PROVIDER_KEY, None)


def is_admin_authenticated() -> bool:
    """Return True when current session is authenticated as admin."""
    if not session.get(ADMIN_SESSION_KEY):
        return False

    provider = session.get(ADMIN_SESSION_PROVIDER_KEY)
    if provider != "supabase":
        return True

    expires_at = session.get(ADMIN_SESSION_EXPIRES_AT_KEY)
    if not expires_at:
        return bool(session.get(ADMIN_SESSION_ACCESS_TOKEN_KEY))

    try:
        # Leave a small buffer to avoid treating nearly expired sessions as valid.
        return int(expires_at) > int(time.time()) + 30
    except (TypeError, ValueError):
        return False
