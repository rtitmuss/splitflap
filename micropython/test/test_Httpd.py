import unittest
from primary.Httpd import Httpd, decode_url_encoded


def raise_error():
    raise ValueError


class SourceHttpdTest(unittest.TestCase):
    def setUp(self):
        self.get_data_called = False
        self.display_post_called = False

        self.httpd = Httpd({
            "GET /data": lambda request: setattr(self, "get_data_called", True) or (200, b'data', 'text/html'),
            "POST /display": lambda request: setattr(self, "display_post_called", True) or (200, b'', 'text/html'),
            "POST /error": lambda request: raise_error(),
        })

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
        response = self.httpd.process_http_request('POST /display HTTP/1.1\r\n\r\ntext=foo'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))
        self.assertTrue(self.display_post_called)

    def test_process_http_request_get_index_html(self):
        response = self.httpd.process_http_request('GET / HTTP/1.1\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))
        self.assertTrue("text/html".encode('utf-8') in response)

    def test_process_http_request_get_favicon_ico(self):
        response = self.httpd.process_http_request('GET /favicon.ico HTTP/1.1\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))
        self.assertTrue("image/vnd.microsoft.icon".encode('utf-8') in response)

    def test_process_http_request_get_data(self):
        response = self.httpd.process_http_request('GET /data HTTP/1.1\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 200"))
        self.assertTrue(response.endswith("data"))

    def test_process_http_request_bad_request(self):
        response = self.httpd.process_http_request('PUT /\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 400"))

    def test_process_http_request_not_found(self):
        response = self.httpd.process_http_request('GET /missing.html\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 404"))

    def test_process_http_request_server_error(self):
        response = self.httpd.process_http_request('POST /error\r\n\r\n'.encode('utf-8'))
        self.assertTrue(response.startswith("HTTP/1.1 500"))


if __name__ == '__main__':
    unittest.main()
