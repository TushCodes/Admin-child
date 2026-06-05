"""CORS middleware for browser-based frontend/API communication."""

import os

from flask import make_response, request

DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
DEFAULT_ALLOWED_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
DEFAULT_ALLOWED_HEADERS = "Content-Type, Authorization, X-Requested-With, X-Request-ID"


def _csv_config(name: str, default_values=()):
    raw = os.getenv(name, "").strip()
    if not raw:
        return tuple(default_values)
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _allowed_origin(origin: str | None, allowed_origins: tuple[str, ...]) -> str | None:
    if not origin:
        return None
    if "*" in allowed_origins:
        return origin
    if origin in allowed_origins:
        return origin
    return None


def register_cors_middleware(app):
    """Register CORS request/response handling.

    Configure with:
    - CORS_ORIGINS: comma-separated allowed origins. Defaults to common local
      frontend dev servers.
    - CORS_METHODS / CORS_HEADERS / CORS_MAX_AGE
    - CORS_SUPPORTS_CREDENTIALS: defaults to true so cookies work for admin APIs.
    """

    allowed_origins = _csv_config("CORS_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    allowed_methods = os.getenv("CORS_METHODS", DEFAULT_ALLOWED_METHODS)
    allowed_headers = os.getenv("CORS_HEADERS", DEFAULT_ALLOWED_HEADERS)
    max_age = os.getenv("CORS_MAX_AGE", "86400")
    supports_credentials = _env_bool("CORS_SUPPORTS_CREDENTIALS", True)

    app.config["CORS_ALLOWED_ORIGINS"] = allowed_origins

    @app.before_request
    def answer_cors_preflight():
        if request.method != "OPTIONS":
            return None

        response = make_response("", 204)
        return response

    @app.after_request
    def add_cors_headers(response):
        origin = _allowed_origin(request.headers.get("Origin"), allowed_origins)
        if not origin:
            return response

        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = allowed_methods
        response.headers["Access-Control-Allow-Headers"] = allowed_headers
        response.headers["Access-Control-Max-Age"] = max_age
        response.headers.setdefault("Vary", "Origin")
        if supports_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response
