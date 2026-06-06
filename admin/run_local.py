#!/usr/bin/env python3
"""Run the standalone admin-panel Flask app locally."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

APP_MODULE_PATH = Path(__file__).resolve().with_name("app.py")
spec = spec_from_file_location("admin_standalone_app", APP_MODULE_PATH)
module = module_from_spec(spec)
spec.loader.exec_module(module)

admin_app = module.app

if __name__ == "__main__":
    admin_app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
