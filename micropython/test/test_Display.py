import unittest
from Display import Display
from Message import Message


class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.display = Display("ba", [10, 20])

    def test_adjust_word(self):
        self.assertEqual(self.display.adjust_word("a"), "a ")
        self.assertEqual(self.display.adjust_word("abc"), "ab")

    def test_virtual_to_physical(self):
        message = self.display.virtual_to_physical(Message(15, [11, 22], [33, 2030]))

        self.assertEqual(message.get_rpm(), 15)
        self.assertEqual(message.get_element_delay(), [22, 11])
        self.assertEqual(message.get_element_position(), [12, 43])

    def test_physical_to_virtual(self):
        position = self.display.physical_to_virtual([12, 43])

        self.assertEqual(position, [33, 2030])


if __name__ == '__main__':
    unittest.main()
