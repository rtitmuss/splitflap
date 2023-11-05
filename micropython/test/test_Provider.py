import unittest

from Message import Message
from Provider import Provider


class MockDisplay:
    def adjust_word(self, s):
        return s

    def virtual_to_physical(self, element_position):
        return element_position

    def physical_to_virtual(self, element_position):
        return element_position


class OverloadedProvider(Provider):
    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        return "def", 60


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.provider = Provider()

    def test_get_word(self):
        self.assertEqual(self.provider.get_word("[{ABC", self.mock_display), ("ABC", None))

    def test_get_message(self):
        self.assertEqual(self.provider.get_message("ABC", {}, self.mock_display, []),
                         (Message(15, [0, 0, 0], [68, 114, 159]), None))

    def test_get_message_with_rpm(self):
        self.assertEqual(self.provider.get_message("ABC", {}, self.mock_display, []),
                         (Message(15, [0, 0, 0], [68, 114, 159]), None))

    def test_get_message_with_interval_ms(self):
        self.assertEqual(OverloadedProvider().get_message("ABC", {}, self.mock_display, []),
                         (Message(15, [0, 0, 0], [204, 250, 295]), 60))

    def test_get_message_with_random(self):
        message, interval_ms = self.provider.get_message("ABC", {"order": "random"}, self.mock_display, [])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)

    def test_get_message_with_sweep(self):
        message, interval_ms = self.provider.get_message("ABC", {"order": "sweep"}, self.mock_display, [])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)

    def test_get_message_with_diagonal_sweep(self):
        message, interval_ms = self.provider.get_message("ABC", {"order": "diagonal_sweep"}, self.mock_display, [])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)

    def test_get_message_with_end_in_sync(self):
        message, interval_ms = self.provider.get_message("ABC", {"order": "end_in_sync"}, self.mock_display, [])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)


if __name__ == '__main__':
    unittest.main()
