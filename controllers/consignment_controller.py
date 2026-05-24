import logging
from app.models import Consignment, db
from app.controllers import serialize_consignment, paginate_query

logger = logging.getLogger(__name__)

# Controller logic only — no route re-exports or cross-module route imports.
# Routes must import controller helpers directly from ``app.controllers.*``.


def get_panel_rows(limit=200):
    """Return a tuple (rows, total, large_flag) for the admin panel.

    Keeps DB/query logic centralized in the controller so route modules remain
    thin and focused on HTTP concerns.
    """
    total = Consignment.query.count()
    if total > 500:
        return [], total, True

    consignments = Consignment.query.order_by(Consignment.id.asc()).limit(limit).all()
    rows = [serialize_consignment(c) for c in consignments]
    return rows, total, False


def get_list_rows(page=1, per_page=10, search="", sort_by="id", sort_order="asc"):
    """Return rows list for the consignments list API view.

    Preserves the same filtering, sorting and pagination behavior used by
    the route, but keeps DB access inside controller.
    """
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    allowed_sort_columns = {
        "id",
        "consignment_number",
        "status",
        "pickup_pincode",
        "drop_pincode",
        "pickup_tag",
        "drop_tag",
        "pickup_date",
        "drop_date",
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

    items, paginated = paginate_query(
        query, page=page, per_page=per_page, error_out=False
    )
    rows = [serialize_consignment(c) for c in items]

    return rows, paginated
