from collections import namedtuple
from crc16 import crc16
import select
import struct
import uctypes

SYNC = const(0x7e)
ESC = const(0x7d)

HDR_FMT = const('BBI')
CRC_FMT = const('H')

Frame = namedtuple("Frame", ("cmd", "seq", "steps", "letters"))


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

    def write_frame(self, *args):
        buf = bytearray(struct.pack(HDR_FMT, *args[0:-1]))
        buf.extend(args[-1])
        buf.extend(struct.pack(CRC_FMT, crc16(buf)))
        return self.write(buf)

    def uart_write(self, *args):
        return self.uart.write(self.write_frame(*args))

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
        hdr_size = struct.calcsize(HDR_FMT)
        crc_size = struct.calcsize(CRC_FMT)

        reader = self.read()
        byte = yield None
        while True:
            frame = reader.send(byte)
            if frame:
                if crc16(frame) != 0:
                    print('crc error')
                    byte = yield None
                else:
                    unpacked = struct.unpack(HDR_FMT, frame)
                    letters = frame[hdr_size:-crc_size]
                    byte = yield Frame(*unpacked, letters)
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
