from __future__ import annotations

import os
import uuid
import pytest
import allure
"""Pytest configuration and shared fixtures."""
from dotenv import load_dotenv

from src.utils.driver_factory import create_driver
from src.utils.config import get_env_config
from src.utils.api_client import ApiClient
from src.utils.auth import get_auth_token


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=os.environ.get("BROWSER", "chrome"), help="Browser: chrome or firefox")
    parser.addoption("--env", action="store", default=os.environ.get("TEST_ENV", "qa"), help="Environment: dev/qa/uat")
    parser.addoption("--tags", action="store", default=os.environ.get("TAGS", ""), help="Markers to run (e.g., smoke)")
    parser.addoption("--headless", action="store_true", help="Run browsers in headless mode")


def pytest_configure(config):
    # Dynamically select markers if --tags provided
    tags = config.getoption("--tags")
    if tags:
        # Use markers expression
        config.option.markexpr = tags
    # Load .env if present for local development
    load_dotenv()


@pytest.fixture(scope="session")
def env(request):
    env_name = request.config.getoption("--env")
    cfg = get_env_config(env_name)
    return cfg


@pytest.fixture(scope="session")
def api_client(env):
    client = ApiClient(base_url="https://petstore.swagger.io/v2")
    token = get_auth_token()
    if token:
        client.session.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="session", autouse=True)
def auth_token():
    """Fetch auth token once before all tests to support API-UI collaboration."""
    token = get_auth_token()
    if token:
        os.environ["API_TOKEN"] = token
    return token


@pytest.fixture()
def driver(request, env):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    driver = create_driver(browser=browser, headless=headless)
    yield driver
    # Teardown: take screenshot on failure
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is not None and getattr(rep_call, "failed", False):
        try:
            png = driver.get_screenshot_as_png()
            allure.attach(png, name=f"screenshot-{uuid.uuid4().hex}", attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass
    driver.quit()


def pytest_runtest_makereport(item, call):
    # Attach test result to the item for fixture teardown to know outcome
    if "driver" in item.fixturenames:
        setattr(item, "rep_" + call.when, call)
    return None
