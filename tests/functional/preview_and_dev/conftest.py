import pytest

from clients.test_api_client import TestApiClient
from config import config, setup_preview_dev_config
from tests.test_utils import (
    put_functional_test_blackout_metric,
    set_response_codes,
)


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config():
    """
    Setup
    """
    setup_preview_dev_config()

    test_api_client = TestApiClient()
    test_api_client.configure_for_internal_client(
        client_id=config["service"]["internal_api_client_id"],
        api_key=config["service"]["internal_api_client_secret"],
        base_url=config["eas_api_url"],
    )

    purge_functional_test_alerts(test_api_client)
    purge_folders_and_templates(test_api_client)
    purge_user_created_services(test_api_client)

    set_response_codes()

    yield

    set_response_codes()
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
