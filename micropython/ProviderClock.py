import time

from Display import Display
from Message import Message
from Provider import Provider
from typing import Union, Tuple


class ProviderClock(Provider):
    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
            -> Union[Tuple[str, int], Tuple[Message, int]]:
        (year, month, mday, hour, minute, second) = time.localtime()[:6]
        word = "     {:02d}:{:02d}{:02d}.{:02d}.{:04d}".format(hour, minute, mday, month, year)
        interval_ms = (60 - second) * 1000
        return word, interval_ms
