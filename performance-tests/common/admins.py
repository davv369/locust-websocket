from decouple import config
from base import BaseTaskSet


class BaseAdminLoginTaskSet(BaseTaskSet):
    ADMIN_USER = config('ADMIN_USER')
    ADMIN_PASSWORD = config('ADMIN_PASSWORD')

    def __init__(self, parent):
        super().__init__(parent)
        self.admin_auth_headers = None
        self.admin_credentials = {
            "email": self.ADMIN_USER,
            "password": self.ADMIN_PASSWORD
        }
        self.user_id = None
        self.admin_token = None

    def on_start(self):
        self.admin_login()

    def admin_login(self):
        admin_response = self._login(self.admin_credentials)
        self.admin_token = admin_response["accessToken"]
        self.admin_auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
