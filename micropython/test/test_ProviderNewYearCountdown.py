import unittest

from provider.Clock import Clock
from provider.ProviderNewYearCountdown import ProviderNewYearCountdown


class DisplayMock:
    def display_length(self) -> int:
        return 20


class PythonNewYearCountdownTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderNewYearCountdown("Europe/Stockholm", lambda: self.mock_now)

    def test_dec31_even_minute(self):
        self.mock_now = Clock(2024, 12, 31, 22, 0)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, " NEW YEAR " "IN  1H 59M")
        self.assertEqual(interval_ms, 60000)

    def test_dec31_odd_minute(self):
        self.mock_now = Clock(2024, 12, 31, 22, 1)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "2025 SOON:" "    1H 58M")
        self.assertEqual(interval_ms, 60000)

    def test_last_minute(self):
        self.mock_now = Clock(2024, 12, 31, 23, 59, 30)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "BYE 2024: " "  23:59:30")
        self.assertEqual(interval_ms, 1)

    def test_new_year(self):
        self.mock_now = Clock(2025, 1, 1, 1, 1)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "!HAPPY NEW" "YEAR 2025!")
        self.assertIsNone(interval_ms)

    def test_jan2(self):
        self.mock_now = Clock(2025, 1, 2, 1, 1)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, " 2026  IN " "  363D 22H")
        self.assertEqual(interval_ms, 3540000)

    def test_jan2_leap(self):
        self.mock_now = Clock(2028, 1, 2, 1, 1)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, " 2029  IN " "  364D 22H")
        self.assertEqual(interval_ms, 3540000)

    def test_dec30(self):
        self.mock_now = Clock(2025, 12, 30, 1, 1)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, " 2026  IN " "    1D 22H")
        self.assertEqual(interval_ms, 3540000)


if __name__ == '__main__':
    unittest.main()
