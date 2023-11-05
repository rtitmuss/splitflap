from typing import Tuple

import requests
import time

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class Clock:
    utc_offset_sec = {}

    def __init__(self, year: int = 1970, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0):
        # use time.mktime / time.localtime to handle under/overflow
        t0 = time.mktime([year, month, day, hour, minute, second, 0, 0])  # weekday, yearday are unused
        t1 = time.localtime(t0)

        self.year = t1[0]
        self.month = t1[1]
        self.day = t1[2]
        self.hour = t1[3]
        self.minute = t1[4]
        self.second = t1[5]
        self.weekday = t1[6]

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

    def add(self, year: int = 0, month: int = 0, day: int = 0, hour: int = 0, minute: int = 0, second: int = 0):
        # overflow and underflow is handled in the constructor
        return Clock(self.year + year,
                     self.month + month,
                     self.day + day,
                     self.hour + hour,
                     self.minute + minute,
                     self.second + second)

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
                    result += _DAYS[self.weekday]
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
