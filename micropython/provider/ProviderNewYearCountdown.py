from typing import Union, Tuple

from provider.Clock import Clock
from provider.Provider import Provider


class ProviderNewYearCountdown(Provider):
    def __init__(self, timezone: str):
        self.timezone = timezone

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        now = Clock.now(self.timezone)

        if now.month == 1 and now.day == 1:  # Jan 1st
            return now.strftime("!HAPPY NEWYEAR %Y!"), None

        next_interval_ms = (60 - now.second) * 1000

        delta_hours = 23 - now.hour
        delta_minutes = 59 - now.minute

        if delta_minutes % 2 == 0:
            return f"{now.year+1:04} IN      {delta_hours:02}:{delta_minutes:02} ", next_interval_ms
        else:
            return f"COUNT DOWN    {delta_hours:02}:{delta_minutes:02} ", next_interval_ms
