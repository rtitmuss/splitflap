import unittest
from Message import Message
from primary.Display import Display, ljust, split_string_by_length, combine_lines_for_display


class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.display = Display(["bc", "a"], [10, 20, 30])

    def test_display_length(self):
        self.assertEqual(self.display.display_length(), 3)

    def test_adjust_word(self):
        self.assertEqual(self.display.adjust_word("a"), "a  ")
        self.assertEqual(self.display.adjust_word("abcd"), "abc")

    def test_format_string_left_justified(self):
        input_str = "Th i a longer str."
        result = self.display.format_string_left_justified(input_str)
        expected = ["Thi ", "a lo", "nger", "str."]
        self.assertEqual(result, expected)

    def test_virtual_to_physical(self):
        message = self.display.virtual_to_physical(Message(15, [11, 22, 33], [33, 44, 2030]))

        self.assertEqual(message.get_rpm(), 15)
        self.assertEqual(message.get_element_delay(), [33, 11, 22])
        self.assertEqual(message.get_element_position(), [(2030 + 30) % 2038, 33 + 10, 44 + 20])

    def test_physical_to_virtual(self):
        position = self.display.physical_to_virtual([(2030 + 30) % 2038, 33 + 10, 44 + 20])

        self.assertEqual(position, [33, 44, 2030])

    def test_ljust(self):
        self.assertEqual(ljust("hello", 10), "hello     ")
        self.assertEqual(ljust("longer", 5), "longer")

    def test_split_string_by_length(self):
        input_string = "This is a longer string that needs to be split into lines."
        result = split_string_by_length(input_string, 10)
        expected = ["This is a", "longer", "string", "that needs", "to be", "split into", "lines."]
        self.assertEqual(result, expected)

    def test_split_string_by_length_short_string(self):
        input_string = "Short"
        result = split_string_by_length(input_string, 10)
        self.assertEqual(result, ["Short"])

    def test_split_string_by_length_exact_length(self):
        input_string = "ExactlyTen"
        result = split_string_by_length(input_string, 10)
        self.assertEqual(result, ["ExactlyTen"])

    def test_split_string_by_length_long_words(self):
        input_string = "ThisIsALongWord ThatNeedsToBeSplitIntoLines."
        result = split_string_by_length(input_string, 10)
        self.assertEqual(result, ["ThisIsALon", "gWord", "ThatNeedsT", "oBeSplitIn", "toLines."])

    def test_combine_lines_for_display(self):
        lines = ["short", "longer  line", "another", "test"]
        result = combine_lines_for_display(lines, 2, 12)
        expected = ["short       longer  line", "another     test        "]
        self.assertEqual(result, expected)

    def test_combine_lines_for_display_remaining(self):
        lines = ["short", "longer  line", "another", "test", "extra"]
        result = combine_lines_for_display(lines, 2, 12)
        expected = ["short       longer  line", "another     test        ", "extra       "]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
