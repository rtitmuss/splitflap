import requests
import time
import json
import os

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

_TIMEZONE_CACHE_FILE = "timezone_cache.json"
_TIMEZONE_REQUEST_TIMEOUT = 10  # seconds
_TIMEZONE_CACHE_MAX_AGE = 6 * 60 * 60  # 6 hours in seconds


class Clock:
    timezone_data = {}

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
    def now():
        now = time.gmtime()
        return Clock(now[0], now[1], now[2], now[3], now[4], now[5])

    @staticmethod
    def _load_timezone_cache():
        try:
            with open(_TIMEZONE_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                Clock.timezone_data = cache_data.get('timezones', {})
        except OSError:
            # File does not exist
            Clock.timezone_data = {}
        except Exception as e:
            print(f"[TIMEZONE] Error loading cache: {e}")
            Clock.timezone_data = {}

    @staticmethod
    def _save_timezone_cache():
        try:
            cache_data = {'timezones': Clock.timezone_data}
            with open(_TIMEZONE_CACHE_FILE, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"[TIMEZONE] Error saving cache: {e}")

    @staticmethod
    def _fetch_timezone_data(timezone: str):
        last_updated = time.time()

        # First attempt: timeapi.io
        response = None
        try:
            response = requests.get(
                'https://timeapi.io/api/TimeZone/zone?timeZone={}'.format(timezone),
                timeout=_TIMEZONE_REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data and 'currentUtcOffset' in data and 'seconds' in data['currentUtcOffset']:
                    return {
                        'current_offset': data['currentUtcOffset']['seconds'],
                        'last_updated': last_updated
                    }
            elif response.status_code == 404:
                raise ValueError("Invalid timezone")
        except Exception as e:
            print(f"[TIMEZONE] timeapi.io failed: {e}")
        finally:
            if response:
                response.close()

        # Second attempt: WorldTimeAPI
        response = None
        try:
            response = requests.get(
                'http://worldtimeapi.org/api/timezone/{}'.format(timezone),
                timeout=_TIMEZONE_REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if 'raw_offset' in data and 'dst_offset' in data:
                    offset_sec = data['raw_offset'] + data['dst_offset']
                    return {'current_offset': offset_sec, 'last_updated': last_updated}
            elif response.status_code == 404:
                raise ValueError("Invalid timezone")
        except Exception as e:
            print(f"[TIMEZONE] WorldTimeAPI failed: {e}")
        finally:
            if response:
                response.close()

        return None

    @staticmethod
    def timezone(timezone: str):
        if not Clock.timezone_data:
            Clock._load_timezone_cache()

        current_time = time.time()
        timezone_info = Clock.timezone_data.get(timezone)

        # Update cache if data is missing or too old
        if not timezone_info or (current_time - timezone_info.get('last_updated', 0)) > _TIMEZONE_CACHE_MAX_AGE:
            timezone_info = Clock._fetch_timezone_data(timezone)
            if timezone_info:
                Clock.timezone_data[timezone] = timezone_info
                Clock._save_timezone_cache()

        if not timezone_info:
            return Clock

        offset_sec = timezone_info.get('current_offset', 0)

        class TimezoneClock(Clock):
            @staticmethod
            def now():
                now = time.gmtime()
                return Clock(now[0], now[1], now[2], now[3], now[4], now[5] + offset_sec)

        return TimezoneClock

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
