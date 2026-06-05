"""Database URL validation and SQLAlchemy engine configuration helpers."""

import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def require_database_uri():
    """Require a PostgreSQL DATABASE_URL for production, allow SQLite in development."""
    database_uri = os.getenv("DATABASE_URL", "").strip()
    if not database_uri:
        if os.getenv("FLASK_ENV", "").strip().lower() == "development":
            return "postgresql://admin_child:admin_child@127.0.0.1:5432/admin_child"
        raise RuntimeError("DATABASE_URL is required. SQLite is no longer supported.")

    if database_uri.startswith("sqlite://"):
        if os.getenv("FLASK_ENV", "").strip().lower() == "development":
            return database_uri
        raise RuntimeError("SQLite is only supported for development testing.")

    database_uri = normalize_postgres_uri(database_uri)

    if not database_uri.startswith("postgresql://"):
        raise RuntimeError("DATABASE_URL must be a PostgreSQL URL (postgresql://...).")

    return database_uri


def normalize_postgres_uri(database_uri):
    """Normalize postgres URIs and enforce SSL for Supabase hosts."""
    # Some platforms expose postgres:// which SQLAlchemy does not accept.
    if database_uri.startswith("postgres://"):
        database_uri = database_uri.replace("postgres://", "postgresql://", 1)

    parsed_uri = urlparse(database_uri)
    hostname = (parsed_uri.hostname or "").lower()

    if "supabase.com" in hostname:
        query_params = dict(parse_qsl(parsed_uri.query, keep_blank_values=True))
        query_params.setdefault("sslmode", "require")
        parsed_uri = parsed_uri._replace(query=urlencode(query_params))
        database_uri = urlunparse(parsed_uri)

    return database_uri


def build_engine_options(database_uri, get_env_bool, get_env_int):
    """Return SQLAlchemy engine settings appropriate for SQLite or PostgreSQL."""
    if database_uri.startswith("sqlite://"):
        return {
            "pool_pre_ping": False,
        }

    return {
        # Supabase/Render-safe defaults; overridable via env vars.
        "pool_pre_ping": get_env_bool("DB_POOL_PRE_PING", True),
        "pool_recycle": get_env_int("DB_POOL_RECYCLE", 180),
        "pool_size": get_env_int("DB_POOL_SIZE", 3),
        "max_overflow": get_env_int("DB_MAX_OVERFLOW", 2),
        "pool_timeout": get_env_int("DB_POOL_TIMEOUT", 30),
        "connect_args": {
            "connect_timeout": get_env_int("DB_CONNECT_TIMEOUT", 10),
        },
    }
