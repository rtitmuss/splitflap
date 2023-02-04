import unittest

from UartProtocol import UartProtocol


class MockUart:

    def __init__(self, buf=None):
        self.buf = buf
        self.pos = 0

    def any(self):
        return len(self.buf) - self.pos

    def read(self, n):
        byte = self.buf[self.pos:self.pos + n]
        self.pos += n
        return byte

    def write(self, buf):
        self.buf = buf


class TestUartProtocol(unittest.TestCase):

    def setUp(self):
        self.uartProtocol = UartProtocol()

    def test_write_frame(self):
        self.assertEqual(self.uartProtocol.write_frame(b'a'), b'\x7ea\x7e')

    def test_write_frame_with_esc(self):
        self.assertEqual(self.uartProtocol.write_frame(b'a\x7eb\x7e'),
                         b'\x7ea\x7d\x7eb\x7d\x7e\x7e')

    def test_write(self):
        self.assertEqual(
            self.uartProtocol.write(UartProtocol.CMD_SET, 2, 'foo'),
            b'~\x01\x02foo\x95\xbb~')

    def test_uart_write(self):
        mock_uart = MockUart()
        self.uartProtocol.uart_write(mock_uart, UartProtocol.CMD_SET, 2, 'foo')
        self.assertEqual(mock_uart.buf, b'~\x01\x02foo\x95\xbb~')

    def test_read_frame(self):
        read_frame = self.uartProtocol.read_frame()

        self.assertEqual(read_frame.send(b'\x7e'), None)
        self.assertEqual(read_frame.send(b'a'), None)
        self.assertEqual(read_frame.send(b'\x7e'), b'a')

    def test_read_frame_with_esc(self):
        read_frame = self.uartProtocol.read_frame()

        self.assertEqual(read_frame.send(b'\x7e'), None)
        self.assertEqual(read_frame.send(b'a'), None)
        self.assertEqual(read_frame.send(b'\x7d'), None)
        self.assertEqual(read_frame.send(b'\x7e'), None)
        self.assertEqual(read_frame.send(b'b'), None)
        self.assertEqual(read_frame.send(b'\x7d'), None)
        self.assertEqual(read_frame.send(b'\x7e'), None)
        self.assertEqual(read_frame.send(b'\x7e'), b'a\x7eb\x7e')

    def test_read_frame_sync(self):
        read_frame = self.uartProtocol.read_frame()

        self.assertEqual(read_frame.send(b'b'), None)
        self.assertEqual(read_frame.send(b'\x7e'), None)
        self.assertEqual(read_frame.send(b'a'), None)
        self.assertEqual(read_frame.send(b'\x7e'), b'a')

    def test_read(self):
        read = self.uartProtocol.read()

        for c in b'~\x01\x02foo\x95\xbb~':
            frame = read.send(bytes([c]))

        self.assertEqual(frame.cmd, UartProtocol.CMD_SET)
        self.assertEqual(frame.seq, 2)
        self.assertEqual(frame.letters, b'foo')

    def test_read(self):
        read = self.uartProtocol.read()

        for c in b'~\x01\x02foo\x95\xcb~':
            frame = read.send(bytes([c]))

        self.assertEqual(frame, None)

    def test_uart_read(self):
        mock_uart = MockUart(b'~\x01\x02foo\x95\xbb~')
        frame = self.uartProtocol.uart_read(mock_uart)

        self.assertEqual(frame.cmd, UartProtocol.CMD_SET)
        self.assertEqual(frame.seq, 2)
        self.assertEqual(frame.letters, b'foo')

    def test_uart_read_cmd(self):
        mock_uart = MockUart(b'~\x01\x02foo\x95\xbb~~\x02\x03barU\xef~')
        frame = self.uartProtocol.uart_read(mock_uart,
                                            cmd=UartProtocol.CMD_ACK)

        self.assertEqual(frame.cmd, UartProtocol.CMD_ACK)

    def test_uart_read_cmd_not_found(self):
        mock_uart = MockUart(b'~\x01\x02foo\x95\xbb~~\x02\x03barU\xef~')
        frame = self.uartProtocol.uart_read(mock_uart,
                                            cmd=UartProtocol.CMD_END)

        self.assertEqual(frame, None)

    def test_uart_read_seq(self):
        mock_uart = MockUart(b'~\x01\x02foo\x95\xbb~~\x02\x03barU\xef~')
        frame = self.uartProtocol.uart_read(mock_uart, seq=3)

        self.assertEqual(frame.seq, 3)

    def test_uart_read_seq_not_found(self):
        mock_uart = MockUart(b'~\x01\x02foo\x95\xbb~~\x02\x03barU\xef~')
        frame = self.uartProtocol.uart_read(mock_uart, seq=4)

        self.assertEqual(frame, None)


if __name__ == '__main__':
    unittest.main()
