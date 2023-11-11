import socketio
from locust import HttpUser, task, between
from decouple import config


class GameUser(HttpUser):
    wait_time = between(1, 2)

    def __init__(self, envirement):
        super().__init__(envirement)
        self.player_id = None
        self.accessToken = None
        self._url = config('WS_URL')
        self._socket = socketio.Client()
        self.is_white = False
        self.game_id = None

    def user_data(self):
        i = self.environment.runner.user_count
        return i

    def on_start(self):
        i = self.user_data()
        email = f"performancechecker{i}@example.com"
        headers = {"Content-Type": "application/json"}
        payload = {"email": email, "password": config('PASSWORD')}

        resp = self.client.post(
            "/users/auth/login",
            json=payload,
            headers=headers,
        )
        response_data = resp.json()
        self.accessToken = response_data.get("accessToken")
        user_data = response_data.get("user")
        self.player_id = user_data.get("_id")

        def ws_connect():
            self._socket.connect(self._url, auth={"token": self.accessToken})

        ws_connect()

    @task
    def start_game_session(self):
        url = config("PARING_URL")
        payload = {
            "baseTimeMs": 240000,
            "extraTimeMs": 0,
            "timeControl": "BLITZ"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.accessToken}"
        }
        resp = self.client.post(url=url, json=payload, headers=headers)
        response_data = resp.json()
        status_message = response_data.get('message')
        if status_message == 'ok':
            pass

        @self._socket.on('game-found')
        def handle_game_found(game_data):
            self.game_id = game_data.get("_id")
            player1_data = game_data.get("PLAYER_1", {})
            player2_data = game_data.get("PLAYER_2", {})
            self.game_player1_id = player1_data.get("userId")
            self.game_player2_id = player2_data.get("userId")
            if self.game_player1_id == self.player_id:
                self.is_white = True
            else:
                self.is_white = False
            if self.game_player1_id or self.game_player2_id == self.player_id:
                join_url = f"/game-mgmt/games/{self.game_id}/join"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.accessToken}"
                }

                self.client.post(url=join_url, headers=headers)

        @self._socket.on('game-started')
        def handle_game_started(game_data):
            self.game_id = game_data.get("_id")
            player1_data = game_data.get("PLAYER_1", {})
            self.game_player1_id = player1_data.get("userId")
            if self.is_white:
                self.move_payload1 = "Nf3"
                move_url = config("MOVE_URL")
                self.client.post(url=move_url,
                                 json={"move": {"id": self.game_id, "user_id": self.player_id,
                                                "move": self.move_payload1}},
                                 headers=headers)
            if not self.is_white:
                pass


