import unittest

from ProviderClock import ProviderClock


class DisplayMock:
    def display_length(self) -> int:
        return 20


class PythonClockTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderClock("%H.%M", None)

    def test_get_work_or_message(self):
        word_or_message, interval_ms = self.provider.get_word_or_message(None, None, self.display, None)
        self.assertIsInstance(word_or_message, str)
        self.assertIsInstance(interval_ms, int)


if __name__ == '__main__':
    unittest.main()
