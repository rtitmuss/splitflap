import random

from Display import Display
from Message import Message
from Provider import Provider
from typing import Union, Tuple


class ProviderArt(Provider):
    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
            -> Union[Tuple[str, int], Tuple[Message, int]]:
        display_len = display.display_length()
        pattern = []
        for i in range(display_len):
            pattern.append(random.choice(' $&#'))

        pattern[random.randint(0, display_len - 1)] = 'X'
        pattern[random.randint(0, display_len - 1)] = 'O'
        pattern[random.randint(0, display_len - 1)] = '-'

        word = ''.join(pattern)
        interval_ms = 5 * 60 * 1000
        return word, interval_ms
