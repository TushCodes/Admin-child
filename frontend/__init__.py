"""Frontend asset and template locations for the Flask application."""

from pathlib import Path

FRONTEND_ROOT = Path(__file__).resolve().parent
TEMPLATE_FOLDER = FRONTEND_ROOT / "templates"
STATIC_FOLDER = FRONTEND_ROOT / "static"

__all__ = ["FRONTEND_ROOT", "TEMPLATE_FOLDER", "STATIC_FOLDER"]
