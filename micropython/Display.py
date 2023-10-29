from Message import Message
from StepperMotor import stepper_add_offset, stepper_sub_offset


def reorder(data, default, indices):
    reordered_data = [default] * len(indices)
    for i, index in enumerate(indices):
        if i < len(data):
            reordered_data[index] = data[i]
    return reordered_data


class Display:
    def __init__(self, display_order: str, display_offsets: [int]):
        self.display_offsets = display_offsets
        self.physical_indices = [ord(char) - ord('a') for char in display_order]

        self.virtual_indices = [0] * len(self.physical_indices)
        for i, index in enumerate(self.physical_indices):
            self.virtual_indices[index] = i

    def adjust_word(self, word: str) -> str:
        word_len = len(self.physical_indices)
        return (word + ' ' * (word_len - len(word)))[:word_len]

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
