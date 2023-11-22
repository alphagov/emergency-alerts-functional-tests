from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def set_service_id(self, service_id):
        self.service_id = service_id
