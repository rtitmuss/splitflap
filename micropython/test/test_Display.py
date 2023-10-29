import unittest
from Display import Display
from Message import Message


class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.display = Display("bca", [10, 20, 30])

    def test_adjust_word(self):
        self.assertEqual(self.display.adjust_word("a"), "a  ")
        self.assertEqual(self.display.adjust_word("abcd"), "abc")

    def test_virtual_to_physical(self):
        message = self.display.virtual_to_physical(Message(15, [11, 22, 33], [33, 44, 2030]))

        self.assertEqual(message.get_rpm(), 15)
        self.assertEqual(message.get_element_delay(), [33, 11, 22])
        self.assertEqual(message.get_element_position(), [(2030 + 30) % 2038, 33 + 10, 44 + 20])

    def test_physical_to_virtual(self):
        position = self.display.physical_to_virtual([(2030 + 30) % 2038, 33 + 10, 44 + 20])

        self.assertEqual(position, [33, 44, 2030])


if __name__ == '__main__':
    unittest.main()
