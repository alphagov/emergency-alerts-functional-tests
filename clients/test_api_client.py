import logging

from notifications_python_client.base import BaseAPIClient, logger


class TestApiClient(BaseAPIClient):
    __test__ = False

    def __init__(self):
        super().__init__("a" * 73, "b")

        # The logger will warn on non-200 requests, which commonly happens when we
        # purge admin elevation so let's just silence the noise.
        logger.setLevel(logging.ERROR)

    def configure_for_internal_client(self, client_id, api_key, base_url):
        self.service_id = client_id
        self.api_key = api_key
        self.base_url = base_url
