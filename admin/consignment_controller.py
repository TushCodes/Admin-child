import logging
from app.models import Consignment, db
logger = logging.getLogger(__name__)

# Import and expose route handlers from canonical route modules so tests and
# old call sites that reference names on this module continue to work while
# route registration is handled by the extracted modules under app.routes.
from app.routes.admin.consignment_routes_panel import (
    consignments_panel,
    consignments_list_api,
    consignments_save,
)
from app.routes.admin.consignment_routes_exports import (
    consignments_import_excel,
    consignments_export_excel,
    consignments_export_pdf,
    consignments_import_template_excel,
)
from app.routes.admin.consignment_routes_pod import (
    consignment_pod_file,
    consignment_pod_upload,
    consignment_pod_delete,
)


def get_panel_rows(limit=200):
    """Return a tuple (rows, total, large_flag) for the admin panel.

    Keeps DB/query logic centralized in the controller so route modules remain
    thin and focused on HTTP concerns.
    """
    total = Consignment.query.count()
    if total > 500:
        return [], total, True

    consignments = Consignment.query.order_by(Consignment.id.asc()).limit(limit).all()
    rows = [
        {
            "id": c.id,
            "consignment_number": c.consignment_number,
            "status": c.status,
            "pickup_pincode": c.pickup_pincode,
            "pickup_address": getattr(c, "pickup_address", None),
            "pickup_tag": getattr(c, "pickup_tag", None),
            "pickup_date": getattr(c, "pickup_date", None),
            "drop_pincode": c.drop_pincode,
            "drop_address": getattr(c, "drop_address", None),
            "drop_tag": getattr(c, "drop_tag", None),
            "drop_date": getattr(c, "drop_date", None),
            "eta": c.eta,
            "pod_image": getattr(c, "pod_image", None),
        }
        for c in consignments
    ]
    return rows, total, False


def get_list_rows(page=1, per_page=10, search="", sort_by="id", sort_order="asc"):
    """Return rows list for the consignments list API view.

    Preserves the same filtering, sorting and pagination behavior used by
    the route, but keeps DB access inside controller.
    """
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    allowed_sort_columns = {
        "id", "consignment_number", "status", "pickup_pincode",
        "drop_pincode", "pickup_tag", "drop_tag", "pickup_date", "drop_date"
    }
    sort_by = sort_by if sort_by in allowed_sort_columns else "id"
    sort_order = "asc" if sort_order.lower() == "asc" else "desc"

    query = Consignment.query
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Consignment.consignment_number.ilike(pattern),
                Consignment.status.ilike(pattern),
                Consignment.pickup_tag.ilike(pattern),
                Consignment.drop_tag.ilike(pattern),
                Consignment.pickup_pincode.ilike(pattern),
                Consignment.drop_pincode.ilike(pattern),
                Consignment.pickup_address.ilike(pattern),
                Consignment.drop_address.ilike(pattern),
            )
        )

    sort_column = getattr(Consignment, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    rows = [
        {
            "id": c.id,
            "consignment_number": c.consignment_number,
            "status": c.status,
            "pickup_pincode": c.pickup_pincode,
            "pickup_address": getattr(c, "pickup_address", None),
            "pickup_tag": getattr(c, "pickup_tag", None),
            "pickup_date": getattr(c, "pickup_date", None),
            "drop_pincode": c.drop_pincode,
            "drop_address": getattr(c, "drop_address", None),
            "drop_tag": getattr(c, "drop_tag", None),
            "drop_date": getattr(c, "drop_date", None),
            "eta": c.eta,
            "pod_image": getattr(c, "pod_image", None),
        }
        for c in paginated.items
    ]

    return rows, paginated
