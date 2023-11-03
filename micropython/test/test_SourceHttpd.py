import unittest
from Message import Message
from SourceHttpd import SourceHttpd, decode_url_encoded

class MockDisplay:
    def adjust_word(self, s):
        return s

    def virtual_to_physical(self, element_position):
        return element_position

    def physical_to_virtual(self, element_position):
        return element_position


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.source_httpd = SourceHttpd(self.mock_display)

    def test_process_post_display(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\ntext=foo'.encode('utf-8'))
        self.assertEqual(status, (200, b''))
        self.assertEqual(self.source_httpd.queue[0], {"text": "foo"})

    def test_process_post_display_bad_request(self):
        status = self.source_httpd.process_post_display('POST /display\r\n\r\n'.encode('utf-8'))
        self.assertEqual(status, (400, b''))
        self.assertFalse(self.source_httpd.queue)

    def test_form_data_to_message(self):
        message = self.source_httpd.form_data_to_message({"text": "foo"}, [])
        self.assertEqual(message, Message(15, [0, 0, 0], [295, 702, 702]))

    def test_form_data_to_message_with_rpm(self):
        message = self.source_httpd.form_data_to_message({"text": "foo", "rpm": "10"}, [])
        self.assertEqual(message, Message(10, [0, 0, 0], [295, 702, 702]))


if __name__ == '__main__':
    unittest.main()
