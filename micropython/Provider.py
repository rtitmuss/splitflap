from Message import Message
from typing import Union, Tuple

from Display import Display


class Provider:
    def get_word_or_message(self, word: str, rpm: int, display: Display, motor_position: [int]) \
            -> Union[Tuple[str, int], Tuple[Message, int]]:
        pass
