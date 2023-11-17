from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")
