import unittest

from provider.ProviderDadJoke import ProviderDadJoke


class DisplayMock:
    def display_length(self) -> int:
        return 20

    def format_string_left_justified(self, input_str: str) -> List[str]:
        if (len(input_str) > 20):
            return [input_str[:20], input_str[20:]]
        else:
            return [input_str]


class MockResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def close(self):
        pass


class RequestsMock:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def get(self, url, headers, timeout):
        return MockResponse(self.status_code, self.text)


class TestProviderDadJoke(unittest.TestCase):
    def setUp(self):
        self.mockDisplay = DisplayMock()

    def test_get_word_success(self):
        text = "\nWhere do cats write notes?\nScratch Paper!"
        provider = ProviderDadJoke(requestsFactory=RequestsMock(200, text))
        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "WHERE DO CATS WRITE ")
        self.assertEqual(interval_ms, 14000)

        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "NOTES? SCRATCH PAPER!")
        self.assertIsNone(interval_ms)

    def test_http_error_response(self):
        provider = ProviderDadJoke(requestsFactory=RequestsMock(404, "Not found"))
        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "ERR: 404!")
        self.assertIsNone(interval_ms)

    def test_network_exception(self):
        class RequestsMockException:
            def get(self, url, headers, timeout):
                raise Exception("Network down")

        provider = ProviderDadJoke(requestsFactory=RequestsMockException())
        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "")
        self.assertIsNone(interval_ms)

    def test_empty_or_whitespace_joke(self):
        provider = ProviderDadJoke(requestsFactory=RequestsMock(200, "\n   \n  "))
        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "")
        self.assertIsNone(interval_ms)

    def test_joke_with_no_valid_characters(self):
        provider = ProviderDadJoke(requestsFactory=RequestsMock(200, "@%^*()"))
        word, interval_ms = provider.get_word('', self.mockDisplay)
        self.assertEqual(word, "")
        self.assertIsNone(interval_ms)


if __name__ == '__main__':
    unittest.main()
