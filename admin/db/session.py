"""Database session and transaction lifecycle helpers for the admin app."""

from contextlib import contextmanager
import logging

from flask import g, has_request_context

from ..models import db

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


@contextmanager
def transaction(_db=None):
    """Commit the active session on success and rollback on exception."""
    active_db = _db or db
    session = get_request_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        try:
            session.rollback()
        except Exception:
            logger.exception("Failed to rollback DB session")
        raise
    finally:
        if not has_request_context():
            active_db.session.remove()


def request_session():
    """Return the DB session managed by request middleware when present."""
    return get_request_db_session()


def rollback_request_session():
    """Ask database middleware to rollback this request at teardown."""
    mark_db_rollback()
    get_request_db_session().rollback()


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
