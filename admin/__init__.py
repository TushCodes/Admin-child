"""Admin panel package and blueprint definitions."""

from pathlib import Path

from importlib import import_module

from pathlib import Path

ADMIN_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = ADMIN_ROOT / "frontend" / "templates"
STATIC_FOLDER = ADMIN_ROOT / "frontend" / "static"

from flask import Blueprint, current_app, redirect, url_for
from importlib import import_module

ADMIN_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = ADMIN_ROOT / "frontend" / "templates"
STATIC_FOLDER = ADMIN_ROOT / "frontend" / "static"

admin_bp = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    static_url_path="/admin-assets",
)

# Allow route decorators to run even if the blueprint was referenced earlier
# (helps when loading standalone in varied import orders during local runs).
try:
    admin_bp._register_once = False
except Exception:
    pass

# Ensure `app.admin` points to this `admin` package for legacy imports.
import sys, types
if "app" not in sys.modules:
    app_mod = types.ModuleType("app")
    app_mod.__path__ = []
    sys.modules["app"] = app_mod
sys.modules.setdefault("app.admin", sys.modules.get(__name__, None) or import_module("admin"))
try:
    setattr(sys.modules["app"], "admin", sys.modules["app.admin"])
except Exception:
    pass
try:
    # Expose common symbols expected on the legacy `app` package.
    ext = import_module("admin.extensions")
    if ext is not None and hasattr(ext, "limiter"):
        setattr(sys.modules["app"], "limiter", getattr(ext, "limiter"))
except Exception:
    pass


def _install_legacy_module_aliases():
    """Map old DB/model import paths to modules now housed under admin/."""
    import sys

    legacy_targets = {
        "app.models": "app.admin.models",
        "app.models.base": "app.admin.models.base",
        "app.models.consignment": "app.admin.models.consignment",
        "app.models.lead": "app.admin.models.lead",
        "app.models.track": "app.admin.models.track",
        "app.db": "app.admin.db",
        "app.db.config": "app.admin.db.config",
        "app.db.maintenance": "app.admin.db.maintenance",
        "app.db.seed": "app.admin.db.seed",
        "app.db.session": "app.admin.db.session",
    }
    # Pre-populate sys.modules for common `app.*` imports by mapping them
    # to corresponding `admin.*` modules present in this package. This helps
    # other imports (e.g., app.middleware.database) resolve to admin.* equivalents.
    import os
    import types

    if "app" not in sys.modules:
        app_mod = types.ModuleType("app")
        # Mark as package so imports like `app.admin` treat it as a package
        app_mod.__path__ = []
        sys.modules["app"] = app_mod

    admin_root = ADMIN_ROOT
    for root, dirs, files in os.walk(admin_root):
        rel = Path(root).relative_to(admin_root)
        parent = "admin" if rel == Path(".") else "admin." + ".".join(rel.parts)
        # register packages (directories with __init__.py)
        for d in list(dirs):
            dpath = Path(root) / d
            if (dpath / "__init__.py").exists():
                pkg_mod = parent + "." + d
                app_pkg = "app." + pkg_mod[len("admin."):]
                app_admin_pkg = "app." + pkg_mod
                try:
                    mod = import_module(pkg_mod)
                    sys.modules.setdefault(app_pkg, mod)
                    sys.modules.setdefault(app_admin_pkg, mod)
                except Exception:
                    pass
        # register modules
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                mod_name = parent + "." + f[:-3]
                app_name = "app." + mod_name[len("admin."):]
                app_admin_name = "app." + mod_name
                try:
                    mod = import_module(mod_name)
                    sys.modules.setdefault(app_name, mod)
                    sys.modules.setdefault(app_admin_name, mod)
                except Exception:
                    pass
    for legacy_name, target_name in legacy_targets.items():
        try:
            sys.modules.setdefault(legacy_name, import_module(target_name))
        except ModuleNotFoundError:
            # Fallback: try importing the equivalent module under the local `admin` package.
            fallback = target_name.replace("app.admin", "admin")
            try:
                sys.modules.setdefault(legacy_name, import_module(fallback))
            except Exception:
                # If fallback fails, skip setting this alias.
                continue

def _register_route_modules():
    """Import route modules for blueprint registration side effects."""
    import_module("app.admin.routes.admin.auth_routes")
    import_module("app.admin.api.dashboard")


def register_admin_routes():
    """Import route modules before registering the admin blueprint."""
    _register_route_modules()


@admin_bp.route("/admin/dashboard", methods=["GET"])
def dashboard():
    """Serve the Flask-Admin dashboard at the legacy `/admin/dashboard` URL."""
    view = current_app.view_functions.get("flask_admin.index")
    if view:
        return view()
    return redirect(url_for("flask_admin.index"))


@admin_bp.route("/admin/consignments", methods=["GET"])
def consignments():
    """Redirect legacy consignment links to the Flask-Admin consignment view."""
    return redirect(url_for("consignments_admin.index_view"))


def create_app(*args, **kwargs):
    """Create the standalone admin app when Flask is pointed at `admin`."""
    from .app import create_app as create_standalone_app

    return create_standalone_app(*args, **kwargs)


# Install legacy module aliases after the blueprint and route decorators
# have been defined so imports of submodules don't trigger premature
# registration of blueprint routes.
_install_legacy_module_aliases()
