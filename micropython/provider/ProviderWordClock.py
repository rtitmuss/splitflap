from typing import Callable, Union, Tuple

from primary.Display import Display
from provider.Clock import Clock
from provider.Provider import Provider

# Inspired from https://github.com/samuelmr/garmin-abouttime

HOUR_STRINGS = {
    "en": [
        "twelve",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
    ],
    "sv": [
        "tolv",  # 12
        "ett",  # 1
        "två",  # 2
        "tre",  # 3
        "fyra",  # 4
        "fem",  # 5
        "sex",  # 6
        "sju",  # 7
        "åtta",  # 8
        "nio",  # 9
        "tio",  # 10
        "elva",  # 11
    ],
}

MINUTE_STRINGS = {
    "en": [
        "{this_hour} o-clock",
        "five past {this_hour}",
        "ten past {this_hour}",
        "quarter past {this_hour}",
        "twenty past {this_hour}",
        "near {this_hour} thirty",
        "half past {this_hour}",
        "past half {this_hour}",
        "twenty to {next_hour}",
        "quarter to {next_hour}",
        "ten to {next_hour}",
        "near {next_hour} o-clock",
    ],
    "sv": [
        "{this_hour} prick",  # "{this_hour} o'clock" (e.g., "tolv prick")
        "strax efter {this_hour}",  # "just after {this_hour}"
        "tio över {this_hour}",  # "ten past {this_hour}"
        "kvart över {this_hour}",  # "quarter past {this_hour}"
        "tjugo över {this_hour}",  # "twenty past {this_hour}"
        "nära halv {this_hour}",  # "near half past {this_hour}"
        "halv {next_hour}",  # "half past {this_hour}"
        "strax efter halv {next_hour}",  # "just after half past {this_hour}"
        "tjugo i {next_hour}",  # "twenty to {next_hour}"
        "kvart i {next_hour}",  # "quarter to {next_hour}"
        "tio i {next_hour}",  # "ten to {next_hour}"
        "strax före {next_hour}",  # "just before {next_hour}"
    ],
}


def remove_diacritics(text: str) -> str:
    replacements = {'å': 'a', 'ä': 'a', 'ö': 'o'}
    return ''.join(replacements.get(char, char) for char in text)


class ProviderWordClock(Provider):
    def __init__(self, clock_mock: Callable = None):
        self.clock_mock = clock_mock

    def get_word(self, args: dict[str, str], display: Display) -> Tuple[str, Union[int, None]]:
        lang = args.get('lang', 'en')
        timezone = args.get('timezone', 'UTC')
        now = self.clock_mock() if self.clock_mock else Clock.timezone(timezone).now()

        hour_strings = HOUR_STRINGS[lang]
        min_strings = MINUTE_STRINGS[lang]

        next_5_minute = (now.minute // 5 + 1) * 5
        remaining_minutes = next_5_minute - now.minute
        remaining_seconds = remaining_minutes * 60 - now.second
        next_interval_ms = remaining_seconds * 1000

        this_hour = hour_strings[now.hour % 12]
        next_hour = hour_strings[(now.hour + 1) % 12]
        word_clock = min_strings[now.minute // 5].format(this_hour=this_hour, next_hour=next_hour)
        word_clock = remove_diacritics(word_clock)

        return display.format_string_left_justified(word_clock)[0], next_interval_ms
