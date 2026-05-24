from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__
)

# Import canonical route modules so the blueprint gets its routes registered.
# Doing this here keeps the admin package self-contained while avoiding
# legacy modules that were previously present under app.admin.
from app.routes.admin import auth_routes, dashboard, backup, leads, \
    consignment_routes_panel, consignment_routes_exports, consignment_routes_pod  # noqa: E402, F401 (side-effect imports)
from app.admin import consignment_controller  # noqa: E402, F401  (expose controller helpers)

