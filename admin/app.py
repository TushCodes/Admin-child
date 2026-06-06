"""Standalone Flask app factory for running the admin panel by itself."""

from __future__ import annotations

from importlib import import_module
import logging
import os
from pathlib import Path
import sys

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
from sqlalchemy import text

# Support `cd admin && python app.py` and `cd admin && flask --app app ...`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from admin import STATIC_FOLDER, TEMPLATE_FOLDER, admin_bp
from admin.db.config import build_engine_options, require_database_uri
from admin.db.maintenance import ensure_consignment_columns_async
from admin.db.seed import seed_development_data
from admin.db.session import register_database_middleware
from admin.extensions import limiter
from admin.flask_admin_setup import init_flask_admin
from admin.middleware.admin_auth import register_admin_auth_middleware
from admin.models import db

logger = logging.getLogger(__name__)


def _load_env_file(path: Path):
    """Load simple KEY=VALUE pairs from a local env file if it exists."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
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
        logger.warning("Invalid integer for %s: %s. Using default %s", name, raw, default)
        return default


def _resolve_secret_key():
    configured = os.getenv("SECRET_KEY", "").strip()
    if configured:
        return configured
    if os.getenv("FLASK_ENV", "").strip().lower() == "development":
        logger.warning("SECRET_KEY is not set; using a development-only fallback key.")
        return "dev-local-admin-secret-key-change-me"
    raise RuntimeError("SECRET_KEY is required for the standalone admin app.")


def _resolve_rate_limit_storage_uri():
    return (
        os.getenv("RATELIMIT_STORAGE_URI", "").strip()
        or os.getenv("REDIS_URL", "").strip()
        or "memory://"
    )


def _should_auto_create_tables():
    if os.getenv("FLASK_ENV", "").strip().lower() == "production":
        return _get_env_bool("AUTO_CREATE_TABLES", False)
    return _get_env_bool("AUTO_CREATE_TABLES", True)


def _bootstrap_standalone_environment():
    admin_root = Path(__file__).resolve().parent
    project_root = admin_root.parent
    os.environ.setdefault("FLASK_ENV", "development")
    _load_env_file(project_root / ".env.local")
    _load_env_file(project_root / ".env")
    _load_env_file(admin_root / ".env.local")
    _load_env_file(admin_root / ".env")

    if (
        os.getenv("FLASK_ENV", "").strip().lower() == "development"
        and not os.getenv("DATABASE_URL", "").strip()
    ):
        instance_dir = admin_root / "instance"
        instance_dir.mkdir(exist_ok=True)
        os.environ["DATABASE_URL"] = f"sqlite:///{instance_dir / 'admin.db'}"


def create_app():
    """Create a standalone admin-panel Flask application."""
    _bootstrap_standalone_environment()

    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_FOLDER),
        static_folder=str(STATIC_FOLDER),
        instance_path=str(Path(__file__).resolve().parent / "instance"),
    )
    app.config["SECRET_KEY"] = _resolve_secret_key()
    database_uri = require_database_uri()
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = build_engine_options(
        database_uri, _get_env_bool, _get_env_int
    )
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["SESSION_COOKIE_SECURE"] = _get_env_bool(
        "SESSION_COOKIE_SECURE",
        default=os.getenv("FLASK_ENV", "").strip().lower() == "production",
    )
    app.config["RATELIMIT_STORAGE_URI"] = _resolve_rate_limit_storage_uri()
    app.config["RATELIMIT_HEADERS_ENABLED"] = True

    db.init_app(app)
    limiter.init_app(app)
    register_database_middleware(app)
    register_admin_auth_middleware(app)

    if _should_auto_create_tables():
        try:
            if not database_uri.startswith("sqlite://"):
                ensure_consignment_columns_async(database_uri, logger)
        except Exception:
            logger.exception("Failed to start consignment schema repair")
        with app.app_context():
            db.create_all()
            seed_development_data(db, app)

    import_module("admin.routes.admin.auth_routes")
    import_module("admin.api.dashboard")
    app.register_blueprint(admin_bp)
    init_flask_admin(app)

    @app.route("/")
    def index():
        return render_template("admin/landing.html")

    @app.route("/admin")
    @app.route("/admin/")
    def admin_index():
        return redirect(url_for("admin.login"))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "admin"}), 200

    @app.route("/health/db")
    def database_health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as error:
            logger.error("Database health check failed: %s", error)
            return jsonify({"status": "error", "database": "unavailable"}), 503

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(app.static_folder, "favicon.ico")

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/admin/api/"):
            return jsonify({"success": False, "message": "Resource not found."}), 404
        return render_template("admin/landing.html", requested_path=request.path), 200

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    port = int(os.getenv("PORT", "5001"))
    debug = os.getenv("FLASK_ENV", "").strip().lower() != "production"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
