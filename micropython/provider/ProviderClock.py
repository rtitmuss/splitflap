from typing import Union, Tuple

from Message import LETTERS

from primary.Display import Display
from provider.Clock import Clock
from provider.Provider import Provider


class ProviderClock(Provider):
    def get_word(self, args: dict[str, str], display: Display) -> Tuple[str, Union[int, None]]:
        text = args.get('text', '')
        timezone = args.get('timezone', 'UTC')

        clock = Clock.timezone(timezone).now()
        clock_str = clock.strftime(text)
        clean_str = ''.join(char for char in clock_str.upper() if char in LETTERS)

        next_interval_ms = (60 - clock.second) * 1000
        return clean_str, next_interval_ms
