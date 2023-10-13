import unittest
from Message import Message


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.message = Message(rpm=5, element_delay=[1, 2, 3], element_position=[5, 6, 7])

    def test_get_rpm(self):
        self.assertEqual(self.message.get_rpm(), 5)

    def test_get_element_delay(self):
        self.assertEqual(self.message.get_element_delay(), [1, 2, 3])

    def test_get_element_position(self):
        self.assertEqual(self.message.get_element_position(), [5, 6, 7])

    def test_equal(self):
        self.assertEqual(self.message, Message(5, [1, 2, 3], [5, 6, 7]))
        self.assertNotEqual(self.message, Message(15, [1, 2, 3], [5, 6, 7]))
        self.assertNotEqual(self.message, Message(5, [11, 2, 3], [5, 6, 7]))
        self.assertNotEqual(self.message, Message(5, [1, 2, 3], [15, 6, 7]))

    def test_index(self):
        self.assertEqual(self.message[1], Message(5, [2], [6]))

    def test_slice(self):
        self.assertEqual(self.message[1:], Message(5, [2, 3], [6, 7]))

    def test_slice_out_of_range(self):
        self.assertTrue(not self.message[5:])

    def test_word_starting_in_sync(self):
        self.assertEqual(Message.word_starting_in_sync(15, "hello"),
                         Message(15, [0, 0, 0, 0, 0], [385, 250, 567, 567, 702]))

if __name__ == '__main__':
    unittest.main()
