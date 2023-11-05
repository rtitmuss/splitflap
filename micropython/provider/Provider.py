from typing import Union, Tuple, Dict

from Display import Display
from Message import Message, LETTERS


class Provider:
    def get_message(self, display_word: str, display_data: Dict[str, str], display: Display, motor_position: [int])\
            -> Tuple[Message, Union[int, None]]:
        rpm = int(display_data.get('rpm', 15))
        order = display_data.get('order', None)

        word, interval_ms = self.get_word(display_word, display)
        display_word = display.adjust_word(word)
        print('word: \'{}\' rpm: {}'.format(display_word, rpm))

        if order == "random":
            message = Message.word_random(rpm, display_word, 2)
        elif order == "sweep":
            message = Message.word_sweep(rpm, display_word, 2)
        elif order == "diagonal_sweep":
            message = Message.word_diagonal_sweep(rpm, display_word, 2)
        elif order == "end_in_sync":
            message = Message.word_end_in_sync(rpm, display_word, motor_position)
        else:
            message = Message.word_start_in_sync(rpm, display_word)

        return message, interval_ms

    def get_word(self, word: str, display: Display) -> Tuple[str, Union[int, None]]:
        # filter characters using LETTERS
        clean_word = ''.join(char for char in word if char in LETTERS)
        interval_ms = None
        return clean_word, interval_ms
