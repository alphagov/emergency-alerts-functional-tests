from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def get(self, url):
        return self.request(method="GET", url=url)
