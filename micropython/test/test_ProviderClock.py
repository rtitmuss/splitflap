import unittest

from provider.ProviderClock import ProviderClock


class DisplayMock:
    def display_length(self) -> int:
        return 20


class PythonClockTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderClock("%H.%M", None)

    def test_get_word(self):
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertIsInstance(word, str)
        self.assertIsInstance(interval_ms, int)


if __name__ == '__main__':
    unittest.main()
