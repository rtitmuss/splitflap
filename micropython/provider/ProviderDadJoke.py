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


def get_dad_jokes() -> Union[List[str], None]:
    response = None
    try:
        response = requests.get(_URL, headers=_HEADERS, timeout=_REQUEST_TIMEOUT)
        if response.status_code == 200:
            jokes = response.text.split('\n')

            # filter characters using LETTERS
            jokes = list(map(lambda joke: ''.join(char for char in joke.upper() if char in LETTERS), jokes))
        else:
            jokes = [f"Err: {response.status_code}"]
        return jokes
    except Exception as e:
        print(f"[DADJOKE] Request error {e}")
    finally:
        if response:
            response.close()
    return []


class ProviderDadJoke(Provider):
    def __init__(self):
        self.lines = []
        self.jokes = []

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        if not self.lines:
            if not self.jokes:
                self.jokes = get_dad_jokes()

            if self.jokes:
                self.lines = display.format_string_left_justified(self.jokes.pop(0))

        joke_word = self.lines.pop(0) if self.lines else ''
        return joke_word, 14000 if self.lines else None
