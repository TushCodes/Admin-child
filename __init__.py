"""Application package marker used when the project is imported as ``app``."""

from flask import (
    Flask,
    send_from_directory,
    request,
    jsonify,
)
from jinja2 import ChoiceLoader, FileSystemLoader
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
from cachelib import FileSystemCache
from functools import wraps
from importlib import import_module
import hashlib
import os
import logging
from sqlalchemy import text

if __name__ != "app":
    # Pytest may import this repository-level __init__ module by filename.
    # Mark it as package-like before aliasing it to `app` so absolute imports
    # such as `app.routes` still resolve.
    __path__ = [os.path.dirname(__file__)]
    sys.modules.setdefault("app", sys.modules[__name__])

from app.frontend import STATIC_FOLDER, TEMPLATE_FOLDER
from app.admin import TEMPLATE_FOLDER as ADMIN_TEMPLATE_FOLDER
from app.admin.models import db as models_db
from app.admin.db.maintenance import ensure_consignment_columns_async

# Configure logging
logging.basicConfig(
    level=getattr(
        logging, os.getenv("LOG_LEVEL", "INFO").strip().upper(), logging.INFO
    ),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _resolve_rate_limit_storage_uri():
    configured = os.getenv("RATELIMIT_STORAGE_URI", "").strip()
    if configured:
        return configured

    redis_url = os.getenv("REDIS_URL", "").strip()
    if redis_url:
        return redis_url

    return "memory://"


def _get_env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _get_env_int(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning(
            "Invalid integer for %s: %s. Using default %s", name, raw, default
        )
        return default


from app.admin.db.config import require_database_uri, build_engine_options
from app.admin.db.seed import seed_development_data
from app.middleware import register_middleware


# Simple cache shim exposing `cached(timeout=...)` decorator.
class SimpleCache:
    def __init__(self, cache_dir="flask_cache", default_timeout=300):
        self._cache = FileSystemCache(cache_dir)
        self.default_timeout = default_timeout

    def _make_key(self):
        key = request.path
        if request.query_string:
            key += "?" + request.query_string.decode()
        return hashlib.sha1(key.encode("utf-8")).hexdigest()

    def cached(self, timeout=None):
        def decorator(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                try:
                    cache_key = self._make_key()
                    cached_value = self._cache.get(cache_key)
                    if cached_value is not None:
                        return cached_value

                    result = func(*args, **kwargs)
                    self._cache.set(cache_key, result, timeout or self.default_timeout)
                    return result

                except Exception as error:
                    logger.error(f"Cache error: {error}")
                    return func(*args, **kwargs)

            return wrapped

        return decorator


# cache instance
cache = SimpleCache()

# limiter instance shared across the application
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=_resolve_rate_limit_storage_uri(),
)


def _load_env_file(path):
    """Load simple KEY=VALUE pairs from a local env file if it exists."""
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def _should_load_local_env_files():
    # Render injects env vars directly; avoid reading local files in production by default.
    if _get_env_bool("LOAD_LOCAL_ENV_FILES", False):
        return True
    return os.getenv("FLASK_ENV", "").strip().lower() != "production"


def _should_auto_create_tables():
    if os.getenv("FLASK_ENV", "").strip().lower() == "production":
        if _get_env_bool("AUTO_CREATE_TABLES", False):
            logger.warning(
                "Ignoring AUTO_CREATE_TABLES in production; manage schema externally."
            )
        return False

    return _get_env_bool("AUTO_CREATE_TABLES", default=True)


if _should_load_local_env_files():
    _load_env_file(".env.local")
    _load_env_file(".env")


def create_app():
    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_FOLDER),
        static_folder=str(STATIC_FOLDER),
    )
    app.jinja_loader = ChoiceLoader(
        [
            FileSystemLoader(str(ADMIN_TEMPLATE_FOLDER)),
            app.jinja_loader,
        ]
    )
    # Log effective PORT so platform startup probes can be debugged in deployment logs.
    try:
        effective_port = os.getenv("PORT", "10000")
        logger.info("STARTUP: effective PORT=%s", effective_port)
    except Exception:
        logger.exception("Failed to log STARTUP port")

    # DATABASE CONFIG
    database_uri = require_database_uri()
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["SESSION_COOKIE_SECURE"] = _get_env_bool(
        "SESSION_COOKIE_SECURE",
        default=os.getenv("FLASK_ENV", "").strip().lower() == "production",
    )
    app.config["PREFERRED_URL_SCHEME"] = (
        "https"
        if os.getenv("FLASK_ENV", "").strip().lower() == "production"
        else "http"
    )
    app.config["FRONTEND_API_BASE_URL"] = os.getenv("FRONTEND_API_BASE_URL", "")

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = build_engine_options(
        database_uri, _get_env_bool, _get_env_int
    )

    app.config["RATELIMIT_STORAGE_URI"] = _resolve_rate_limit_storage_uri()
    app.config["RATELIMIT_HEADERS_ENABLED"] = True
    app.config.from_object("app.config")

    models_db.init_app(app)
    limiter.init_app(app)
    register_middleware(app)

    auto_create_tables = _should_auto_create_tables()
    if auto_create_tables:
        try:
            if not app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite://"):
                ensure_consignment_columns_async(
                    app.config["SQLALCHEMY_DATABASE_URI"], logger
                )
        except Exception:
            logger.exception("Failed to start consignment schema repair")

        with app.app_context():
            models_db.create_all()
            seed_development_data(models_db, app)
    else:
        try:
            if not app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite://"):
                ensure_consignment_columns_async(
                    app.config["SQLALCHEMY_DATABASE_URI"], logger
                )
        except Exception:
            logger.exception("Failed to start consignment schema repair")

        logger.info("AUTO_CREATE_TABLES disabled. Skipping db.create_all() at startup.")
        logger.info("Consignment schema repair runs asynchronously in production.")

    from app.routes.main import main_bp
    from app.routes.track import track_bp
    from app.routes.pages import pages_bp
    from app.admin import admin_bp, register_admin_routes
    from app.admin.flask_admin_setup import init_flask_admin
    import_module("app.admin.routes.admin.auth_routes")
    import_module("app.admin.api.dashboard")

    register_admin_routes()
    app.register_blueprint(main_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(admin_bp)

    try:
        init_flask_admin(app)
    except Exception:
        logger.exception(
            "Flask-Admin failed to initialize; continuing without admin UI"
        )

    @app.route("/health")
    def health():
        return (
            jsonify(
                {
                    "status": "ok",
                    "message": "Application is healthy",
                }
            ),
            200,
        )

    @app.route("/health/db")
    def database_health():
        try:
            models_db.session.execute(text("SELECT 1"))
            return (
                jsonify(
                    {
                        "status": "ok",
                        "database": "postgresql",
                        "message": "Database connection is healthy",
                    }
                ),
                200,
            )
        except Exception as error:
            logger.error("Database health check failed: %s", error)
            return (
                jsonify(
                    {
                        "status": "error",
                        "database": "postgresql",
                        "message": "Database connection failed",
                    }
                ),
                503,
            )

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(app.static_folder, "favicon.ico")

    return app
