import requests
from micropython import const

from Message import LETTERS
from typing import Union, Tuple, List

from primary.Display import Display
from provider.Provider import Provider

_URL = const("https://icanhazdadjoke.com")
_HEADERS = {"Accept": "text/plain",
            "User-Agent": "Splitflap (https://github.com/rtitmuss/splitflap)"}
_REQUEST_TIMEOUT = const(10)  # seconds to wait for a response


class ProviderDadJoke(Provider):
    def __init__(self, requestsFactory=requests):
        self.requests = requestsFactory
        self.lines = []

    def get_dad_joke(self) -> Union[str, None]:
        response = None
        try:
            response = self.requests.get(_URL, headers=_HEADERS, timeout=_REQUEST_TIMEOUT)
            if response.status_code == 200:
                joke = response.text.replace('\n', ' ').strip()

                # filter characters using LETTERS
                return ''.join(char for char in joke.upper() if char in LETTERS)
            else:
                return f"ERR: {response.status_code}!"
        except Exception as e:
            print(f"[DADJOKE] Request error {e}")
        finally:
            if response:
                response.close()
        return None

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        if not self.lines:
            joke = self.get_dad_joke()
            if joke:
                self.lines = display.format_string_left_justified(joke)

        joke_line = self.lines.pop(0) if self.lines else ''
        return joke_line, 14000 if self.lines else None
