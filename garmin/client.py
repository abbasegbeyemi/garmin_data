from dataclasses import asdict
from datetime import date

import garth

from garmin.auth import AuthClient


class APIClient:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    def get_sleep_data(self, date_start: date, lookback_days: int = 7) -> list[dict]:
        sleep_data = garth.SleepData.list(date_start, lookback_days)
        return [asdict(s) for s in sleep_data]
