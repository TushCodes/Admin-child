"""DEPRECATED — this module is intentionally empty.

All routes that were previously defined here have been moved to individual
modules in this package:

  - dashboard.py   →  /admin/dashboard
  - backup.py      →  /admin/generate-backup
  - leads.py       →  /admin/leads, /admin/leads/reject-empty-phone

Keeping duplicate @admin_bp.route() decorators here caused Flask to raise
AssertionError at startup ("View function mapping is overwriting an existing
endpoint function"). Do not add route definitions back to this file.
"""
