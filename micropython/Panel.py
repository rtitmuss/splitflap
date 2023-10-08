import math

from array import array
from micropython import const

from reduce import reduce
from typing import Union
from Element import Element
from Message import Message


class Panel:
    MAX_28BYJ_48_RPM: int = const(15)

    def __init__(self, element_list: [Element]):
        self.step_interval_us = None
        self.element_list = element_list
        self.set_rpm(Panel.MAX_28BYJ_48_RPM)
        return

    def set_message(self, message: Message):
        self.set_rpm(message.rpm)
        for index, element in enumerate(self.element_list):
            element.set_message(message[index:])

    def set_rpm(self, rpm):
        # 1 / (15 max_rpm / 60 sec * 2038 steps)= ~1953ms
        self.step_interval_us = math.floor(
            (1 / (min(Panel.MAX_28BYJ_48_RPM, rpm) / 60 * 2038)) * 1000000)

    def get_motor_position(self) -> [int]:
        return reduce(lambda x, y: x + y, map(lambda element: element.get_motor_position(), self.element_list))
        # return [item for element in self.element_list for item in element.get_motor_position()]

    def is_stopped(self) -> bool:
        return all(map(lambda element: element.is_stopped(), self.element_list))
        # is_stopped = True
        # for element in self.element_list:
        #     is_stopped = is_stopped and element.is_stopped()
        # return is_stopped

    def step(self) -> Union[int, None]:
        for element in self.element_list:
            element.step()

        return self.step_interval_us
