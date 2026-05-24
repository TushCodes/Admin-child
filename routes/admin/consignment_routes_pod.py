import logging
import os
import uuid
from flask import current_app, redirect, request, send_file
from app.controllers.responses import json_error, json_success
from werkzeug.utils import secure_filename
import io as _io

from app.admin import admin_bp
from app.admin.auth import require_admin
from app.models import Consignment, db
from app.services.pod_storage import (
    get_supabase_client as _get_supabase_client,
    get_pod_url as _get_pod_url,
)
from app.utils.db import transaction

logger = logging.getLogger(__name__)


@admin_bp.route(
    "/admin/consignments/<int:consignment_id>/pod",
    methods=["GET"],
    endpoint="consignment_pod_file",
)
@require_admin
def consignment_pod_file(consignment_id):
    try:
        consignment = db.session.get(Consignment, consignment_id)
        if not consignment or not getattr(consignment, "pod_image", None):
            return json_error("No POD found.", 404)

        pod_path = consignment.pod_image
        # If it's an already-public URL or a supabase marker, try to resolve
        # to a redirectable URL via the shared `get_pod_url` helper.
        url = _get_pod_url(pod_path, ttl=30)
        if url:
            return redirect(url)

        upload_folder = os.path.join(current_app.instance_path, "uploads")
        safe_path = os.path.normpath(os.path.join(upload_folder, pod_path))
        if not safe_path.startswith(os.path.abspath(upload_folder)):
            return json_error("Invalid POD path.", 400)

        if not os.path.exists(safe_path):
            return json_error("POD file missing.", 404)

        return send_file(safe_path)
    except Exception:
        logger.exception("Error serving POD file")
        return json_error("Failed to serve POD.", 500)


@admin_bp.route(
    "/admin/consignments/<int:consignment_id>/pod",
    methods=["POST"],
    endpoint="consignment_pod_upload",
)
@require_admin
def consignment_pod_upload(consignment_id):
    upload = request.files.get("file")
    if not upload or not upload.filename:
        return json_error("No file uploaded.", 400)

    if not (upload.mimetype or "").startswith("image/"):
        return json_error("POD must be an image file.", 400)

    try:
        consignment = db.session.get(Consignment, consignment_id)
        if not consignment:
            return json_error("Consignment not found.", 404)

        filename = secure_filename(upload.filename)
        filename = f"{uuid.uuid4().hex}_{filename}"
        file_bytes = upload.read()

        supa = _get_supabase_client()
        bucket = os.getenv("SUPABASE_BUCKET", "pod-uploads")
        if supa:
            try:
                object_path = f"{consignment_id}/{filename}"
                supa.storage.from_(bucket).upload(
                    object_path,
                    _io.BytesIO(file_bytes),
                    {"content-type": upload.mimetype or "application/octet-stream"},
                )
                with transaction(db) as session:
                    consignment.pod_image = f"supabase:{bucket}/{object_path}"
                return json_success({"pod_image": consignment.pod_image})
            except Exception:
                try:
                    db.session.rollback()
                except Exception:
                    logger.exception(
                        "Failed to rollback DB session after supabase upload error"
                    )
                logger.exception(
                    "Supabase POD upload failed; falling back to local storage"
                )

        try:
            upload_folder = os.path.join(current_app.instance_path, "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            dest_path = os.path.join(upload_folder, filename)
            with open(dest_path, "wb") as file_handle:
                file_handle.write(file_bytes)
            with transaction(db) as session:
                consignment.pod_image = filename
            return json_success({"pod_image": filename})
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                logger.exception(
                    "Failed to rollback DB session after local POD upload error"
                )
            logger.exception("POD upload failed (local)")
            return json_error("Upload failed.", 500)
    except Exception:
        logger.exception("POD upload failed")
        return json_error("Upload failed.", 500)


@admin_bp.route(
    "/admin/consignments/<int:consignment_id>/pod",
    methods=["DELETE"],
    endpoint="consignment_pod_delete",
)
@require_admin
def consignment_pod_delete(consignment_id):
    try:
        consignment = db.session.get(Consignment, consignment_id)
        if not consignment or not getattr(consignment, "pod_image", None):
            return json_error("No POD to delete.", 404)

        pod_val = consignment.pod_image
        if isinstance(pod_val, str) and pod_val.startswith("supabase:"):
            client = _get_supabase_client()
            if client:
                try:
                    _, rest = pod_val.split(":", 1)
                    bucket, object_path = rest.split("/", 1)
                    client.storage.from_(bucket).remove([object_path])
                except Exception:
                    logger.exception("Failed to remove POD from Supabase")

        else:
            upload_folder = os.path.join(current_app.instance_path, "uploads")
            pod_rel = consignment.pod_image
            try:
                pod_path = os.path.normpath(os.path.join(upload_folder, pod_rel))
                if pod_path.startswith(
                    os.path.abspath(upload_folder)
                ) and os.path.exists(pod_path):
                    try:
                        os.remove(pod_path)
                    except Exception:
                        logger.exception("Failed to remove POD file from disk")
            except Exception:
                logger.exception("Error while attempting to remove local POD file")

        with transaction(db) as session:
            consignment.pod_image = None
        return json_success()
    except Exception:
        logger.exception("Failed deleting POD")
        return json_error("Delete failed.", 500)
