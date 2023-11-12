from typing import List

from Message import Message
from StepperMotor import stepper_add_offset, stepper_sub_offset


def reorder(data, default, indices):
    reordered_data = [default] * len(indices)
    for i, index in enumerate(indices):
        if i < len(data):
            reordered_data[index] = data[i]
    return reordered_data


def ljust(s: str, length: int) -> str:
    return s + ' ' * (length - len(s))


def split_string_by_length(input_string: str, cols: int) -> List[str]:
    words = input_string.split()
    result = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= cols:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                result.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

        while current_length > cols:
            line = ' '.join(current_line)
            result.append(line[:cols])
            current_line = [line[cols:]]
            current_length = len(current_line[0])

    if current_line:
        result.append(' '.join(current_line))

    return result


def combine_lines_for_display(lines: List[str], rows: int, cols: int) -> List[str]:
    result = []

    for i in range(0, len(lines) - rows + 1, rows):
        pair = [ljust(line, cols) for line in lines[i:i + rows]]
        result.append(''.join(pair))

    remaining_lines = len(lines) % rows
    if remaining_lines > 0:
        pair = [ljust(line, cols) for line in lines[-remaining_lines:]]
        result.append(''.join(pair))

    return result


class Display:
    def __init__(self, display_order: [str], display_offsets: [int]):
        self.rows = len(display_order)
        self.cols = len(display_order[0])
        self.display_offsets = display_offsets
        self.physical_indices = [ord(char) - ord('a') for char in ''.join(display_order)]

        self.virtual_indices = [0] * len(self.physical_indices)
        for i, index in enumerate(self.physical_indices):
            self.virtual_indices[index] = i

    def display_length(self) -> int:
        return len(self.physical_indices)

    def adjust_word(self, input_str: str) -> str:
        word_len = len(self.physical_indices)
        return ljust(input_str, word_len)[:word_len]

    def format_string_left_justified(self, input_str: str) -> List[str]:
        return combine_lines_for_display(split_string_by_length(input_str, self.cols), self.rows, self.cols)

    def virtual_to_physical(self, message: Message) -> Message:
        rpm = message.get_rpm()
        element_delay = message.get_element_delay()
        element_position = message.get_element_position()

        display_offsets = self.display_offsets
        offset_position = [stepper_add_offset(element_position[i], display_offsets[i]) for i in range(len(element_position))]

        physical_delay = reorder(element_delay, 0, self.physical_indices)
        physical_position = reorder(offset_position, 0, self.physical_indices)

        return Message(rpm, physical_delay, physical_position)

    def physical_to_virtual(self, motor_position: [int]) -> [int]:
        offset_position = reorder(motor_position, 0, self.virtual_indices)

        display_offsets = self.display_offsets
        virtual_position = [stepper_sub_offset(offset_position[i], display_offsets[i]) for i in range(len(offset_position))]

        return virtual_position
