import urllib.parse

from notifications_python_client.authentication import create_jwt_token
from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def __init__(self, api_key, base_url):
        super().__init__(api_key=api_key, base_url=base_url)

    def _create_request_objects(self, url, data, params):
        api_token = create_jwt_token(self.api_key, "dev-notify-secret-key")

        kwargs = {"headers": self.generate_headers(api_token), "timeout": self.timeout}

        if data is not None:
            kwargs.update(data=self._serialize_data(data))

        if params is not None:
            kwargs.update(params=params)

        url = urllib.parse.urljoin(str(self.base_url), str(url))

        return url, kwargs
