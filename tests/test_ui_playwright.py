"""Optional Playwright UI smoke tests for Streamlit dashboard.

Enable with environment variables:
- RUN_UI_E2E_TESTS=1
- APP_BASE_URL=http://localhost:8501 (optional)
"""
import os
import urllib.request
import pytest


RUN_E2E = os.getenv("RUN_UI_E2E_TESTS") == "1"
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

pytestmark = pytest.mark.skipif(not RUN_E2E, reason="UI E2E tests disabled. Set RUN_UI_E2E_TESTS=1")


@pytest.fixture(scope="module")
def playwright_page():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


@pytest.fixture(scope="module", autouse=True)
def ensure_app_reachable():
    try:
        with urllib.request.urlopen(APP_BASE_URL, timeout=5):
            return
    except Exception:
        pytest.skip(f"Streamlit app is not reachable at {APP_BASE_URL}")


def test_dashboard_loads_core_sections(playwright_page):
    """Verify dashboard shell and sidebar controls render."""
    page = playwright_page
    page.goto(APP_BASE_URL, wait_until="domcontentloaded")

    expect = pytest.importorskip("playwright.sync_api").expect
    expect(page.locator("text=/Cost\\s*&\\s*Usage\\s*Analyzer/i").first).to_be_visible(timeout=30000)
    expect(page.get_by_text("Select a subscription and one or more resource groups in the sidebar.")).to_be_visible(timeout=30000)


def test_dashboard_has_analysis_tabs(playwright_page):
    """Verify default prompt is shown before subscription/resource-group selection."""
    page = playwright_page
    page.goto(APP_BASE_URL, wait_until="domcontentloaded")

    expect = pytest.importorskip("playwright.sync_api").expect
    expect(page.get_by_text("Data source: SQLite cache by default. Use 'Refresh from Azure' to fetch latest data.")).to_be_visible(timeout=30000)
