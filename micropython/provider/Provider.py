from typing import Union, Tuple, Dict

from Message import Message, LETTERS
from primary.Display import Display


class Provider:
    def get_message(self, args: Dict[str, str], display: Display, motor_position: [int])\
            -> Tuple[Message, Union[int, None]]:
        rpm = int(args.get('rpm', 15))
        order = args.get('order', None)

        word, interval_ms = self.get_word(args, display)
        # filter characters using LETTERS
        clean_word = ''.join(char for char in word.upper() if char in LETTERS)
        display_word = display.adjust_word(clean_word)
        self.last_word = display_word
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

    def get_word(self, args: Dict[str, str], display: Display) -> Tuple[str, Union[int, None]]:
        return args.get('text', ''), None
