from pathlib import Path

import garth
from garth.exc import GarthException


class AuthClient:
    def __init__(self, token_dir=".garth"):
        self.token_dir = token_dir

    def is_logged_in(self) -> bool:
        garth.resume(self.token_dir)
        try:
            garth.client.username
        except GarthException:
            return False
        return True

    def login(self) -> None:
        garth.login(self.token_dir)

    def logout(self) -> None:
        Path(".garth").unlink()
