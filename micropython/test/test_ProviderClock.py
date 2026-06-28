import unittest

from provider.ProviderClock import ProviderClock


class DisplayMock:
    def display_length(self) -> int:
        return 20


class MockResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def close(self):
        pass


class RequestsMock:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text
        self.call_count = 0

    def get(self, url, timeout=10):
        self.call_count += 1
        return MockResponse(self.status_code, self.text)


WEATHER_RESPONSE = '{"current":{"temperature_2m":22.3},"hourly":{"weather_code":[0,1,2]}}'
WEATHER_COLD = '{"current":{"temperature_2m":-5.7},"hourly":{"weather_code":[3,71,73]}}'


class PythonClockTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()

    def test_get_word_basic(self):
        provider = ProviderClock()
        word, interval_ms = provider.get_word({"text": "%H.%M", "timezone": "UTC"}, self.display)
        self.assertIsInstance(word, str)
        self.assertIsInstance(interval_ms, int)

    def test_weather_substitution(self):
        mock = RequestsMock(200, WEATHER_RESPONSE)
        provider = ProviderClock(requests_factory=mock)
        provider._fetch_weather("59.33", "18.07")

        result = provider._replace_weather_codes("%t", provider.weather_cache)
        self.assertEqual(result, " 22")

        result = provider._replace_weather_codes("%w", provider.weather_cache)
        self.assertEqual(result, "CLOUDY")

    def test_weather_negative_temp(self):
        mock = RequestsMock(200, WEATHER_COLD)
        provider = ProviderClock(requests_factory=mock)
        provider._fetch_weather("59.33", "18.07")

        result = provider._replace_weather_codes("%t", provider.weather_cache)
        self.assertEqual(result, " -6")

        result = provider._replace_weather_codes("%w", provider.weather_cache)
        self.assertEqual(result, "SNOW  ")

    def test_weather_caching(self):
        mock = RequestsMock(200, WEATHER_RESPONSE)
        provider = ProviderClock(requests_factory=mock)
        provider._fetch_weather("59.33", "18.07")
        self.assertEqual(mock.call_count, 1)

        # Second call should use cache
        provider._fetch_weather("59.33", "18.07")
        self.assertEqual(mock.call_count, 1)

    def test_weather_fetch_failure(self):
        mock = RequestsMock(500, "")
        provider = ProviderClock(requests_factory=mock)
        result = provider._fetch_weather("59.33", "18.07")
        self.assertIsNone(result)
        self.assertEqual(mock.call_count, 3)  # 3 retries

    def test_no_weather_without_lat_lon(self):
        mock = RequestsMock(200, WEATHER_RESPONSE)
        provider = ProviderClock(requests_factory=mock)
        word, _ = provider.get_word({"text": "%H.%M", "timezone": "UTC"}, self.display)
        self.assertEqual(mock.call_count, 0)

    def test_format_with_weather(self):
        mock = RequestsMock(200, WEATHER_RESPONSE)
        provider = ProviderClock(requests_factory=mock)
        word, _ = provider.get_word({
            "text": "%H:%M  %d.%m%w  %tC",
            "timezone": "UTC",
            "lat": "59.33",
            "lon": "18.07"
        }, self.display)
        self.assertIn("22", word)
        self.assertEqual(mock.call_count, 1)


if __name__ == '__main__':
    unittest.main()
