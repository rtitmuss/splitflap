import unittest

from SourceWords import SourceWords


class SourceWordsTest(unittest.TestCase):
    def setUp(self):
        self.source_words = SourceWords(["apple", "banana", "cherry", "date", "elderberry", "fig"], None)

    def test_pick_random_words(self):
        self.assertLessEqual(len(self.source_words.pick_random_words(20)), 20)


if __name__ == '__main__':
    unittest.main()
