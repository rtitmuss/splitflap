import unittest

from provider.ProviderArt import ProviderArt


class DisplayMock:
    def display_length(self) -> int:
        return 20


class PythonArtTest(unittest.TestCase):
    def setUp(self):
        self.display = DisplayMock()
        self.provider = ProviderArt()

    def test_get_word(self):
        word_or_message, interval_ms = self.provider.get_word(None, self.display)
        self.assertIsInstance(word_or_message, str)
        self.assertEqual(interval_ms, 300000)


if __name__ == '__main__':
    unittest.main()
