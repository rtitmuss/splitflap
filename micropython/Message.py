import random
from math import ceil

from StepperMotor import STEPS_PER_REVOLUTION, stepper_add

LETTERS = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#'
_STEPS_PER_LETTER = STEPS_PER_REVOLUTION / len(LETTERS)


def _fisher_yates_shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def _letter_position(letter):
    index = LETTERS.find(letter.upper())
    if index == -1:
        raise ValueError('invalid letter')

    return ceil((index + 0.5) * _STEPS_PER_LETTER)


class Message:
    def __init__(self, rpm: int, element_delay: [int], element_position: [int]):
        self.rpm = rpm
        self.element_delay = element_delay
        self.element_position = element_position

    def __eq__(self, other):
        return self.rpm == other.rpm \
            and self.element_delay == other.element_delay \
            and self.element_position == other.element_position

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            return Message(self.rpm, self.element_delay[start:stop:step], self.element_position[start:stop:step])
        else:
            return Message(self.rpm, [self.element_delay[key]], [self.element_position[key]])

    def __len__(self):
        return len(self.element_position)

    def get_rpm(self) -> int:
        return self.rpm

    def get_element_delay(self) -> [int]:
        return self.element_delay

    def get_element_position(self) -> [int]:
        return self.element_position

    @classmethod
    def word_start_in_sync(cls, rpm: int, word: str):
        element_position = list(map(_letter_position, word))
        return Message(rpm, [0] * len(element_position), element_position)

    @classmethod
    def word_start_sweep(cls, rpm: int, word: str, sweep_offset: int):
        element_position = list(map(_letter_position, word))
        elements_delay = [int(i * _STEPS_PER_LETTER * sweep_offset) for i in range(len(element_position))]
        return Message(rpm, elements_delay, element_position)

    @classmethod
    def word_random(cls, rpm: int, word: str, sweep_offset: int):
        element_position = list(map(_letter_position, word))
        random_delay = _fisher_yates_shuffle(list(range(len(element_position))))
        elements_delay = [int(i * _STEPS_PER_LETTER * sweep_offset) for i in random_delay]
        return Message(rpm, elements_delay, element_position)

    @classmethod
    def word_end_in_sync(cls, rpm: int, word: str, motor_position: [int]):
        element_position = list(map(_letter_position, word))
        len_element_position = len(element_position)

        padded_motor_position = motor_position + [0] * (len_element_position - len(motor_position))

        element_steps = \
            [stepper_add(element_position[i], -padded_motor_position[i]) for i in range(len_element_position)]

        max_steps = max(element_steps)
        elements_delay = [max_steps - step for step in element_steps]

        return Message(rpm, elements_delay, element_position)
