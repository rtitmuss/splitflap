import random

from Display import Display
from Message import Message
from Provider import Provider
from typing import Union, Tuple


class ProviderArt(Provider):
    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
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
