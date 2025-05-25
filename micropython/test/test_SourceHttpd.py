import unittest
from Message import Message
from provider.Provider import Provider
from provider.Clock import Clock
from primary.SourceHttpd import SourceHttpd, decode_url_encoded


class MockDisplay:
    def adjust_word(self, s):
        return s

    def virtual_to_physical(self, element_position):
        return element_position

    def physical_to_virtual(self, element_position):
        return element_position


class MocKWifi:
    def connect(self):
        pass


class MockClock(Clock):
    def __init__(self, year=2024, month=1, day=1, hour=0, minute=0, second=0):
        super().__init__(year, month, day, hour, minute, second)

    @staticmethod
    def now(timezone: str = None):
        return MockClock()  # Return a fixed time for testing


class MockProvider(Provider):
    def __init__(self, message: Message, interval_ms: Union[int, None]):
        self.message = message
        self.interval_ms = interval_ms
        self.called = False

    def get_message(self, word: str, display_data: Dict[str, str], display: Display, motor_position: [int])\
            -> Tuple[Message, Union[int, None]]:
        return self.message, self.interval_ms


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.mock_provider = MockProvider(Message(15, [0], [0]), 60)
        self.mock_clock = MockClock()
        self.source_httpd = SourceHttpd(MocKWifi(), self.mock_display, {
            "{MESSAGE}": self.mock_provider,
        }, self.mock_clock)

    def test_process_post_display(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\ntext=foo'.encode('utf-8'))
        self.assertEqual(status, (200, b'', 'text/html'))
        self.assertEqual(self.source_httpd.display_queue[0], {"text": "foo"})

    def test_process_post_display_bad_request(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\n'.encode('utf-8'))
        self.assertEqual(status, (400, b'', 'text/html'))
        self.assertFalse(self.source_httpd.display_queue)

    def test_display_data_to_message(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "foo"}, [])
        self.assertEqual(message, Message(15, [0, 0, 0], [295, 702, 702]))
        self.assertIsNone(interval_ms)

    def test_display_data_to_message_with_provider(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "{message}"}, [])
        self.assertIsInstance(message, Message)
        self.assertEqual(interval_ms, 60)


if __name__ == '__main__':
    unittest.main()
