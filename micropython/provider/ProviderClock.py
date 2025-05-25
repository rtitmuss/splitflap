from typing import Union, Tuple

from primary.Display import Display
from provider.Clock import Clock
from provider.Provider import Provider


class ProviderClock(Provider):
    def __init__(self, format: str, timezone: str):
        self.format = format
        self.timezone = timezone

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        clock = Clock.timezone(self.timezone).now()
        next_interval_ms = (60 - clock.second) * 1000
        return clock.strftime(self.format), next_interval_ms
