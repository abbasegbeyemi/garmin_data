from dataclasses import asdict

import garth

from garmin.auth import AuthClient


class APIClient:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    def get_sleep_data(self, days: int = 7) -> list[dict]:
        sleep_data = garth.DailySleep.list(period=days)
        return [asdict(s) for s in sleep_data]
