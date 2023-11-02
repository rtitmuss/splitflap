import random
import time

from micropython import const

from Display import Display
from typing import Union

from Message import Message
from Source import Source

_RPM = const(10)


class SourceWords(Source):
    def __init__(self, words: [str], display: Display):
        self.words = words
        self.display = display
        self.i = 0
        self.last_word = None

    def pick_random_words(self, max_len: int) -> str:
        while True:
            words = []
            words_length = 0

            while words_length <= max_len:  # Add 1 for the space between words
                rand_word = random.choice(self.words)
                rand_word_len = len(rand_word)

                if words_length + rand_word_len <= max_len:
                    words.append(rand_word)
                    words_length += rand_word_len + 1  # Add 1 for the space between words
                else:
                    break

            word = ' '.join(words)
            if word != self.last_word:
                break

        self.last_word = word
        return word

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        if not is_stopped:
            return

        time.sleep(2)

        motor_position = self.display.physical_to_virtual(physical_motor_position)

        # clock
        # (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()
        # src_word = "{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(hour, minute, second, mday, month, year % 100)

        src_word = self.pick_random_words(self.display.display_length())
        word = self.display.adjust_word(src_word)

        print('word: \'{}\''.format(word))
        print('motor_position:', motor_position)

        self.i += 1
        c = self.i % 4
        if c == 0:
            message = Message.word_start_in_sync(_RPM, word)
        elif c == 1:
            message = Message.word_end_in_sync(_RPM, word, motor_position)
        elif c == 2:
            message = Message.word_start_sweep(_RPM, word, 2)
        else:
            message = Message.word_random(_RPM, word, 2)

        return self.display.virtual_to_physical(message)
