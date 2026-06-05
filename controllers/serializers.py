"""Model serialization helpers used by controllers and routes."""


def serialize_consignment(consignment):
    """Return a lightweight dict representation of a Consignment row."""
    return {
        "id": consignment.id,
        "consignment_number": consignment.consignment_number,
        "status": consignment.status,
        "pickup_pincode": consignment.pickup_pincode,
        "pickup_address": getattr(consignment, "pickup_address", None),
        "pickup_tag": getattr(consignment, "pickup_tag", None),
        "pickup_date": getattr(consignment, "pickup_date", None),
        "drop_pincode": consignment.drop_pincode,
        "drop_address": getattr(consignment, "drop_address", None),
        "drop_tag": getattr(consignment, "drop_tag", None),
        "drop_date": getattr(consignment, "drop_date", None),
        "eta": getattr(consignment, "eta", None),
        "pod_image": getattr(consignment, "pod_image", None),
    }
