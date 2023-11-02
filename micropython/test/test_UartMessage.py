import unittest
from Message import Message
from UartFrame import UartFrame
from UartMessage import UartMessage


class UartFrameMock(UartFrame):
    def __init__(self, uart):
        super().__init__(uart)
        self.buffer = ''

    def uart(self) -> int:
        return 0

    def send_frame(self, frame: bytearray):
        self.buffer = frame

    def recv_frame(self) -> bytearray:
        return self.buffer


class UartMessageTest(unittest.TestCase):
    def setUp(self):
        self.uart_frame = UartFrameMock(0)
        self.uart_message = UartMessage(self.uart_frame)

    def test_message(self):
        send_message = Message(15, [1, 2, 3], [7, 8, 9])
        self.uart_message.send_message(99, send_message)
        seq, recv_message = self.uart_message.recv_message()
        self.assertEqual(seq, 99)
        self.assertEqual(send_message, recv_message)

    def test_message_timeout(self):
        self.uart_message.buffer = None
        result = self.uart_message.recv_message()
        self.assertIsNone(result)

    def test_ack(self):
        self.uart_message.send_ack(99, True, [1, 2, 3])
        seq, is_stopped, motor_position = self.uart_message.recv_ack()
        self.assertEqual(seq, 99)
        self.assertEqual(is_stopped, True)
        self.assertEqual(motor_position, [1, 2, 3])

    def test_ack_timeout(self):
        self.uart_message.buffer = None
        result = self.uart_message.recv_ack()
        self.assertIsNone(result)

    def test_next_seq(self):
        seq1 = self.uart_message.next_seq()
        seq2 = self.uart_message.next_seq()
        self.assertEqual(seq1 + 1, seq2)


if __name__ == '__main__':
    unittest.main()
