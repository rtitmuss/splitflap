import unittest
from UartFrame import UartFrame


class UartMock():
    def __init__(self):
        self.pos = None
        self.buffer = None

    def any(self):
        return len(self.buffer) - self.pos

    def read(self, n):
        byte = self.buffer[self.pos:self.pos + n]
        self.pos += n
        return byte

    def write(self, buffer):
        self.buffer = buffer
        self.pos = 0


class UartFrameTest(unittest.TestCase):
    def setUp(self):
        self.uartMock = UartMock()
        self.uartFrame = UartFrame(self.uartMock)

    def test_send_frame(self):
        self.uartFrame.send_frame(b'ab\x7E\x7Dcd')
        self.assertEqual(self.uartMock.buffer, [0x7e, 0x61, 0x62, 0x7d, 0x7e, 0x7d, 0x7d, 0x63, 0x64, 0x7e])

    def test_recv_frame(self):
        self.uartMock.write(b'\x7Eab\x7D\x7E\x7D\x7Dcd\x7E')
        frame = self.uartFrame.recv_frame()
        self.assertEqual(frame, b'ab\x7E\x7Dcd')


if __name__ == '__main__':
    unittest.main()
