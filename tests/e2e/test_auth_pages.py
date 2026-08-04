import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "http://127.0.0.1:8013"


@pytest.fixture(scope="module")
def server():
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./e2e_auth.db"
    env["JWT_SECRET_KEY"] = "e2e-secret"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8013",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )

    for _ in range(30):
        try:
            urlopen(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("FastAPI test server did not start")

    yield BASE_URL

    process.terminate()
    process.wait(timeout=10)


def unique_email():
    return f"e2e{int(time.time() * 1000)}@example.com"


def test_register_page_valid_user_shows_success(server):
    email = unique_email()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.fill("#confirm-password", "Password123")
        page.click("button[type='submit']")

        expect(page.locator("#message")).to_contain_text("Registration successful")
        assert page.evaluate("localStorage.getItem('access_token')") is not None
        browser.close()


def test_register_page_short_password_shows_error(server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", unique_email())
        page.fill("#password", "short")
        page.fill("#confirm-password", "short")
        page.click("button[type='submit']")

        expect(page.locator("#message")).to_contain_text("Password must be at least 8 characters")
        browser.close()


def test_login_page_valid_user_shows_success(server):
    email = unique_email()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.fill("#confirm-password", "Password123")
        page.click("button[type='submit']")
        expect(page.locator("#message")).to_contain_text("Registration successful")

        page.goto(f"{server}/static/login.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.click("button[type='submit']")

        expect(page.locator("#message")).to_contain_text("Login successful")
        assert page.evaluate("localStorage.getItem('access_token')") is not None
        browser.close()


def test_login_page_wrong_password_shows_error(server):
    email = unique_email()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.fill("#confirm-password", "Password123")
        page.click("button[type='submit']")
        expect(page.locator("#message")).to_contain_text("Registration successful")

        page.goto(f"{server}/static/login.html")
        page.fill("#email", email)
        page.fill("#password", "WrongPass123")
        page.click("button[type='submit']")

        expect(page.locator("#message")).to_contain_text("Invalid email or password")
        browser.close()


def test_calculation_page_bread_flow(server):
    email = unique_email()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.fill("#confirm-password", "Password123")
        page.click("button[type='submit']")
        expect(page.locator("#message")).to_contain_text("Registration successful")

        page.goto(f"{server}/static/calculations.html")
        page.fill("#a", "15")
        page.fill("#b", "3")
        page.select_option("#type", "Divide")
        page.click("#save-button")
        expect(page.locator("#message")).to_contain_text("Calculation added")
        expect(page.locator("#calculation-list")).to_contain_text("5")

        page.click("button[data-action='read']")
        expect(page.locator("#detail")).to_contain_text("= 5")

        page.click("button[data-action='edit']")
        page.fill("#a", "20")
        page.fill("#b", "4")
        page.select_option("#type", "Multiply")
        page.click("#save-button")
        expect(page.locator("#message")).to_contain_text("Calculation updated")
        expect(page.locator("#calculation-list")).to_contain_text("80")

        page.click("button[data-action='delete']")
        expect(page.locator("#message")).to_contain_text("Calculation deleted")
        expect(page.locator("#calculation-list")).not_to_contain_text("80")
        browser.close()


def test_calculation_page_rejects_division_by_zero(server):
    email = unique_email()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{server}/static/register.html")
        page.fill("#email", email)
        page.fill("#password", "Password123")
        page.fill("#confirm-password", "Password123")
        page.click("button[type='submit']")
        expect(page.locator("#message")).to_contain_text("Registration successful")

        page.goto(f"{server}/static/calculations.html")
        page.fill("#a", "10")
        page.fill("#b", "0")
        page.select_option("#type", "Divide")
        page.click("#save-button")

        expect(page.locator("#message")).to_contain_text("Cannot divide by zero")
        browser.close()
