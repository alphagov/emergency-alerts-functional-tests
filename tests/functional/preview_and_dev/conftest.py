import logging
import time

import pytest
from notifications_python_client.errors import HTTPError

from clients.test_api_client import TestApiClient
from config import config, setup_preview_dev_config
from tests.test_utils import (
    clear_proxy_error_alarm,
    put_functional_test_blackout_metric,
    set_response_codes,
)


def create_test_client():
    test_api_client = TestApiClient()
    test_api_client.configure_for_internal_client(
        client_id=config["service"]["internal_api_client_id"],
        api_key=config["service"]["internal_api_client_secret"],
        base_url=config["eas_api_url"],
    )
    return test_api_client


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config():
    """
    Setup
    """
    logging.info(str(time.time()) + " Setting up preview_dev_config")
    setup_preview_dev_config()
    test_api_client = create_test_client()
    purge_functional_test_alerts(test_api_client)
    purge_folders_and_templates(test_api_client)
    purge_user_created_services(test_api_client)
    purge_users_created_by_functional_tests(test_api_client)
    # purge_password_history(test_api_client, config["broadcast_service"]["broadcast_user_3"]["id"])
    platform_admin_ids = [
        config["broadcast_service"]["platform_admin"]["id"],
        config["broadcast_service"]["platform_admin_2"]["id"],
    ]
    for user_id in platform_admin_ids:
        purge_admin_actions_created_by_functional_tests(test_api_client, user_id)
        reset_platform_admin_redemption(test_api_client, user_id)
    purge_failed_logins_created_by_functional_tests(test_api_client)
    yield
    logging.info(str(time.time()) + " Tearing down preview_dev_config")


@pytest.fixture(scope="module")
def cbc_blackout():
    put_functional_test_blackout_metric(500)
    time.sleep(10)
    set_response_codes()
    yield
    set_response_codes()
    clear_proxy_error_alarm()
    time.sleep(90)
    put_functional_test_blackout_metric(200)


def purge_functional_test_alerts(test_api_client):
    service = config["broadcast_service"]["service_id"]
    older_than = config["broadcast_service"]["purge_older_than"]

    url = f"/service/{service}/broadcast-message/purge/{older_than}"
    test_api_client.delete(url)


def purge_folders_and_templates(test_api_client):
    service = config["broadcast_service"]["service_id"]

    url = f"/service/{service}/template/purge"
    test_api_client.delete(url)


def purge_user_created_services(test_api_client):
    admin_user = config["broadcast_service"]["platform_admin"]["id"]

    url = f"/service/purge-services-created/{admin_user}"
    test_api_client.delete(url)


def purge_users_created_by_functional_tests(test_api_client):
    url = "/service/purge-users-created-by-tests"
    test_api_client.delete(url)


def purge_admin_actions_created_by_functional_tests(test_api_client, user_id):
    url = f"/admin-action/purge/{user_id}"
    test_api_client.delete(url)


def purge_failed_logins_created_by_functional_tests(test_api_client):
    url = "/service/purge-failed-logins-created-by-tests"
    test_api_client.delete(url)


def purge_password_history(test_api_client, user_id):
    url = f"/user/{user_id}/purge-password-history"
    test_api_client.delete(url)


def reset_platform_admin_redemption(test_api_client, user_id):
    url = f"/user/{user_id}/redeem-elevation"
    try:
        test_api_client.post(url, data={})
    except HTTPError:
        pass  # May return an error if there's no redemption, but that's ok


# A fixture that can be called ad-hoc in tests known to trigger throttling
@pytest.fixture
def purge_failed_logins():
    return lambda: purge_failed_logins_created_by_functional_tests(create_test_client())
