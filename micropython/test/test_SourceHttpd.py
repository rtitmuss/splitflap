import unittest
from typing import Union, Tuple, Dict, List

from Message import Message
from provider.Provider import Provider
from provider.Clock import Clock
from primary.Display import Display
from primary.SourceHttpd import SourceHttpd


class MockDisplay:
    def __init__(self):
        self.rows = 1
        self.cols = 3
        self.physical_indices = [0, 1, 2]
        self.virtual_indices = [0, 1, 2]
        self.display_offsets = [0, 0, 0]

    def display_length(self) -> int:
        return len(self.physical_indices)

    def adjust_word(self, s):
        return s[:3].ljust(3)

    def virtual_to_physical(self, message):
        return message

    def physical_to_virtual(self, motor_position):
        return motor_position

    def format_string_left_justified(self, input_str):
        return [input_str[:3].ljust(3)]


class MockWifi:
    def connect(self):
        pass


class MockClock(Clock):
    def __init__(self, year=2024, month=1, day=1, hour=0, minute=0, second=0):
        super().__init__(year, month, day, hour, minute, second)

    @staticmethod
    def now(timezone: str = None):
        return MockClock()


class MockProvider(Provider):
    def __init__(self, message: Message, interval_ms: Union[int, None]):
        self.message = message
        self.interval_ms = interval_ms

    def get_message(self, args: Dict[str, str], display: Display, motor_position: List[int])\
            -> Tuple[Message, Union[int, None]]:
        return self.message, self.interval_ms


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.mock_provider = MockProvider(Message(15, [0], [0]), 60)
        self.mock_clock = MockClock()
        self.source_httpd = SourceHttpd(MockWifi(), self.mock_display, {
            "MESSAGE": self.mock_provider,
        }, self.mock_clock)

    def test_process_post_display_with_text(self):
        status = self.source_httpd.process_post_display(b'text=foo')
        self.assertEqual(status, (200, b'', 'text/plain'))
        self.assertEqual(self.source_httpd.override_message, {"text": "foo"})

    def test_process_post_display_with_format(self):
        status = self.source_httpd.process_post_display(b'format=ART')
        self.assertEqual(status, (200, b'', 'text/plain'))
        self.assertEqual(self.source_httpd.override_message, {"format": "ART"})

    def test_process_post_display_bad_request(self):
        status = self.source_httpd.process_post_display(b'')
        self.assertEqual(status, (400, b'', 'text/plain'))
        self.assertIsNone(self.source_httpd.override_message)

    def test_display_data_to_message(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "foo"}, [0, 0, 0])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)

    def test_display_data_to_message_with_provider(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"format": "MESSAGE"}, [0, 0, 0])
        self.assertEqual(message, self.mock_provider.message)
        self.assertEqual(interval_ms, 60)


if __name__ == '__main__':
    unittest.main()
