from collections import namedtuple
from crc16 import crc16
import select
import struct
import uctypes

SYNC = const(0x7e)
ESC = const(0x7d)

HEADER_FMT = const('BBBBI')
LETTER_FMT = const('sB')
CRC_FMT = const('H')

HEADER_SIZE = struct.calcsize(HEADER_FMT)
LETTER_SIZE = struct.calcsize(LETTER_FMT)
CRC_SIZE = struct.calcsize(CRC_FMT)

Frame = namedtuple(
    "Frame",
    ("cmd", "seq", "rpm", "display_mode", "steps", "letters", "offsets"))


def UartFrame(cmd,
              seq,
              rpm=0,
              display_mode=0,
              steps=0,
              letters='',
              offsets=[]):
    return Frame(cmd, seq, rpm, display_mode, steps, letters, offsets)


def coroutine(func):

    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


def __wrap(buf):
    yield SYNC
    for c in buf:
        if c == SYNC:
            yield ESC
        yield c
    yield SYNC


class UartProtocol:

    CMD_SET = 0x01
    CMD_ACK = 0x02
    CMD_END = 0x03

    def __init__(self, uart):
        self.uart = uart
        self.poll = select.poll()
        try:
            self.poll.register(uart, select.POLLIN)
        except OSError:
            True  # unit test

    def write(self, buf):
        return bytes(__wrap(buf))

    def write_frame(self, frame):
        buf = bytearray(
            struct.pack(HEADER_FMT, frame.cmd, frame.seq, frame.rpm,
                        frame.display_mode, frame.steps))

        for i, letter in enumerate(frame.letters):
            offset = frame.offsets[i] if i < len(frame.offsets) else 0
            buf.extend(struct.pack(LETTER_FMT, letter, offset))

        buf.extend(struct.pack(CRC_FMT, crc16(buf)))
        return self.write(buf)

    def uart_write(self, frame):
        return self.uart.write(self.write_frame(frame))

    @coroutine
    def read(self):
        frame = None
        while True:
            byte = yield frame
            frame = None

            if byte[0] == SYNC:
                buf = bytearray()
                while True:
                    byte = yield
                    if byte[0] == SYNC:
                        frame = bytes(buf)
                        break
                    if byte[0] == ESC:
                        byte = yield
                    buf += byte

    @coroutine
    def read_frame(self):
        reader = self.read()
        byte = yield None
        while True:
            frame = reader.send(byte)
            if frame:
                if crc16(frame) != 0:
                    print('crc error')
                    byte = yield None
                else:
                    n = (len(frame) - HEADER_SIZE - CRC_SIZE) // LETTER_SIZE
                    header = struct.unpack(HEADER_FMT, frame)

                    data = []
                    for i in range(0, n):
                        data += struct.unpack_from(
                            LETTER_FMT, frame, HEADER_SIZE + LETTER_SIZE * i)

                    byte = yield Frame(*header,
                                       b''.join(data[::2]).decode('ascii'),
                                       data[1::2])
            else:
                byte = yield None

    def uart_read(self, cmd=None, seq=None, timeout_ms=None):
        read_frame = self.read_frame()

        while True:
            if timeout_ms:
                if not self.poll.poll(timeout_ms):
                    return  # frame timeout

            byte = self.uart.read(1)
            if not byte:
                return  # char timeout

            frame = read_frame.send(byte)
            if frame:
                if (cmd == None or cmd == frame.cmd) and (seq == None
                                                          or seq == frame.seq):
                    return frame
                else:
                    print('Unexpected frame:', frame)
