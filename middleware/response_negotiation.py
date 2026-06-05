"""Backward-compatible import path for response negotiation helpers."""

from app.utils.content_negotiation import wants_json_response

__all__ = ["wants_json_response"]
