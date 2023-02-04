from collections import namedtuple
from crc16 import crc16
import struct
import uctypes

SYNC = const(0x7e)
ESC = const(0x7d)

HDR_FMT = const('BB')
CRC_FMT = const('H')

Frame = namedtuple("Frame", ("cmd", "seq", "letters"))


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

    def write_frame(self, buf):
        return bytes(__wrap(buf))

    def write(self, cmd, seq, letters):
        buf = bytearray(struct.pack(HDR_FMT, cmd, seq))
        buf.extend(letters)
        buf.extend(struct.pack(CRC_FMT, crc16(buf)))
        return self.write_frame(buf)

    def uart_write(self, uart, *args):
        return uart.write(self.write(*args))

    @coroutine
    def read_frame(self):
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
    def read(self):
        hdr_size = struct.calcsize(HDR_FMT)
        crc_size = struct.calcsize(CRC_FMT)

        reader = self.read_frame()
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

    def uart_read(self, uart, cmd=None, seq=None, timeout=0):
        read = self.read()

        while True:
            byte = uart.read(1)
            if not byte:
                return  # timeout

            frame = read.send(byte)
            if frame and (cmd == None or cmd
                          == frame.cmd) and (seq == None or seq == frame.seq):
                return frame
