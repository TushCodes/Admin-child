"""Database session and transaction lifecycle helpers."""

from contextlib import contextmanager
import logging

from app.middleware.database import get_request_db_session, mark_db_rollback

logger = logging.getLogger(__name__)


@contextmanager
def transaction(db):
    """Context manager to commit or rollback a DB session.

    Usage:
        with transaction(db):
            db.session.add(obj)
            ...
    Commits on success, rolls back on exception.
    """
    try:
        session = get_request_db_session()
        yield session
        session.commit()
    except Exception:
        try:
            get_request_db_session().rollback()
        except Exception:
            logger.exception("Failed to rollback DB session")
        raise


def request_session():
    """Return the DB session managed by request middleware when present."""
    return get_request_db_session()


def rollback_request_session():
    """Ask database middleware to rollback this request at teardown."""
    mark_db_rollback()
    get_request_db_session().rollback()
