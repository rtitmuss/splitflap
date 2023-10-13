from math import ceil

LETTERS = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#'

STEPS_PER_REVOLUTION = 2038  # 28BYJ-48
STEPS_PER_LETTER = STEPS_PER_REVOLUTION / len(LETTERS)


def _letter_position(letter):
    index = LETTERS.find(letter.upper())
    if index == -1:
        raise ValueError('invalid letter')

    return ceil((index + 0.5) * STEPS_PER_LETTER)


class Message:
    def __init__(self, rpm: int, element_delay: [int], element_position: [int]):
        self.rpm = rpm
        self.element_delay = element_delay
        self.element_position = element_position

    def __eq__(self, other):
        return self.rpm == other.rpm \
            and self.element_delay == other.element_delay \
            and self.element_position == other.element_position

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            return Message(self.rpm, self.element_delay[start:stop:step], self.element_position[start:stop:step])
        else:
            return Message(self.rpm, [self.element_delay[key]], [self.element_position[key]])

    def __len__(self):
        return len(self.element_position)

    def get_rpm(self) -> int:
        return self.rpm

    def get_element_delay(self) -> [int]:
        return self.element_delay

    def get_element_position(self) -> [int]:
        return self.element_position

    @classmethod
    def word_starting_in_sync(cls, rpm: int, word: str):
        element_position = list(map(_letter_position, word))
        return Message(rpm, [0] * len(element_position), element_position)
