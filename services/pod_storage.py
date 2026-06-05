"""Proof-of-delivery file storage helpers for Supabase or local uploads."""

import os
import logging
import _io
from flask import current_app

logger = logging.getLogger(__name__)


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


def store_pod_bytes(
    filename, file_bytes, content_type=None, bucket_name=None, instance_path=None
):
    """Store bytes either in Supabase (if configured) or on local disk.

    Returns a marker string for supabase uploads ("supabase:bucket/path") or
    a local filename.
    """
    client = get_supabase_client()
    if client:
        bucket = bucket_name or os.getenv("SUPABASE_BUCKET", "pod-uploads")
        object_path = f"consignments/{filename}"
        client.storage.from_(bucket).upload(
            object_path,
            _io.BytesIO(file_bytes),
            {"content-type": content_type or "application/octet-stream"},
        )
        return f"supabase:{bucket}/{object_path}"

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

    if isinstance(pod_value, str) and pod_value.startswith("supabase:"):
        client = get_supabase_client()
        if not client:
            return
        try:
            _, storage_path = pod_value.split(":", 1)
            bucket, object_path = storage_path.split("/", 1)
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


def get_pod_url(pod_value, signed_url_ttl=None):
    """Return a URL for the given pod_value when possible.

    - If `pod_value` is an absolute http(s) URL, return it unchanged.
    - If `pod_value` is a Supabase marker ("supabase:bucket/path"), attempt
      to create a short signed URL (or fall back to public URL). Returns None
      when no URL can be generated (e.g., supabase not configured).
    """
    if not pod_value or not isinstance(pod_value, str):
        return None

    if pod_value.startswith("http://") or pod_value.startswith("https://"):
        return pod_value

    if pod_value.startswith("supabase:"):
        client = get_supabase_client()
        if not client:
            return None
        try:
            _, storage_path = pod_value.split(":", 1)
            bucket, object_path = storage_path.split("/", 1)
            if signed_url_ttl is None:
                signed_url_ttl = int(os.getenv("SUPABASE_SIGNED_URL_TTL", "30"))
            signed_response = client.storage.from_(bucket).create_signed_url(
                object_path, signed_url_ttl
            )
            pod_url = None
            if isinstance(signed_response, dict):
                pod_url = (
                    signed_response.get("signedURL")
                    or signed_response.get("signed_url")
                    or signed_response.get("signedUrl")
                )
            if not pod_url:
                public_response = client.storage.from_(bucket).get_public_url(
                    object_path
                )
                pod_url = public_response.get("publicURL") or public_response.get(
                    "publicUrl"
                )
            return pod_url
        except Exception:
            logger.exception("Error generating Supabase POD URL")
            try:
                public_response = client.storage.from_(bucket).get_public_url(
                    object_path
                )
                return public_response.get("publicURL") or public_response.get(
                    "publicUrl"
                )
            except Exception:
                return None

    return None
