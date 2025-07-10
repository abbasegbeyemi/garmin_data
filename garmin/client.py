from dataclasses import asdict
from datetime import date, datetime
from typing import Literal, Optional

from garminconnect import Garmin


class GarminClient:
    def __init__(self, token_dir: str = ".garth"):
        self.token_dir = token_dir
        self._garmin = None

    @property
    def garmin(self) -> Garmin:
        if self._garmin is None:
            self._garmin = Garmin()
        return self._garmin

    def login(self) -> None:
        self.garmin.login(self.token_dir)
        print(f"Logged in to Garmin as {self.garmin.get_full_name()}")

    def get_sleep_data(self, when: datetime) -> dict:
        sleep_data = self.garmin.get_sleep_data(when.date().isoformat())
        return sleep_data

    def get_activities(
        self,
        from_date: datetime,
        to_date: datetime,
        activity_type: Optional[
            Literal[
                "cycling",
                "running",
                "swimming",
                "multi_sport",
                "fitness_equipment",
                "hiking",
                "walking",
                "other",
            ]
        ] = "running",
    ) -> list[dict]:
        activities = self.garmin.get_activities_by_date(
            from_date.date().isoformat(),
            to_date.date().isoformat(),
            activity_type,
        )
        return activities

    # def get_running_data(self, date_start: date, lookback_days: int = 7) -> list[dict]:
    #     running_data = self.garmin.get_running_data(date_start, lookback_days)
    #     return [asdict(r) for r in running_data]

    # def get_running_data(self, date_start: date, lookback_days: int = 7) -> list[dict]:
    #     running_data = garth.RunningData.list(date_start, lookback_days)
    #     return [asdict(r) for r in running_data]
