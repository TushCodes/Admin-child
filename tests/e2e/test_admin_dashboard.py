"""End-to-end tests for the admin dashboard user flow."""

import asyncio

from tests.support.admin_dashboard import login_and_collect_dashboard_text
from tests.support.server import run_app_server


def test_admin_dashboard_components_are_visible(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'admin-dashboard.db'}"

    with run_app_server(database_url=database_url) as base_url:
        url, text = asyncio.run(login_and_collect_dashboard_text(base_url))

    assert url.endswith("/admin/dashboard")
    assert "Welcome back!" in text
    assert "Consignment Sheet" in text
    assert "Leads Panel" in text
    assert "Database Backup" in text
    assert "Gram SCS Admin" in text
