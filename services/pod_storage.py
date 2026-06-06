"""Proof-of-delivery file storage helpers for Supabase or local uploads."""

import _io
import logging
import mimetypes
import os
from urllib.parse import unquote, urlparse

from flask import current_app, send_file

logger = logging.getLogger(__name__)

SUPABASE_MARKER_PREFIX = "supabase:"


def get_supabase_client():
    """Return a configured Supabase client, or None when cloud storage is unavailable."""
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    if not supabase_url or not supabase_key:
        return None
    try:
        from supabase import create_client
    except Exception:
        logger.warning("Supabase package not available; falling back to local uploads")
        return None

    try:
        return create_client(supabase_url, supabase_key)
    except Exception:
        logger.exception("Failed to create Supabase client")
        return None


def _split_supabase_marker(pod_value):
    if not isinstance(pod_value, str) or not pod_value.startswith(
        SUPABASE_MARKER_PREFIX
    ):
        return None

    storage_path = pod_value.split(":", 1)[1]
    if "/" not in storage_path:
        return None

    bucket, object_path = storage_path.split("/", 1)
    if not bucket or not object_path:
        return None
    return bucket, object_path


def _extract_supabase_path_from_url(pod_value):
    """Best-effort recovery for legacy public/signed Supabase URLs stored in DB."""
    if not isinstance(pod_value, str) or not pod_value.startswith(
        ("http://", "https://")
    ):
        return None

    parsed = urlparse(pod_value)
    marker = "/storage/v1/object/"
    if marker not in parsed.path:
        return None

    suffix = parsed.path.split(marker, 1)[1]
    for prefix in ("public/", "sign/"):
        if suffix.startswith(prefix):
            suffix = suffix[len(prefix) :]
            break

    if "/" not in suffix:
        return None

    bucket, object_path = suffix.split("/", 1)
    bucket = unquote(bucket)
    object_path = unquote(object_path)
    if not bucket or not object_path:
        return None
    return bucket, object_path


def resolve_supabase_reference(pod_value):
    """Return (bucket, object_path) for current markers or legacy Supabase URLs."""
    return _split_supabase_marker(pod_value) or _extract_supabase_path_from_url(
        pod_value
    )


def store_pod_bytes(
    filename, file_bytes, content_type=None, bucket_name=None, instance_path=None
):
    """Store bytes either in Supabase (if configured) or on local disk.

    Returns a marker string for supabase uploads ("supabase:bucket/path") or
    a local filename. Supabase storage keeps the object path permanent; viewing
    later is handled through the Flask POD endpoint instead of expiring signed URLs.
    """
    client = get_supabase_client()
    if client:
        bucket = bucket_name or os.getenv("SUPABASE_BUCKET", "pod-uploads")
        object_path = f"consignments/{filename}"
        try:
            client.storage.from_(bucket).upload(
                object_path,
                _io.BytesIO(file_bytes),
                {"content-type": content_type or "application/octet-stream"},
            )
            return f"{SUPABASE_MARKER_PREFIX}{bucket}/{object_path}"
        except Exception:
            logger.exception(
                "Supabase POD upload failed; falling back to local storage"
            )

    upload_folder = os.path.join(
        (instance_path or current_app.instance_path), "uploads"
    )
    os.makedirs(upload_folder, exist_ok=True)
    destination_path = os.path.join(upload_folder, filename)
    with open(destination_path, "wb") as file_handle:
        file_handle.write(file_bytes)
    return filename


def delete_pod_file(pod_value, instance_path=None):
    """Remove a POD file from Supabase or local disk when it exists."""
    if not pod_value:
        return

    supabase_ref = resolve_supabase_reference(pod_value)
    if supabase_ref:
        client = get_supabase_client()
        if not client:
            return
        try:
            bucket, object_path = supabase_ref
            client.storage.from_(bucket).remove([object_path])
        except Exception:
            logger.exception("Failed to remove POD from Supabase")
        return

    upload_folder = os.path.join(
        (instance_path or current_app.instance_path), "uploads"
    )
    pod_path = os.path.normpath(os.path.join(upload_folder, pod_value))
    if pod_path.startswith(os.path.abspath(upload_folder)) and os.path.exists(pod_path):
        try:
            os.remove(pod_path)
        except Exception:
            logger.exception("Failed to remove POD file from disk")


def get_pod_url(pod_value):
    """Return only stable public POD URLs.

    Signed URLs are intentionally not created or returned because they expire.
    Supabase markers should be served through :func:`send_pod_file_response`.
    """
    if not pod_value or not isinstance(pod_value, str):
        return None

    if resolve_supabase_reference(pod_value):
        if "/storage/v1/object/sign/" in pod_value or "token=" in pod_value:
            return None
        if pod_value.startswith(("http://", "https://")):
            return pod_value
        client = get_supabase_client()
        if not client:
            return None
        try:
            bucket, object_path = resolve_supabase_reference(pod_value)
            public_response = client.storage.from_(bucket).get_public_url(object_path)
            if isinstance(public_response, dict):
                return public_response.get("publicURL") or public_response.get(
                    "publicUrl"
                )
            return public_response
        except Exception:
            logger.exception("Error generating Supabase public POD URL")
            return None

    if pod_value.startswith(("http://", "https://")):
        return pod_value

    return None


def _download_supabase_bytes(client, bucket, object_path):
    response = client.storage.from_(bucket).download(object_path)
    if isinstance(response, bytes):
        return response
    if hasattr(response, "content"):
        return response.content
    if hasattr(response, "read"):
        return response.read()
    return bytes(response)


def send_pod_file_response(pod_value, instance_path=None):
    """Build a Flask response for a POD without using expiring signed URLs."""
    supabase_ref = resolve_supabase_reference(pod_value)
    if supabase_ref:
        client = get_supabase_client()
        if not client:
            raise FileNotFoundError("Supabase storage is not configured.")

        bucket, object_path = supabase_ref
        file_bytes = _download_supabase_bytes(client, bucket, object_path)
        mimetype = mimetypes.guess_type(object_path)[0] or "application/octet-stream"
        download_name = os.path.basename(object_path) or "pod"
        return send_file(
            _io.BytesIO(file_bytes),
            mimetype=mimetype,
            download_name=download_name,
            conditional=False,
        )

    upload_folder = os.path.join(
        (instance_path or current_app.instance_path), "uploads"
    )
    safe_path = os.path.normpath(os.path.join(upload_folder, pod_value))
    if not safe_path.startswith(os.path.abspath(upload_folder)):
        raise ValueError("Invalid POD path.")
    if not os.path.exists(safe_path):
        raise FileNotFoundError("POD file missing.")
    return send_file(safe_path)
