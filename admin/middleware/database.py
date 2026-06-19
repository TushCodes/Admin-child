"""Simple shim for database middleware used in local development.

This provides `get_request_db_session()` and `mark_db_rollback()` so the
admin app can run without the full application middleware plumbing.
"""

from types import SimpleNamespace

_session = None

class _DummySession:
    def commit(self):
        return None
    def rollback(self):
        return None


def get_request_db_session():
    global _session
    if _session is None:
        _session = _DummySession()
    return _session


def mark_db_rollback():
    # No-op for local shim
    return None
