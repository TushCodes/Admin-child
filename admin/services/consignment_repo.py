"""Repository layer for Consignment DB operations.

Keep CRUD and query primitives here. Do NOT commit or rollback in this module;
transaction boundaries live in service layer.
"""

from typing import Optional, Tuple, List, Dict
from app.admin.models import Consignment, db
from sqlalchemy import or_


def get_by_id(consignment_id: int) -> Optional[Consignment]:
    """Return one consignment by database id, or None when it does not exist."""
    return db.session.get(Consignment, consignment_id)


def get_map_all() -> Dict[int, Consignment]:
    """Return all consignments in the map shape expected by legacy callers."""
    return {consignment.id: consignment for consignment in Consignment.query.all()}


def list_paginated(
    page: int = 1,
    per_page: int = 10,
    search: str = "",
    sort_by: str = "id",
    sort_order: str = "asc",
) -> Tuple[List[Consignment], int, int, bool, bool]:
    """Return consignments filtered, sorted, and paginated for list pages."""
    query = Consignment.query
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
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

    total = query.count()
    sort_column = getattr(Consignment, sort_by, Consignment.id)
    if sort_order != "desc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return (
        paginated.items,
        total,
        paginated.pages,
        paginated.has_prev,
        paginated.has_next,
    )


def query_existing_numbers() -> set:
    """Return all existing consignment numbers as a set for duplicate checks."""
    rows = Consignment.query.with_entities(Consignment.consignment_number).all()
    return {record[0] for record in rows}


def add(instance: Consignment):
    """Stage a consignment object to be saved in the current database session."""
    db.session.add(instance)


def delete_by_id(consignment_id: int):
    """Delete a consignment by id when a matching row exists."""
    consignment = get_by_id(consignment_id)
    if consignment:
        db.session.delete(consignment)


def count() -> int:
    """Return the total number of consignments."""
    return Consignment.query.count()


def all_ordered() -> List[Consignment]:
    """Return all consignments ordered by their database id."""
    return Consignment.query.order_by(Consignment.id.asc()).all()


def flush():
    """Flush pending database changes without committing the transaction."""
    db.session.flush()
