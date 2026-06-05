"""Helpers for running the Flask application during browser tests."""

import socket
import threading
from contextlib import contextmanager

from werkzeug.serving import make_server

from tests.support.app_factory import create_test_app


def find_free_port():
    """Return an available localhost TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextmanager
def run_app_server(database_url=None):
    """Start the Flask app in a background thread and yield its base URL."""
    app = create_test_app(database_url=database_url)
    port = find_free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
