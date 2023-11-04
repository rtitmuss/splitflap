from Clock import Clock
from Display import Display
from Message import Message
from Provider import Provider
from typing import Union, Tuple


class ProviderClock(Provider):
    def __init__(self, format: str, timezone: str):
        self.format = format
        self.timezone = timezone

    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
            -> Union[Tuple[str, int], Tuple[Message, int]]:
        clock = Clock.now(self.timezone)
        next_interval_ms = (60 - clock.second) * 1000
        return clock.strftime(self.format), next_interval_ms
