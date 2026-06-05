"""Development database seed data helpers."""

import logging
import os

from app.models import Consignment
from app.db.session import transaction

logger = logging.getLogger(__name__)


def seed_development_data(db, app):
    """Create predictable sample consignments for a fresh development database."""
    if os.getenv("FLASK_ENV", "").strip().lower() != "development":
        return

    try:
        existing_count = Consignment.query.count()
        if existing_count >= 100:
            return

        sample_consignment_data = []
        statuses = ["Pickup Scheduled", "In Transit", "Out for Delivery", "Delivered"]
        existing_numbers = {
            row[0]
            for row in Consignment.query.with_entities(
                Consignment.consignment_number
            ).all()
        }

        for index in range(1, 101):
            consignment_number = f"DEV{str(index).zfill(4)}"
            if consignment_number in existing_numbers:
                continue

            status = statuses[index % len(statuses)]
            pickup_pincode = str(110000 + (index % 900000))[:6]
            drop_pincode = str(400000 + (index % 500000))[:6]
            pickup_address = f"{index} Dev Pickup St, Dev City {index % 10}"
            drop_address = f"{index} Dev Drop Ave, Dest City {index % 10}"
            pickup_date = f"2026-05-{(index % 28) + 1:02d}"
            drop_date = f"2026-06-{(index % 28) + 1:02d}"
            eta = f"2026-06-{(index % 28) + 1:02d} 12:00"

            sample_consignment_data.append(
                Consignment(
                    consignment_number=consignment_number,
                    status=status,
                    pickup_address=pickup_address,
                    pickup_pincode=pickup_pincode,
                    pickup_date=pickup_date,
                    drop_address=drop_address,
                    drop_pincode=drop_pincode,
                    drop_date=drop_date,
                    eta=eta,
                    pickup_tag=f"PICK{index % 5}",
                    drop_tag=f"DROP{index % 7}",
                )
            )

        consignments_to_add = []
        remaining = max(0, 100 - existing_count)
        for item in sample_consignment_data:
            if remaining <= 0:
                break
            consignments_to_add.append(item)
            remaining -= 1

        if consignments_to_add:
            try:
                with transaction(db):
                    db.session.add_all(consignments_to_add)
            except Exception as error:
                logger.exception("Failed to seed development consignments: %s", error)

        logger.info(
            "Seeded development consignments; total now %d (added %d)",
            Consignment.query.count(),
            len(consignments_to_add),
        )
    except Exception as error:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session during seeding")
        logger.exception("Failed to seed development consignments: %s", error)
