import time

from Message import Message
from Source import Source

_WORDS = list([
        "abcdefghijkl", "Hello  World", "AAAAAAAAAAAA", "BBBBBBBBBBBB", "ZZZZZZZZZZZZ", "YYYYYYYYYYYY",
        "Spirit", "Purple",
        "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
        "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital",
        "Orbit", "Pepper", "874512", "365498", "720156", "935827", "$$$$$$",
        "$#$#$#", "&&&&&&"
    ])


class SourceWords(Source):
    def __init__(self):
        self.i = 0

    def load_message(self, is_stopped: bool, motor_position: [int]) -> Union[Message, None]:
        if not is_stopped:
            return

        time.sleep(0.5)

        word = _WORDS[self.i % len(_WORDS)]
        self.i += 1

        return Message.word_starting_in_sync(15, word)
