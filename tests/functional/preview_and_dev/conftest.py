import pytest

from clients.test_api_client import TestApiClient
from config import config, setup_preview_dev_config


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config():
    """
    Setup
    """
    setup_preview_dev_config()

    _purge_functional_test_alerts()


def _purge_functional_test_alerts():
    client = TestApiClient()
    client.configure_for_internal_client(
        client_id=config["service"]["internal_api_client_id"],
        api_key=config["service"]["internal_api_client_secret"],
        base_url=config["notify_api_url"],
    )
    service = config["broadcast_service"]["service_id"]
    older_than = config["broadcast_service"]["purge_older_than"]
    url = f"/service/{service}/broadcast-message/purge/{older_than}"

    client.get(url)
