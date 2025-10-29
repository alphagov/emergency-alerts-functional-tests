import os
from datetime import datetime
from pathlib import Path

import pytest

from clients.broadcast_client import BroadcastClient
from clients.test_api_client import TestApiClient
from config import config, setup_shared_config
from tests.pages.pages import HomePage
from tests.playwright_adapter import PlaywrightDriver


@pytest.fixture(scope="session", autouse=True)
def shared_config():
    """
    Setup shared config variables (eg env and urls)
    """
    setup_shared_config()


@pytest.fixture(scope="session")
def download_directory(tmp_path_factory):
    return tmp_path_factory.mktemp("downloads")


@pytest.fixture(scope="module")
def _driver(request, download_directory):
    http_proxy = os.getenv("HTTP_PROXY")
    # option added by pytest Playwright plugin, autoset by pytest.ini
    headless = not request.config.getoption("--headed")

    if os.environ.get("CI", "false") != "false":
        headless = True

    driver = PlaywrightDriver(
        headless=headless, proxy=http_proxy, download_dir=str(download_directory)
    )
    driver.set_window_size(1280, 720)

    driver.delete_all_cookies()

    # go to root page and accept analytics cookies to hide banner in all pages
    driver.get(config["eas_admin_url"])
    HomePage(driver).accept_cookie_warning()

    yield driver
    driver.close()


@pytest.fixture(scope="function")
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed

    _driver.start_tracing()

    yield _driver

    filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    test_status = "passed"
    if prev_failed_tests != request.session.testsfailed:
        test_status = "failed"
        print("URL at time of failure:", _driver.current_url)

    trace_dir = Path.cwd() / "functional-test-traces" / test_status
    trace_dir.mkdir(parents=True, exist_ok=True)

    filename = str(trace_dir / f"{filename_datetime}-{request.function.__name__}.zip")
    _driver.stop_tracing(filename)


@pytest.fixture(scope="module")
def broadcast_client():
    client = BroadcastClient(
        api_key=config["broadcast_service"]["api_key_live"],
        base_url=config["eas_api_url"],
    )
    return client


@pytest.fixture(scope="module")
def api_client():
    client = TestApiClient()
    client.configure_for_internal_client(
        client_id=config["service"]["internal_api_client_id"],
        api_key=config["service"]["internal_api_client_secret"],
        base_url=config["eas_api_url"],
    )
    return client
