import gc
import json
import requests
import time

from micropython import const
from typing import Union, Tuple

from Message import LETTERS
from primary.Display import Display
from provider.Clock import Clock
from provider.Provider import Provider

_WEATHER_URL = const("https://api.open-meteo.com/v1/forecast")
_WEATHER_PARAMS = const("&current=temperature_2m,is_day&hourly=weather_code&forecast_hours=3")
_REQUEST_TIMEOUT = const(10)
_MAX_RETRIES = const(3)
_CACHE_MS = const(600_000)  # 10 minutes

# WMO weather codes to short descriptions
_WEATHER_CODES = {
    0: "SUNNY", 1: "SUNNY", 2: "CLOUDY", 3: "CLOUDY",
    45: "FOG", 48: "FOG",
    51: "DRZZLE", 53: "DRZZLE", 55: "DRZZLE",
    61: "RAIN", 63: "RAIN", 65: "RAIN",
    66: "FZRAIN", 67: "FZRAIN",
    71: "SNOW", 73: "SNOW", 75: "SNOW", 77: "SNOW",
    80: "SHOWER", 81: "SHOWER", 82: "SHOWER",
    85: "SLEET", 86: "SLEET",
    95: "STORM", 96: "STORM", 99: "STORM",
}


class ProviderClock(Provider):
    def __init__(self, requests_factory=requests):
        self.requests = requests_factory
        self.weather_cache = None
        self.weather_cache_time = None

    def _fetch_weather(self, lat: str, lon: str) -> Union[dict, None]:
        # Return cached weather if still fresh
        if self.weather_cache and self.weather_cache_time:
            if time.ticks_diff(time.ticks_ms(), self.weather_cache_time) < _CACHE_MS:
                return self.weather_cache

        url = f"{_WEATHER_URL}?latitude={lat}&longitude={lon}{_WEATHER_PARAMS}"

        for attempt in range(_MAX_RETRIES):
            response = None
            try:
                gc.collect()
                response = self.requests.get(url, timeout=_REQUEST_TIMEOUT)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    current = data.get("current", {})
                    hourly = data.get("hourly", {})
                    codes = hourly.get("weather_code", [])
                    self.weather_cache = {
                        "temperature_2m": current.get("temperature_2m"),
                        "weather_code": max(codes) if codes else None,
                        "is_day": current.get("is_day", 1),
                    }
                    self.weather_cache_time = time.ticks_ms()
                    print(f"[WEATHER] Updated: {self.weather_cache}")
                    return self.weather_cache
                else:
                    print(f"[WEATHER] HTTP {response.status_code}")
            except Exception as e:
                print(f"[WEATHER] Error (attempt {attempt + 1}/{_MAX_RETRIES}): {e}")
            finally:
                if response:
                    response.close()

        return self.weather_cache  # return stale cache on failure

    def _replace_weather_codes(self, text: str, weather: dict) -> str:
        if not weather:
            text = text.replace("%t", "  ?")
            text = text.replace("%w", "?     ")
            return text

        temp = weather.get("temperature_2m")
        if temp is not None:
            text = text.replace("%t", f"{int(round(temp)):3d}")

        code = weather.get("weather_code")
        if code is not None:
            desc = _WEATHER_CODES.get(code, "?")
            if desc == "SUNNY" and not weather.get("is_day", 1):
                desc = "CLEAR"
            text = text.replace("%w", f"{desc:6s}")

        return text

    def get_word(self, args: dict[str, str], display: Display) -> Tuple[str, Union[int, None]]:
        text = args.get('text', '')
        timezone = args.get('timezone', 'UTC')
        lat = args.get('lat', '')
        lon = args.get('lon', '')

        # Substitute weather codes before strftime
        if lat and lon and ('%t' in text or '%w' in text):
            weather = self._fetch_weather(lat, lon)
            text = self._replace_weather_codes(text, weather)

        clock = Clock.timezone(timezone).now()
        clock_str = clock.strftime(text)
        clean_str = ''.join(char for char in clock_str.upper() if char in LETTERS)

        next_interval_ms = (60 - clock.second) * 1000
        return clean_str, next_interval_ms
