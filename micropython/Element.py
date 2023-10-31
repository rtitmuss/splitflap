from array import array

import micropython
from micropython import const

from StepperMotor import STEPS_PER_REVOLUTION
from typing import Union
from Message import Message

_MAX_HOME_STEPS = int(STEPS_PER_REVOLUTION * 0.2)
_MAX_NON_HOME_STEPS = int(STEPS_PER_REVOLUTION * 1.2)

_MOT_PHASE_A = const(0b00001000)
_MOT_PHASE_B = const(0b00000100)
_MOT_PHASE_C = const(0b00000010)
_MOT_PHASE_D = const(0b00000001)

_STEP_PATTERN = array('i', [
    _MOT_PHASE_A | _MOT_PHASE_B, _MOT_PHASE_B | _MOT_PHASE_C,
    _MOT_PHASE_C | _MOT_PHASE_D, _MOT_PHASE_D | _MOT_PHASE_A
])

_STEP_PATTERN_LENGTH = len(_STEP_PATTERN)


class Element:
    def __init__(self):
        # True if error is detected
        self.panic: Union[str, None] = None

        # stepper motor pins
        self.motor_pins: int = 0

        # home pin (hall effect sensor)
        self.home_pin: Union[int, None] = None

        # stall detection if count home steps exceeds MAX_HOME_STEPS
        self.count_home_steps: int = 0
        self.count_non_home_steps: int = 0

        # motor and target letter positions
        self.motor_position: int = -STEPS_PER_REVOLUTION
        self.element_position: int = -STEPS_PER_REVOLUTION
        self.element_rotation: int = 0
        self.element_delay: int = 0

    def set_home_pin(self, home_pin):
        self.home_pin = home_pin

    def get_motor_pins(self):
        return self.motor_pins

    def _panic(self, error):
        self.motor_pins = 0
        self.panic = error
        print('panic: {}'.format(error))

    def set_message(self, message: Message):
        if not message:
            return

        self.element_delay = message.get_element_delay()[0]

        element_position = message.get_element_position()[0]
        self.element_position = element_position % STEPS_PER_REVOLUTION
        self.element_rotation = element_position // STEPS_PER_REVOLUTION

    def get_motor_position(self) -> [int]:
        return [self.motor_position if self.panic is None else -1]

    def is_stopped(self) -> bool:
        return self.panic or (self.element_delay == 0
                and self.motor_position == self.element_position)

    def step(self):
        if self.home_pin is None:
            raise ValueError('home_pin not set')

        if self.element_delay > 0:
            self.element_delay -= 1
            return

        if self.motor_pins:
            if self.home_pin:
                self.count_home_steps += 1
                if self.count_home_steps > _MAX_HOME_STEPS:
                    self._panic('dwell home')
            elif self.count_home_steps > 0:
                # falling edge, found home position
                self.count_home_steps = 0
                self.count_non_home_steps = 0
                self.motor_position = 0
            else:
                self.count_non_home_steps += 1
                if self.count_non_home_steps > _MAX_NON_HOME_STEPS:
                    self._panic('missed home')

        if self.panic:
            return

        if self.motor_position != self.element_position or self.element_rotation > 0:
            self.motor_pins = _STEP_PATTERN[self.motor_position % _STEP_PATTERN_LENGTH]
            self.motor_position += 1
            if self.motor_position == self.element_position:
                self.element_rotation -= 1
        else:
            self.motor_pins = 0

        self.home_pin = None


# ignore micropython.native with unit tests on laptop
try:
    from micropython import native
    Element.get_motor_position = native(Element.get_motor_position)
    Element.is_stopped = native(Element.is_stopped)
    Element.step = native(Element.step)
except ImportError:
    pass
