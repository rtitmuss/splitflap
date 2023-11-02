import unittest
from Message import Message
from SourceHttpd import SourceHttpd, decode_url_encoded

class MockDisplay:
    def adjust_word(self, s):
        return s

    def virtual_to_physical(self, element_position):
        return element_position


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.mock_display = MockDisplay()
        self.source_httpd = SourceHttpd(self.mock_display)

    def test_decode_url_encoded_basic_pairs(self):
        self.assertEqual(decode_url_encoded("name=John&age=30&city=York"),
                         {'name': 'John', 'age': '30', 'city': 'York'})

    def test_decode_url_encoded_special_characters_in_keys(self):
        self.assertEqual(decode_url_encoded("first%20name=John&last+name=Doe"),
                         {'first name': 'John', 'last name': 'Doe'})

    def test_decode_url_encoded_special_characters_in_values(self):
        self.assertEqual(decode_url_encoded("name=John+Doe&comment=This+is+a+test%21&symbol=%24%25%5E"),
                         {'name': 'John Doe', 'comment': 'This is a test!', 'symbol': '$%^'})

    def test_decode_url_encoded_empty_values(self):
        self.assertEqual(decode_url_encoded("name=&age=&city="),
                         {'name': '', 'age': '', 'city': ''})

    def test_decode_url_encoded_missing_values(self):
        self.assertEqual(decode_url_encoded("name=John&city=&comment=Test"),
                         {'name': 'John', 'city': '', 'comment': 'Test'})

    def test_decode_url_encoded_duplicate_keys(self):
        self.assertEqual(decode_url_encoded("name=John&name=Doe&name=Smith"),
                         {'name': 'Smith'})

    def test_process_http_request_post_display(self):
        response = self.source_httpd.process_http_request('POST /display\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))

    def test_process_http_request_get_index_html(self):
        response = self.source_httpd.process_http_request('GET /\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))

    def test_process_http_request_not_found(self):
        response = self.source_httpd.process_http_request('GET /missing.html\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 404"))

    def test_process_http_request_bad_request(self):
        response = self.source_httpd.process_http_request('PUT /\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 400"))

    def test_process_post_display(self):
        self.source_httpd.process_http_request('POST /display\r\n\r\ntext=foo'.encode('utf-8'))
        print(self.source_httpd.queue[0])
        self.assertEqual(self.source_httpd.queue[0], Message(15, [0, 0, 0], [295, 702, 702]))

    def test_process_post_display_with_rpm(self):
        self.source_httpd.process_http_request('POST /display\r\n\r\ntext=foo&rpm=10'.encode('utf-8'))
        self.assertEqual(self.source_httpd.queue[0], Message(10, [0, 0, 0], [295, 702, 702]))


if __name__ == '__main__':
    unittest.main()
