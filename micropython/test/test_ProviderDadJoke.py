import unittest

from provider.ProviderDadJoke import ProviderDadJoke


class DisplayMock:
    def display_length(self) -> int:
        return 20

    def format_string_left_justified(self, input_str: str) -> List[str]:
        input_str_mid = int(len(input_str) / 2)
        return [input_str[:input_str_mid], input_str[input_str_mid:]]


class TestProviderDadJoke(unittest.TestCase):
    def setUp(self):
        self.mockDisplay = DisplayMock()
        self.provider = ProviderDadJoke()

    def test_get_word(self):
        word, interval_ms = self.provider.get_word('', self.mockDisplay)
        self.assertIsInstance(word, str)
        self.assertIsInstance(interval_ms, int)


if __name__ == '__main__':
    unittest.main()
