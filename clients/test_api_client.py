from notifications_python_client.base import BaseAPIClient


class TestApiClient(BaseAPIClient):
    def __init__(self, timeout=30):
        super().__init__("a" * 73, "b", timeout=timeout)

    def configure_for_internal_client(self, client_id, api_key, base_url):
        self.service_id = client_id
        self.api_key = api_key
        self.base_url = base_url
