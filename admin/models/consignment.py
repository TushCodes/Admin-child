"""Database model for consignments managed by admins."""

from .base import db


class Consignment(db.Model):
    """Shipment record managed by admins and shown on the tracking page."""

    id = db.Column(db.Integer, primary_key=True)
    consignment_number = db.Column(db.String(16), unique=True, nullable=False)
    status = db.Column(db.String(200))
    pickup_pincode = db.Column(db.String(6))
    pickup_address = db.Column(db.Text)
    pickup_tag = db.Column(db.String(100))
    pickup_date = db.Column(db.String(100))
    drop_pincode = db.Column(db.String(6))
    drop_address = db.Column(db.Text)
    drop_tag = db.Column(db.String(100))
    drop_date = db.Column(db.String(100))
    eta = db.Column(db.String(100))
    eta_debug_json = db.Column(db.Text)
    # URL or internal path to the Proof-Of-Delivery (POD) image/file
    pod_image = db.Column(db.String(1024))
