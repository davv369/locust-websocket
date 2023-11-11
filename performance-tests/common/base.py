import uuid
from utils import DEFAULTS_HEADERS
from locust import TaskSet


class BaseTaskSet(TaskSet):

    def _send(self, url, credentials):
        return self.client.post(
            url=url,
            json=credentials,
            headers=DEFAULTS_HEADERS,
        ).json()

    def _login(self, credentials: dict):
        return self._send(f"/users/auth/login", credentials)

    @staticmethod
    def str_uuid() -> str:
        return str(uuid.uuid4())
