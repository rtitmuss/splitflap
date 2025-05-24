import math
import time

from micropython import const

from StepperMotor import STEPS_PER_REVOLUTION
from typing import Union
from Element import Element
from ElementGpio import ElementGpio
from Message import Message


class Panel:
    MAX_28BYJ_48_RPM: int = const(15)

    def __init__(self, element_list: [Element]):
        self.step_interval_us = None
        self.element_list = element_list
        self.set_rpm(Panel.MAX_28BYJ_48_RPM)
        return

    def __str__(self):
        state = '\n'.join(str(element) for element in self.element_list)
        return ('Panel: is_stopped={}\n{}'
                .format(self.is_stopped(), '\n'.join(['  ' + line for line in state.split('\n')])))

    def set_message(self, message: Message):
        self.set_rpm(message.rpm)
        for index, element in enumerate(self.element_list):
            element.set_message(message[index:])

    def set_rpm(self, rpm):
        # 1 / (15 max_rpm / 60 sec * 2038 steps)= ~1953ms
        self.step_interval_us = math.floor(
            (1 / (min(Panel.MAX_28BYJ_48_RPM, rpm) / 60 * STEPS_PER_REVOLUTION)) * 1000000)

    def get_motor_position(self) -> [int]:
        # return reduce(lambda x, y: x + y, map(lambda element: element.get_motor_position(), self.element_list))
        # optimized:
        return [item for element in self.element_list for item in element.get_motor_position()]

    def is_stopped(self) -> bool:
        # return all(map(lambda element: element.is_stopped(), self.element_list))
        # optimized:
        is_stopped = True
        for element in self.element_list:
            is_stopped = is_stopped and element.is_stopped()
        return is_stopped

    def step(self) -> Union[int, None]:
        for element in self.element_list:
            element.step()

        return self.step_interval_us

    def home(self) -> [int]:
        num_elements = sum(isinstance(e, ElementGpio) for e in self.element_list)
        m = Message(15, [0] * num_elements, [STEPS_PER_REVOLUTION + 1] * num_elements)
        self.set_message(m)
        while not self.is_stopped():
            delay_us = self.step()
            time.sleep_us(delay_us)
        return self.get_motor_position()


# ignore micropython.native with unit tests on laptop
try:
    from micropython import native
    Panel.get_motor_position = native(Panel.get_motor_position)
    Panel.is_stopped = native(Panel.is_stopped)
    Panel.step = native(Panel.step)
except ImportError:
    pass
