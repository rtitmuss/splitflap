import struct
from typing import Union, Tuple, List

from micropython import const

from Message import Message
from UartFrame import UartFrame

_CMD_MSG = const(0xf1)
_CMD_ACK = const(0xf2)


class UartMessage():
    def __init__(self, uart_frame: UartFrame):
        self.uart_frame = uart_frame
        self.send_seq = 0

    def uart(self):
        return self.uart_frame.uart

    def next_seq(self) -> int:
        self.send_seq += 1
        return self.send_seq

    def send_message(self, seq: int, message: Message):
        n = len(message.get_element_position())
        frame = struct.pack('BBB' + 'hh' * n, _CMD_MSG, seq,
                            message.get_rpm(), *message.get_element_delay(), *message.get_element_position())
        self.uart_frame.send_frame(frame)

    def recv_message(self) -> Union[Tuple[int, Message], None]:
        frame = self.uart_frame.recv_frame()
        if frame:
            n = int((len(frame) - 3) / 4)
            data = struct.unpack('BBB' + 'hh' * n, frame)

            if data[0] == _CMD_MSG:
                seq = data[1]
                rpm = data[2]
                element_delay = list(data[3:3+n])
                element_position = list(data[3+n:])
                return seq, Message(rpm, element_delay, element_position)
        else:
            return None

    def send_ack(self, seq: int, is_stopped: bool, motor_position: [int]):
        n = len(motor_position)
        frame = struct.pack('BBB' + 'h' * n, _CMD_ACK, seq, is_stopped, *motor_position)
        self.uart_frame.send_frame(frame)

    def recv_ack(self) -> Union[Tuple[int, bool, List[int]], None]:
        frame = self.uart_frame.recv_frame()
        if frame:
            n = int((len(frame) - 3) / 2)
            data = struct.unpack('BBB' + 'h' * n, frame)

            if data[0] == _CMD_ACK:
                seq = data[1]
                is_stopped = data[2]
                motor_position = list(data[3:])
                return seq, is_stopped, motor_position
        else:
            return None
