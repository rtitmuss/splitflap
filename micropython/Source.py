from Message import Message
from typing import Union


class Source:
    def load_message(self, is_stopped: bool, motor_position: [int]) -> Union[Message, None]:
        return None
