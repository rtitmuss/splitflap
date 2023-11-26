import requests
from micropython import const

import Message
from Message import LETTERS
from typing import Union, Tuple, List

from primary.Display import Display
from provider.Provider import Provider


class ProviderLetters(Provider):
    def __init__(self):
        self.lines = []

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        if not self.lines:
            num = display.display_length()
            for letter in reversed(Message.LETTERS):
                self.lines.append(letter * num)
            for letter in Message.LETTERS:
                self.lines.append(letter * num)

        word = self.lines.pop(0) if self.lines else ''
        return word, 10000 if self.lines else None
