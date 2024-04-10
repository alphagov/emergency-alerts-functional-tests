import pytest

from clients.test_api_client import TestApiClient
from config import config, setup_preview_dev_config

test_api_client = TestApiClient()
test_api_client.configure_for_internal_client(
    client_id=config["service"]["internal_api_client_id"],
    api_key=config["service"]["internal_api_client_secret"],
    base_url=config["eas_api_url"],
)


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config():
    """
    Setup
    """
    setup_preview_dev_config()

    _purge_functional_test_alerts()
    _purge_folders_and_templates()
    _purge_user_created_services()


def _purge_functional_test_alerts():
    service = config["broadcast_service"]["service_id"]
    older_than = config["broadcast_service"]["purge_older_than"]

    url = f"/service/{service}/broadcast-message/purge/{older_than}"
    test_api_client.delete(url)


def _purge_folders_and_templates():
    service = config["broadcast_service"]["service_id"]

    url = f"/service/{service}/template/purge"
    test_api_client.delete(url)


def _purge_user_created_services():
    admin_user = config["broadcast_service"]["platform_admin"]["id"]

    url = f"/service/purge-services-created/{admin_user}"
    test_api_client.delete(url)
