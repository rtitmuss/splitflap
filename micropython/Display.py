from Message import Message
from StepperMotor import stepper_sub, stepper_add


def reorder(data, default, indices):
    reordered_data = [default] * len(indices)
    for i, index in enumerate(indices):
        if i < len(data):
            reordered_data[index] = data[i]
    return reordered_data


class Display:
    def __init__(self, display_order: str, display_offsets: [int]):
        self.display_offsets = display_offsets
        self.physical_indices = list(map(lambda x: ord(x) - ord('a'), display_order))

    def virtual_to_physical(self, message: Message) -> Message:
        rpm = message.get_rpm()
        element_delay = message.get_element_delay()
        element_position = message.get_element_position()

        display_offsets = self.display_offsets
        offset_position = [stepper_add(element_position[i], display_offsets[i]) for i in range(len(element_position))]

        physical_delay = reorder(element_delay, 0, self.physical_indices)
        physical_position = reorder(offset_position, 0, self.physical_indices)

        return Message(rpm, physical_delay, physical_position)

    def physical_to_virtual(self, motor_position: [int]) -> [int]:
        offset_position = reorder(motor_position, 0, self.physical_indices)

        display_offsets = self.display_offsets
        virtual_position = [stepper_sub(offset_position[i], display_offsets[i]) for i in range(len(offset_position))]

        return virtual_position
