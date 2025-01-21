import unittest

from provider.Clock import Clock
from provider.ProviderWordClock import ProviderWordClock


class DisplayMock:
    def display_length(self) -> int:
        return 20

    def format_string_left_justified(self, input_str: str) -> List[str]:
        return [input_str]


class PythonWordClockTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderWordClock("en", None, lambda: self.mock_now)

    def test_midnight(self):
        self.mock_now = Clock(2025, 1, 1, 0, 0)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "twelve o-clock")
        self.assertIsInstance(interval_ms, int)

    def test_noon(self):
        self.mock_now = Clock(2025, 1, 1, 12, 0)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "twelve o-clock")
        self.assertIsInstance(interval_ms, int)

    def test_almost_midnight(self):
        self.mock_now = Clock(2025, 1, 1, 23, 55)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "near twelve o-clock")
        self.assertIsInstance(interval_ms, int)

    def test_almost_noon(self):
        self.mock_now = Clock(2025, 1, 1, 11, 55)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "near twelve o-clock")
        self.assertIsInstance(interval_ms, int)

    def test_little_past(self):
        self.mock_now = Clock(2025, 1, 1, 1, 5)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "five past one")
        self.assertIsInstance(interval_ms, int)

    def test_ten_past(self):
        self.mock_now = Clock(2025, 1, 1, 2, 10)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "ten past two")
        self.assertIsInstance(interval_ms, int)

    def test_quarter_past(self):
        self.mock_now = Clock(2025, 1, 1, 3, 15)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "quarter past three")
        self.assertIsInstance(interval_ms, int)

    def test_twenty_past(self):
        self.mock_now = Clock(2025, 1, 1, 4, 20)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "twenty past four")
        self.assertIsInstance(interval_ms, int)

    def test_almost_thirty(self):
        self.mock_now = Clock(2025, 1, 1, 5, 25)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "near five thirty")
        self.assertIsInstance(interval_ms, int)

    def test_half_past(self):
        self.mock_now = Clock(2025, 1, 1, 6, 30)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "half past six")
        self.assertIsInstance(interval_ms, int)

    def test_a_bit_past_thirty(self):
        self.mock_now = Clock(2025, 1, 1, 7, 35)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "past half seven")
        self.assertIsInstance(interval_ms, int)

    def test_twenty_to(self):
        self.mock_now = Clock(2025, 1, 1, 8, 40)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "twenty to nine")
        self.assertIsInstance(interval_ms, int)

    def test_quarter_to(self):
        self.mock_now = Clock(2025, 1, 1, 9, 45)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "quarter to ten")
        self.assertIsInstance(interval_ms, int)

    def test_ten_to(self):
        self.mock_now = Clock(2025, 1, 1, 10, 50)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "ten to eleven")
        self.assertIsInstance(interval_ms, int)

    def test_eight(self):
        self.mock_now = Clock(2025, 1, 1, 8, 30)
        word, interval_ms = self.provider.get_word(None, self.display)
        self.assertEqual(word, "half past eight")
        self.assertIsInstance(interval_ms, int)


if __name__ == '__main__':
    unittest.main()
