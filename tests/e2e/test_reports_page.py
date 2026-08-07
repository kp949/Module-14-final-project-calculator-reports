import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8000"


def test_reports_page_loads_after_login():
    if os.path.exists("e2e_reports.db"):
        os.remove("e2e_reports.db")

    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./e2e_reports.db"

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env,
    )

    try:
        time.sleep(3)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            email = f"reports{int(time.time())}@example.com"

            page.goto(f"{BASE_URL}/static/register.html")
            page.fill("#email", email)
            page.fill("#password", "Password123")
            page.fill("#confirm-password", "Password123")
            page.click("button")
            page.wait_for_timeout(1000)

            page.goto(f"{BASE_URL}/static/calculations.html")
            page.fill("#a", "10")
            page.fill("#b", "5")
            page.select_option("#type", "Add")
            page.click("#save-button")
            page.wait_for_timeout(1000)

            page.goto(f"{BASE_URL}/static/reports.html")
            page.wait_for_timeout(1000)

            assert "Calculation Reports" in page.content()
            assert "Report loaded successfully." in page.content()
            assert page.locator("#total-calculations").inner_text() == "1"
            assert page.locator("#add-count").inner_text() == "1"

            browser.close()
    finally:
        server.terminate()
        server.wait()