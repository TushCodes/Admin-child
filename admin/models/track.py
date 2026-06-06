"""Database model used by public consignment tracking."""

from .base import db
from .consignment import Consignment


class TrackConsignment(db.Model):
    """Read-only tracking view of a consignment for public shipment lookups."""

    __table__ = Consignment.__table__
