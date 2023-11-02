from UartMessage import UartMessage
from typing import Union, Tuple, List

import unittest
from ElementUart import ElementUart
from Message import Message


class UartMessageMock():
    def __init__(self):
        self.seq = None
        self.message = None
        self.ack = []

    def uart(self):
        return 9876

    def next_seq(self) -> int:
        return 0

    def send_message(self, seq: int, message: Message):
        self.seq = seq
        self.message = message
        self.ack.append([seq, True, message.get_element_position()])

    def recv_ack(self) -> Union[Tuple[int, bool, List[int]], None]:
        return self.ack.pop(0) if self.ack else None


class ElementUartTest(unittest.TestCase):
    def setUp(self):
        self.uartMessageMock = UartMessageMock()
        self.elementUart = ElementUart(self.uartMessageMock)
        self.message = Message(15, [0], [1])

    def test_unknown_state(self):
        self.elementUart.step()
        self.assertTrue(self.elementUart.is_stopped())
        self.assertEqual(self.elementUart.get_motor_position(), [])

    def test_send_empty_message(self):
        self.elementUart.set_message(Message(15, [], []))
        self.assertTrue(self.elementUart.is_stopped())
        self.assertEqual(self.elementUart.get_motor_position(), [])

    def test_set_message_with_ack(self):
        self.elementUart.set_message(self.message)

        self.assertEqual(self.message, self.uartMessageMock.message)
        self.assertEqual(len(self.uartMessageMock.ack), 0)
        self.assertTrue(len(self.elementUart.get_motor_position()) > 0)

    def test_set_message_no_ack(self):
        self.uartMessageMock.ack.append(None)

        self.elementUart.set_message(self.message)

        self.assertEqual(self.message, self.uartMessageMock.message)
        self.assertEqual(len(self.uartMessageMock.ack), 1)
        self.assertEqual(self.elementUart.get_motor_position(), [])

    def test_set_message_with_ack_wrong_seq(self):
        self.uartMessageMock.ack.append([-1, True, [0]])
        self.elementUart.set_message(self.message)

        self.assertEqual(self.message, self.uartMessageMock.message)
        self.assertEqual(len(self.uartMessageMock.ack), 0)
        self.assertTrue(len(self.elementUart.get_motor_position()) > 0)

    def test_set_message_upstream_motor_position_unknown(self):
        self.uartMessageMock.ack.append([0, False, [-1]])
        self.elementUart.set_message(self.message)

        self.assertEqual(self.elementUart.count, 2038)

    def test_set_message_upstream_is_running(self):
        self.uartMessageMock.ack.append([0, False, [0]])
        self.elementUart.set_message(self.message)

        self.assertEqual(self.elementUart.count, 2038)

    def test_set_message_upstream_forward_step(self):
        self.uartMessageMock.ack.append([0, True, [0]])
        self.elementUart.set_message(Message(15, [0], [1]))

        self.assertEqual(self.elementUart.count, 1)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_forward_step_with_delay(self):
        self.uartMessageMock.ack.append([0, True, [0]])
        self.elementUart.set_message(Message(15, [1], [1]))

        self.assertEqual(self.elementUart.count, 2)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_backward_step(self):
        self.uartMessageMock.ack.append([0, True, [2]])
        self.elementUart.set_message(Message(15, [0], [1]))

        self.assertEqual(self.elementUart.count, 2037)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_backward_step_with_delay(self):
        self.uartMessageMock.ack.append([0, True, [2]])
        self.elementUart.set_message(Message(15, [1], [1]))

        self.assertEqual(self.elementUart.count, 2038)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_no_step(self):
        self.uartMessageMock.ack.append([0, True, [1]])
        self.elementUart.set_message(Message(15, [0], [1]))

        self.assertEqual(self.elementUart.count, 0)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_no_step_with_delay(self):
        self.uartMessageMock.ack.append([0, True, [1]])
        self.elementUart.set_message(Message(15, [1], [1]))

        self.assertEqual(self.elementUart.count, 1)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_force_step(self):
        self.uartMessageMock.ack.append([0, True, [1]])
        self.elementUart.set_message(Message(15, [0], [2039]))

        self.assertEqual(self.elementUart.count, 2038)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])

    def test_set_message_upstream_force_step_with_delay(self):
        self.uartMessageMock.ack.append([0, True, [1]])
        self.elementUart.set_message(Message(15, [1], [2039]))

        self.assertEqual(self.elementUart.count, 2039)

        while not self.elementUart.is_stopped():
            self.elementUart.step()
        self.assertEqual(self.elementUart.get_motor_position(), [1])


if __name__ == '__main__':
    unittest.main()
