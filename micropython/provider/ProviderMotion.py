import random
from typing import Union, Tuple

import StepperMotor
from Message import Message
from primary.Display import Display
from provider.Provider import Provider


class ProviderMotion(Provider):

    def get_message(self, word: str, display_data: Dict[str, str], display: Display, motor_position: [int]) \
            -> Tuple[Message, Union[int, None]]:
        rpm = int(display_data.get('rpm', 10))
        display_len = display.display_length()

        random_element = random.randint(0, display_len - 1)
        motor_position[random_element] = StepperMotor.stepper_add(
            motor_position[random_element],
            random.randint(int(StepperMotor.STEPS_PER_REVOLUTION / 4), int(StepperMotor.STEPS_PER_REVOLUTION / 2))
        )

        return Message(rpm, [0] * display_len, motor_position), 1
