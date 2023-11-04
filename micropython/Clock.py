from typing import Tuple

import requests
import time

_DAYS = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _boundary(x: int, y: int, min: int, max: int) -> Tuple[int, int]:
    while x < min:
        x += max
        y -= 1
    while x >= max:
        x -= max
        y += 1
    return x, y


class Clock:
    utc_offset_sec = {}

    def __init__(self, year: int = 1970, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0):
        second, minute = _boundary(second, minute, 0, 60)
        minute, hour = _boundary(minute, hour, 0, 60)
        hour, day = _boundary(hour, day, 1, 24)
        # todo correct day, month & year overflow
        day, month = _boundary(day, month, 1, 31)

        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    @staticmethod
    def now(timezone: str = None):
        # todo daylight saving time changes
        if timezone and timezone not in Clock.utc_offset_sec:
            Clock.get_timezone(timezone)

        offset_sec = Clock.utc_offset_sec.get(timezone, 0)

        now = time.gmtime()
        return Clock(now[0], now[1], now[2], now[3], now[4], now[5]).add(second=offset_sec)

    @staticmethod
    def get_timezone(timezone: str):
        response = requests.get(
            'https://timeapi.io/api/TimeZone/zone?timeZone={}'.format(timezone))

        if response.status_code == 200:
            data = response.json()
            if data:
                if 'currentUtcOffset' in data and 'seconds' in data['currentUtcOffset']:
                    Clock.utc_offset_sec[timezone] = data['currentUtcOffset']['seconds']
        if response.status_code == 404:
            raise ValueError("Invalid timezone")

        response.close()

    def __str__(self):
        return self.strftime('%Y-%m-%d %H:%M:%S')

    def __eq__(self, clock):
        return (self.year == clock.year and
                self.month == clock.month and
                self.day == clock.day and
                self.hour == clock.hour and
                self.minute == clock.minute and
                self.second == clock.second)

    def add(self, hour: int = 0, minute: int = 0, second: int = 0):
        # overflow and underflow is handled in the constructor
        return Clock(self.year,
                     self.month,
                     self.day,
                     self.hour + hour,
                     self.minute + minute,
                     self.second + second)

    # Zeller's Congruence algorithm returns an integer from 0 (Saturday) to 6 (Friday)
    def day_of_week(self):
        if self.month < 3:
            self.month += 12
            self.year -= 1

        k = self.year % 100
        j = self.year // 100

        return (self.day + 13 * (self.month + 1) // 5 + k + k // 4 + j // 4 - 2 * j) % 7

    def strftime(self, format: str) -> str:
        i = 0
        result = []
        len_format = len(format)
        while i < len_format:
            if format[i] == '%' and i + 1 < len_format:
                if format[i + 1] == 'Y':
                    result += '{:04d}'.format(self.year)
                    i += 2
                elif format[i + 1] == 'm':
                    result += '{:02d}'.format(self.month)
                    i += 2
                elif format[i + 1] == 'd':
                    result += '{:02d}'.format(self.day)
                    i += 2
                elif format[i + 1] == 'H':
                    result += '{:02d}'.format(self.hour)
                    i += 2
                elif format[i + 1] == 'I':
                    if self.hour == 0:
                        hour_12 = 12
                    elif self.hour > 12:
                        hour_12 = self.hour - 12
                    else:
                        hour_12 = self.hour
                    result += '{:02d}'.format(hour_12)
                    i += 2
                elif format[i + 1] == 'M':
                    result += '{:02d}'.format(self.minute)
                    i += 2
                elif format[i + 1] == 'S':
                    result += '{:02d}'.format(self.second)
                    i += 2
                elif format[i + 1] == 'a':
                    result += _DAYS[self.day_of_week()]
                    i += 2
                elif format[i + 1] == 'b':
                    result += _MONTHS[self.month - 1]
                    i += 2
                elif format[i + 1] == 'p':
                    result += ('AM' if self.hour < 12 else 'PM')
                    i += 2
                elif format[i + 1] == '%':
                    result += '%'
                    i += 2
                else:
                    result += format[i]
                    i += 1
            else:
                result += format[i]
                i += 1

        return ''.join(result)
