import random
import time

from Display import Display
from typing import Union

from Message import Message
from Source import Source

_WORDS = list([
        "abcdefghijkl", "defghijklmno", "abcdefghijkl",
        "Hello  World", "AAAAAAAAAAAA", "BBBBBBBBBBBB", "ZZZZZZZZZZZZ", "YYYYYYYYYYYY",
        "Spirit", "Purple",
        "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
        "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital",
        "Orbit", "Pepper", "874512", "365498", "720156", "935827", "$$$$$$$$$$$$",
        "$#$#$##$#$#$", "&&&&&&&&&&&&"
    ])


class SourceWords(Source):
    def __init__(self, display: Display):
        self.display = display
        self.i = 0
        self.last_i = None

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        if not is_stopped:
            return

        time.sleep(2)

        motor_position = self.display.physical_to_virtual(physical_motor_position)

        while True:
            rand_i = random.randint(0, len(_WORDS) - 1)
            if rand_i != self.last_i:
                break
        self.last_i = rand_i
        src_word = _WORDS[rand_i]

        # src_word = _WORDS[self.i % len(_WORDS)]
        self.i += 1

        # clock
        # (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()
        # src_word = "{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(hour, minute, second, mday, month, year % 100)

        word = self.display.adjust_word(src_word)

        print('word:', word)
        print('motor_position:', motor_position)

        c = self.i % 4
        if c == 0:
            message = Message.word_start_in_sync(15, word)
        elif c == 1:
            message = Message.word_end_in_sync(15, word, motor_position)
        elif c == 2:
            message = Message.word_start_sweep(15, word, 2)
        else:
            message = Message.word_random(15, word, 2)

        return self.display.virtual_to_physical(message)
