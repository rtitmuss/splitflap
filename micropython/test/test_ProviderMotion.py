import unittest

from Message import Message
from provider.ProviderMotion import ProviderMotion


class DisplayMock:
    def display_length(self) -> int:
        return 4


class PythonArtTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderMotion()

    def test_get_message(self):
        message, interval_ms = self.provider.get_message(None, {"rpm":"15"}, self.display, [0, 0, 0, 0])
        self.assertIsInstance(message, Message)
        self.assertEqual(interval_ms, 1)


if __name__ == '__main__':
    unittest.main()
