import time
from typing import Union

from Message import Message
from Source import Source

from Config import display_order, display_offsets

_WORDS = list([
        "abcdefghijkl", "Hello  World", "AAAAAAAAAAAA", "BBBBBBBBBBBB", "ZZZZZZZZZZZZ", "YYYYYYYYYYYY",
        "Spirit", "Purple",
        "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
        "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital",
        "Orbit", "Pepper", "874512", "365498", "720156", "935827", "$$$$$$",
        "$#$#$#", "&&&&&&"
    ])


def reorder(data, default, indices):
    reordered_data = [default] * len(indices)
    for i, index in enumerate(indices):
        if i < len(data):
            reordered_data[index] = data[i]
    return reordered_data


display_indices = list(map(lambda x: ord(x) - ord('a'), display_order))
display_offsets = reorder(display_offsets, 0, display_indices)


class SourceWords(Source):
    def __init__(self):
        self.i = 0

    def load_message(self, is_stopped: bool, motor_position: [int]) -> Union[Message, None]:
        if not is_stopped:
            return

        time.sleep(0.5)

        word = _WORDS[self.i % len(_WORDS)]
        self.i += 1

        print('word:', word)
        print('motor_position:', motor_position)

        reordered_word = reorder(word, ' ', display_indices)

        return Message.word_starting_in_sync(15, reordered_word)
