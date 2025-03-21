import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from clients.broadcast_client import BroadcastClient
from clients.test_api_client import TestApiClient
from config import config, setup_shared_config
from tests.pages.pages import HomePage


def pytest_addoption(parser):
    parser.addoption("--no-headless", action="store_true", default=False)


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

    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Selenium")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        },
    )

    if not request.config.getoption("--no-headless"):
        options.add_argument("--headless")

    if http_proxy is not None and http_proxy != "":
        options.add_argument("--proxy-server={}".format(http_proxy))

    service = ChromeService(
        log_path="./logs/chrome_browser.log", service_args=["--verbose"]
    )

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 720)

    driver.delete_all_cookies()

    # go to root page and accept analytics cookies to hide banner in all pages
    driver.get(config["eas_admin_url"])
    HomePage(driver).accept_cookie_warning()
    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope="function")
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    yield _driver
    HomePage(_driver).sign_out_if_required()
    if prev_failed_tests != request.session.testsfailed:
        print("URL at time of failure:", _driver.current_url)
        filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = str(
            Path.cwd()
            / "screenshots"
            / "{}_{}.png".format(filename_datetime, request.function.__name__)
        )
        _driver.save_screenshot(str(filename))
        print("Error screenshot saved to " + filename)


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
