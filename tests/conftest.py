"""Shared pytest fixtures for the modular test suite."""

import pytest

from tests.support.app_factory import create_test_app


@pytest.fixture
def app(tmp_path):
    """Return an application instance backed by an isolated SQLite database."""
    return create_test_app(database_url=f"sqlite:///{tmp_path / 'app.db'}")


@pytest.fixture
def client(app):
    """Return a Flask test client for the isolated application fixture."""
    return app.test_client()
