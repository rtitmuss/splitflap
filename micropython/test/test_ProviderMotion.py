import unittest

from Message import Message
from ProviderMotion import ProviderMotion


class DisplayMock:
    def display_length(self) -> int:
        return 4


class PythonArtTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderMotion()

    def test_get_work_or_message(self):
        word_or_message, interval_ms = self.provider.get_word_or_message(None, 15, self.display, [0, 0, 0, 0])
        self.assertIsInstance(word_or_message, Message)
        self.assertEqual(interval_ms, 1)


if __name__ == '__main__':
    unittest.main()
