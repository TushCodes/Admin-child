"""Request-scoped database session middleware."""

import logging

from flask import g, has_request_context

from app.models import db

logger = logging.getLogger(__name__)


def get_request_db_session():
    """Return the request-scoped SQLAlchemy session when available."""
    if has_request_context() and hasattr(g, "db_session"):
        return g.db_session
    return db.session


def mark_db_rollback():
    """Flag the current request so teardown rolls back instead of committing."""
    if has_request_context():
        g.db_should_rollback = True


def register_database_middleware(app):
    """Commit/rollback database work at the request middleware boundary."""

    @app.before_request
    def bind_request_db_session():
        g.db_session = db.session
        g.db_should_rollback = False

    @app.after_request
    def rollback_error_responses(response):
        if response.status_code >= 400:
            g.db_should_rollback = True
        return response

    @app.teardown_request
    def finalize_request_db_session(error=None):
        try:
            if error is not None or getattr(g, "db_should_rollback", False):
                db.session.rollback()
            else:
                db.session.commit()
        except Exception:
            logger.exception("Failed to finalize request database session")
            try:
                db.session.rollback()
            except Exception:
                logger.exception("Failed to rollback request database session")
            raise
        finally:
            db.session.remove()
