import micropython
import select

from typing import Union

from Message import Message
from Source import Source
from UartMessage import UartMessage


class SourceUart(Source):
    def __init__(self, uart_message: UartMessage):
        self.uart_message = uart_message
        self.uart = uart_message.uart()
        self.poll = select.poll()
        self.poll.register(self.uart, select.POLLIN)
        self.seq = 0

    @micropython.native
    def load_message(self, is_stopped: bool, motor_position: [int]) -> Union[Message, None]:
        if self.poll.poll(1000 if is_stopped else 0):
            return self.load_message_uart(is_stopped, motor_position)

    def load_message_uart(self, is_stopped: bool, motor_position: [int]) -> Union[Message, None]:
        recv = self.uart_message.recv_message()
        if recv:
            seq, message = recv
            if message:
                self.uart_message.send_ack(seq, is_stopped, motor_position)
                return message
