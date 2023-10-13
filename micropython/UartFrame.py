from typing import Union

from micropython import const
try:
    from machine import UART
except ImportError:
    UART = None  # Error occurs during unit test

_SYNC = const(0x7e)
_ESC = const(0x7d)


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def _read_frame():
    frame = None
    while True:
        byte = yield frame
        frame = None

        if byte[0] == _SYNC:
            buf = bytearray()
            while True:
                byte = yield
                if byte[0] == _SYNC:
                    frame = bytes(buf)
                    break
                if byte[0] == _ESC:
                    byte = yield
                buf += byte


class UartFrame:
    def __init__(self, uart: UART):
        self.uart = uart

    def send_frame(self, frame: bytearray):
        esc_frame = [_SYNC]
        for byte in frame:
            if byte == _SYNC:
                esc_frame.extend([_ESC, _SYNC])
            elif byte == _ESC:
                esc_frame.extend([_ESC, _ESC])
            else:
                esc_frame.append(byte)
        esc_frame.append(_SYNC)
        self.uart.write(bytes(esc_frame))

    def recv_frame(self) -> Union[bytearray, None]:
        read_frame = _read_frame()

        while True:
            byte = self.uart.read(1)
            if not byte:
                return  # char timeout

            frame = read_frame.send(byte)
            if frame:
                return frame
