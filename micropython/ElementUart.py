import select

from micropython import const

from StepperMotor import STEPS_PER_REVOLUTION, stepper_sub
from typing import Callable

from Message import Message
from UartMessage import UartMessage


# poll factory to allow for unit testing
def _poll_factory(uart_message: UartMessage):
    poll = select.poll()
    poll.register(uart_message.uart(), select.POLLIN)

    def poll_func(timeout_ms: int) -> bool:
        return poll.poll(timeout_ms)

    return poll_func


def _calculate_steps(motor_position: [int], element_delay: [int], element_position: [int], element_rotation: [int]) \
        -> int:
    return max(
        stepper_sub(element_position[i], motor_position[i])
        + element_rotation[i] * STEPS_PER_REVOLUTION
        + element_delay[i]
        for i in range(len(motor_position))
    )


class ElementUart:
    def __init__(self, uart_message: UartMessage, poll_factory: Callable = _poll_factory):
        self.poll = poll_factory(uart_message)
        self.uart_message = uart_message
        self.seq = 0

        self.element_delay = []
        self.element_position = []
        self.element_rotation = []
        self.motor_position = []
        self.count = 0

    def __str__(self):
        def _element_str_(i: int):
            state = ['motor={}'.format(self.motor_position[i])]
            if self.element_delay[i] > 0:
                state.append('delay={}'.format(self.element_delay[i]))
            if self.element_rotation[i] > 0:
                state.append('rotation={}'.format(self.element_rotation[i]))
            if self.element_position[i] != self.motor_position[i]:
                state.append('position={}'.format(self.element_position[i]))
            return ' '.join(state)

        return 'ElementUart: count={}\n{}'.format(
            self.count,
            '\n'.join('  {}'.format(_element_str_(i)) for i in range(len(self.motor_position)))
        )

    def set_message(self, message: Message):
        if not message:
            return

        self.element_delay = message.get_element_delay()
        element_position = message.get_element_position()
        self.element_position = [pos % STEPS_PER_REVOLUTION for pos in element_position]
        self.element_rotation = [pos // STEPS_PER_REVOLUTION for pos in element_position]

        send_seq = self.seq
        self.seq += 1

        self.uart_message.send_message(send_seq, message)

        while self.poll(100):
            recv = self.uart_message.recv_ack()
            if not recv:
                self.motor_position = []
                self.count = 0
                return

            recv_seq, is_stopped, motor_position = recv
            if recv_seq != send_seq:
                print('wrong seq:', recv_seq, send_seq)
                continue

            self.motor_position = motor_position
            if not is_stopped or any(pos < 0 for pos in motor_position):
                # Fall back to a full rotation if exact motor position is not known
                self.count = STEPS_PER_REVOLUTION
            else:
                self.count = _calculate_steps(motor_position, self.element_delay, self.element_position,
                                              self.element_rotation)
            break

    def get_motor_position(self) -> [int]:
        return self.motor_position

    def is_stopped(self) -> bool:
        return self.count == 0

    def step(self):
        if self.count > 0:
            self.count -= 1

        element_delay = self.element_delay
        element_position = self.element_position
        element_rotation = self.element_rotation
        motor_position = self.motor_position

        for i in range(len(self.motor_position)):
            if element_delay[i] > 0:
                element_delay[i] -= 1
            else:
                if motor_position[i] != element_position[i] or element_rotation[i] > 0:
                    motor_position[i] += 1
                    motor_position[i] = motor_position[i] % STEPS_PER_REVOLUTION
                    if motor_position[i] == element_position[i] and element_rotation[i] > 0:
                        element_rotation[i] -= 1


# ignore micropython.native with unit tests on laptop
try:
    from micropython import native
    ElementUart.get_motor_position = native(ElementUart.get_motor_position)
    ElementUart.is_stopped = native(ElementUart.is_stopped)
    ElementUart.step = native(ElementUart.step)
except ImportError:
    pass
