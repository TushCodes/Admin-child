"""Validation and normalization helpers for logistics data entered by users."""

import re
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


CONSIGNMENT_NUMBER_REGEX = re.compile(r"^[A-Za-z0-9]{1,16}$")
INDIAN_PINCODE_REGEX = re.compile(r"^[1-9][0-9]{5}$")
ALLOWED_STATUSES = {
    "Pickup Scheduled",
    "In Transit",
    "Out for Delivery",
    "Delivered",
}


def normalize_consignment_number(raw_value):
    """Clean and validate a consignment number entered by a user or spreadsheet."""
    value = (raw_value or "").strip().upper()
    if not CONSIGNMENT_NUMBER_REGEX.fullmatch(value):
        raise ValueError(f"Invalid consignment number: {value or '(empty)'}")
    return value


def normalize_status(raw_value):
    """Clean and validate that a shipment status is one of the supported values."""
    value = (raw_value or "").strip()
    if value not in ALLOWED_STATUSES:
        raise ValueError("Invalid status value.")
    return value


def normalize_indian_pincode(raw_value, field_name):
    """Clean and validate an optional six-digit Indian pincode."""
    value = (raw_value or "").strip()
    if value == "":
        return ""
    if not INDIAN_PINCODE_REGEX.fullmatch(value):
        raise ValueError(f"{field_name} must be a valid 6-digit Indian pincode.")
    return value


def validate_and_round_coordinate(raw_value, field_name):
    """Validate a coordinate value and round it to the supported precision."""
    try:
        decimal_value = Decimal(str(raw_value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    exponent = decimal_value.as_tuple().exponent
    decimal_places = -exponent if exponent < 0 else 0
    if decimal_places > 5:
        raise ValueError(f"{field_name} can have at most 5 decimal places.")

    numeric = float(decimal_value)
    return round(numeric, 5)
