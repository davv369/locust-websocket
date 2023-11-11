from locust import HttpUser, FastHttpUser
from common.users import GameUser
from decouple import config
from locust import HttpUser, constant

HOST = config("HOST", default="", cast=str)


class DefaultUser(FastHttpUser):
    abstract = True
    host = HOST


class LoginUser(DefaultUser):
    tasks = [GameUser]
