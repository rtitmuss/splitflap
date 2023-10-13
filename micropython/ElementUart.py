import select

from Message import Message
from UartMessage import UartMessage


class ElementUart:
    def __init__(self, uart_message: UartMessage):
        self.uart_message = uart_message
        self.poll = select.poll()
        self.poll.register(self.uart_message.uart(), select.POLLIN)
        self.seq = 0
        self.tmp_cnt = 0

    def set_message(self, message: Message):
        if not message:
            return

        # TODO virtual position & retries
        self.uart_message.send_message(self.seq, message)

        if self.poll.poll(100):
            recv = self.uart_message.recv_ack()

            if recv:
                recv_seq, is_stopped, motor_position = recv
                if recv_seq != self.seq:
                    # TODO
                    print('wrong seq:', recv_seq, self.seq)
                print('is_stopped {} motor_position {}', is_stopped, motor_position)

        self.seq += 1

        self.tmp_cnt = 2038
        return

    def get_motor_position(self) -> [int]:
        # TODO virtual position
        return [0]

    def is_stopped(self) -> bool:
        # TODO virtual position != target position and no delay
        return self.tmp_cnt == 0

    def step(self):
        # TODO reduce delay, update virtual position
        if self.tmp_cnt > 0:
            self.tmp_cnt -= 1
        return
