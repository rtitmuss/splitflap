import unittest

from UartProtocol import UartProtocol


class MockUart:

    def set_buf(self, buf):
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
        self.mock_uart = MockUart()
        self.uartProtocol = UartProtocol(self.mock_uart)

    def test_write(self):
        self.assertEqual(self.uartProtocol.write(b'a'), b'\x7ea\x7e')

    def test_writewith_esc(self):
        self.assertEqual(self.uartProtocol.write(b'a\x7eb\x7e'),
                         b'\x7ea\x7d\x7eb\x7d\x7e\x7e')

    def test_write_frame(self):
        self.assertEqual(
            self.uartProtocol.write_frame(UartProtocol.CMD_SET, 2, 1000,
                                          'foo'),
            b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~')

    def test_uart_write(self):
        self.uartProtocol.uart_write(UartProtocol.CMD_SET, 2, 1000, 'foo')
        self.assertEqual(self.mock_uart.buf,
                         b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~')

    def test_read(self):
        read = self.uartProtocol.read()

        self.assertEqual(read.send(b'\x7e'), None)
        self.assertEqual(read.send(b'a'), None)
        self.assertEqual(read.send(b'\x7e'), b'a')

    def test_read_with_esc(self):
        read = self.uartProtocol.read()

        self.assertEqual(read.send(b'\x7e'), None)
        self.assertEqual(read.send(b'a'), None)
        self.assertEqual(read.send(b'\x7d'), None)
        self.assertEqual(read.send(b'\x7e'), None)
        self.assertEqual(read.send(b'b'), None)
        self.assertEqual(read.send(b'\x7d'), None)
        self.assertEqual(read.send(b'\x7e'), None)
        self.assertEqual(read.send(b'\x7e'), b'a\x7eb\x7e')

    def test_read_sync(self):
        read = self.uartProtocol.read()

        self.assertEqual(read.send(b'b'), None)
        self.assertEqual(read.send(b'\x7e'), None)
        self.assertEqual(read.send(b'a'), None)
        self.assertEqual(read.send(b'\x7e'), b'a')

    def test_read_frame(self):
        read_frame = self.uartProtocol.read_frame()

        for c in b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~':
            frame = read_frame.send(bytes([c]))

        self.assertEqual(frame.cmd, UartProtocol.CMD_SET)
        self.assertEqual(frame.seq, 2)
        self.assertEqual(frame.steps, 1000)
        self.assertEqual(frame.letters, b'foo')

    def test_read_frame_crc_error(self):
        read_frame = self.uartProtocol.read_frame()

        for c in b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooFx~':
            frame = read_frame.send(bytes([c]))

        self.assertEqual(frame, None)

    def test_read_invalid_frame(self):
        read_frame = self.uartProtocol.read_frame()

        for c in b'~\x01\x02foo\x95\xcb~':
            frame = read_frame.send(bytes([c]))

        self.assertEqual(frame, None)

    def test_uart_read(self):
        self.mock_uart.set_buf(b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~')
        frame = self.uartProtocol.uart_read()

        self.assertEqual(frame.cmd, UartProtocol.CMD_SET)
        self.assertEqual(frame.seq, 2)
        self.assertEqual(frame.steps, 1000)
        self.assertEqual(frame.letters, b'foo')

    def test_uart_read_cmd(self):
        self.mock_uart.set_buf(
            b'~\x02\x03\x00\x00\xe8\x03\x00\x00bar\x9d\x05~')
        frame = self.uartProtocol.uart_read(cmd=UartProtocol.CMD_ACK)

        self.assertEqual(frame.cmd, UartProtocol.CMD_ACK)

    def test_uart_read_cmd_not_found(self):
        self.mock_uart.set_buf(b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~')
        frame = self.uartProtocol.uart_read(cmd=UartProtocol.CMD_END)

        self.assertEqual(frame, None)

    def test_uart_read_seq(self):
        self.mock_uart.set_buf(
            b'~\x02\x03\x00\x00\xe8\x03\x00\x00bar\x9d\x05~')
        frame = self.uartProtocol.uart_read(seq=3)

        self.assertEqual(frame.seq, 3)

    def test_uart_read_seq_not_found(self):
        self.mock_uart.set_buf(b'~\x01\x02\x00\x00\xe8\x03\x00\x00fooF,~')
        frame = self.uartProtocol.uart_read(seq=4)

        self.assertEqual(frame, None)


if __name__ == '__main__':
    unittest.main()
