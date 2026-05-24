"""Controller for admin leads listing and cleanup."""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def serialize_lead_row(lead):
    return {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "subject": lead.subject,
        "message": lead.message,
        "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(lead, "created_at", None) else "",
    }


def get_leads():
    from app.models import Lead

    leads = Lead.query.order_by(Lead.created_at.desc(), Lead.id.desc()).all()
    return [serialize_lead_row(l) for l in leads]


def delete_empty_phone_leads(db):
    from app.models import Lead
    from sqlalchemy import func, or_

    deleted_count = (
        Lead.query.filter(
            or_(
                Lead.phone.is_(None),
                func.trim(Lead.phone) == "",
            )
        ).delete(synchronize_session=False)
    )
    return deleted_count
