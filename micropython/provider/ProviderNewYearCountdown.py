from typing import Callable, Union, Tuple

from provider.Clock import Clock
from provider.Provider import Provider

# Number of days in each month for a common year (non-leap year)
DAYS_IN_MONTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DAYS_IN_MONTHS_LEAP_YEAR = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _days_to_new_year(year: int, month: int, day: int) -> int:
    is_leap_year = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    days_in_months = DAYS_IN_MONTHS_LEAP_YEAR if is_leap_year else DAYS_IN_MONTHS

    days_passed = sum(days_in_months[:month - 1]) + day
    total_days_in_year = 366 if is_leap_year else 365

    return total_days_in_year - days_passed


class ProviderNewYearCountdown(Provider):
    def __init__(self, timezone: str, clock_now: Callable = None):
        self.clock_now = clock_now if clock_now else lambda: Clock.now(timezone)

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        now = self.clock_now()

        if now.month == 1 and now.day == 1:  # Jan 1st
            return now.strftime("!HAPPY NEW" "YEAR %Y!"), None

        if now.month == 12 and now.day == 31 and now.hour == 23 and now.minute == 59:  # last minute
            return f"BYE {now.year:04}:   {now.hour:02}:{now.minute:02}:{now.second:02}", 1

        if now.month == 12 and now.day == 31:  # last day
            next_interval_ms = (60 - now.second) * 1000
            delta_hours = 23 - now.hour
            delta_minutes = 59 - now.minute

            if delta_minutes % 2 == 0:
                return f"{now.year+1:04} SOON:   {delta_hours:2}H {delta_minutes:02}M", next_interval_ms
            else:
                return f" NEW YEAR IN {delta_hours:2}H {delta_minutes:02}M", next_interval_ms

        next_interval_ms = ((59 - now.minute) * 60 + (60 - now.second)) * 1000
        delta_days = _days_to_new_year(now.year, now.month, now.day)
        delta_hours = 23 - now.hour
        return f" {now.year+1:04}  IN   {delta_days:3}D {delta_hours:02}H", next_interval_ms
