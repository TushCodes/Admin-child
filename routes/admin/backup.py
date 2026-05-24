"""Admin backup route (thin) that delegates payload building to controller."""

import logging
from flask import send_file, session
from app.utils.response import json_error
from app import limiter
from app.admin import admin_bp
from app.admin.auth import require_admin
from app.models import Consignment, Lead
from app.admin.backup import build_backup_payload

logger = logging.getLogger(__name__)

LARGE_BACKUP_ROW_THRESHOLD = 10000


@admin_bp.route("/admin/generate-backup", methods=["GET"])
@limiter.limit("3 per minute")
@require_admin
def generate_backup():
    admin_user = session.get("admin_username") or "unknown"

    try:
        table_specs = [
            ("consignments", Consignment, {"eta_debug_json"}),
            ("leads", Lead, set()),
        ]

        buffer, metadata = build_backup_payload(table_specs)

        total_rows = metadata.get("total_rows", 0)
        if total_rows > LARGE_BACKUP_ROW_THRESHOLD:
            logger.warning(
                "Large admin backup requested by %s: total_rows=%s threshold=%s",
                admin_user,
                total_rows,
                LARGE_BACKUP_ROW_THRESHOLD,
            )

        filename = f"backup_{metadata['generated_at'].replace(':','').replace('-','').replace('T','_')}.json"

        logger.info(
            "Admin backup generated successfully by %s (total_rows=%s)",
            admin_user,
            total_rows,
        )

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/json",
        )
    except Exception as e:
        logger.error("Admin backup generation failed for %s: %s", admin_user, e, exc_info=True)
        return json_error("Failed to generate backup.", 500)
