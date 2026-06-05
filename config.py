"""Application configuration values."""

import logging
import os

logger = logging.getLogger(__name__)


def _is_development() -> bool:
    return os.getenv("FLASK_ENV", "").strip().lower() == "development"


def _resolve_secret_key() -> str:
    configured = os.environ.get("SECRET_KEY", "").strip()
    if configured:
        return configured

    if _is_development():
        logger.warning(
            "SECRET_KEY is not set; using a development-only fallback key. "
            "Set SECRET_KEY in production."
        )
        return "dev-local-secret-key-change-me"

    raise RuntimeError(
        "SECRET_KEY is required and must be set in environment variables."
    )


SECRET_KEY = _resolve_secret_key()
