"""Simple pagination helper used by controllers.

Provides `paginate_query(query, page, per_page)` returning the common tuple
used by legacy code: (items, total, pages, has_prev, has_next).
"""

from typing import Tuple


def paginate_query(query, page: int = 1, per_page: int = 10) -> Tuple[list, int, int, bool, bool]:
    """Paginate a SQLAlchemy query-like object.

    Tries to call `query.paginate(...)` when available (Flask-SQLAlchemy).
    Falls back to manual `count` + `limit`/`offset` when necessary.
    """
    try:
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return (
            paginated.items,
            getattr(paginated, "total", len(paginated.items)),
            getattr(paginated, "pages", 1),
            getattr(paginated, "has_prev", False),
            getattr(paginated, "has_next", False),
        )
    except Exception:
        # Fallback for plain SQLAlchemy queries
        total = query.count()
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 10
        items = list(query.limit(per_page).offset((page - 1) * per_page).all())
        pages = max(1, (total + per_page - 1) // per_page)
        has_prev = page > 1
        has_next = page < pages
        return items, total, pages, has_prev, has_next
