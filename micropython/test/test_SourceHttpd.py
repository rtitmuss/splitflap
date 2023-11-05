
import unittest
from Message import Message
from Provider import Provider
from SourceHttpd import SourceHttpd, decode_url_encoded


class MockDisplay:
    def adjust_word(self, s):
        return s

    def virtual_to_physical(self, element_position):
        return element_position

    def physical_to_virtual(self, element_position):
        return element_position


class MockProvider(Provider):
    def __init__(self, word_or_message: Union[str, Message], interval_ms: Union[int, None]):
        self.word_or_message = word_or_message
        self.interval_ms = interval_ms

    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
            -> Union[Tuple[str, int], Tuple[Message, int]]:
        return self.word_or_message, self.interval_ms


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.source_httpd = SourceHttpd(self.mock_display, {
            "{WORD}": MockProvider("", 60),
            "{MESSAGE}": MockProvider(Message(15, [0], [0]), None),
        })

    def test_process_post_display(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\ntext=foo'.encode('utf-8'))
        self.assertEqual(status, (200, b''))
        self.assertEqual(self.source_httpd.display_queue[0], {"text": "foo"})

    def test_process_post_display_bad_request(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\n'.encode('utf-8'))
        self.assertEqual(status, (400, b''))
        self.assertFalse(self.source_httpd.display_queue)

    def test_display_data_to_message(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "foo"}, [])
        self.assertEqual(message, Message(15, [0, 0, 0], [295, 702, 702]))
        self.assertIsNone(interval_ms)

    def test_display_data_to_message_with_rpm(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "foo", "rpm": "10"}, [])
        self.assertEqual(message, Message(10, [0, 0, 0], [295, 702, 702]))
        self.assertIsNone(interval_ms)

    def test_display_data_to_message_with_word(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "{word}"}, [])
        self.assertIsInstance(message, Message)
        self.assertIsInstance(interval_ms, int)

    def test_display_data_to_message_with_message(self):
        message, interval_ms = self.source_httpd.display_data_to_message({"text": "{message}"}, [])
        self.assertIsInstance(message, Message)
        self.assertIsNone(interval_ms)


if __name__ == '__main__':
    unittest.main()
