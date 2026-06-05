"""Playwright flows for the admin dashboard."""

from pathlib import Path

import pytest
from playwright.async_api import async_playwright


async def login_and_collect_dashboard_text(base_url):
    """Log into the admin dashboard and return the final URL plus body text."""
    async with async_playwright() as playwright:
        executable_path = Path(playwright.chromium.executable_path)
        if not executable_path.exists():
            pytest.skip(
                "Playwright Chromium browser is not installed; run `playwright install chromium`."
            )

        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"{base_url}/admin/login", wait_until="networkidle")
        await page.fill("#username", "admin")
        await page.fill("#password", "admin-pass")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/admin/dashboard", timeout=15000)
        await page.wait_for_load_state("networkidle")
        text = await page.locator("body").inner_text()
        url = page.url
        await browser.close()
        return url, text
