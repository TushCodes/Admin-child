"""Application loading helpers shared by tests."""

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_MODULE_PATH = ROOT / "__init__.py"


def create_test_app(database_url=None):
    """Load the Flask app package from the repo root with test-safe defaults."""
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("RATELIMIT_STORAGE_URI", "memory://")
    if database_url is not None:
        os.environ["DATABASE_URL"] = database_url
    else:
        os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

    spec = importlib.util.spec_from_file_location("app", str(APP_MODULE_PATH))
    module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = module
    spec.loader.exec_module(module)
    return module.create_app()
