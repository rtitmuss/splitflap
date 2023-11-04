import random

import StepperMotor
from Display import Display
from Message import Message
from Provider import Provider
from typing import Union, Tuple


class ProviderMotion(Provider):
    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
                -> Union[Tuple[str, int], Tuple[Message, int]]:
        display_len = display.display_length()

        random_element = random.randint(0, display_len - 1)
        motor_position[random_element] = StepperMotor.stepper_add(
            motor_position[random_element],
            random.randint(int(StepperMotor.STEPS_PER_REVOLUTION / 4), int(StepperMotor.STEPS_PER_REVOLUTION / 2))
        )

        return Message(rpm, [0] * display_len, motor_position), 1
