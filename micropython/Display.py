import math
import time


class Display:

    MAX_RPM = 15  # (max rpm 15)

    BEGIN_IN_SYNC = 0
    END_IN_SYNC = 1
    ROTATE_ALWAYS_END_IN_SYNC = 2

    def __init__(self, display_led, letters_list):
        self.display_led = display_led
        self.letter_list = letters_list
        self.set_rpm(Display.MAX_RPM)

    def __task(self, max_steps):
        for letter in self.letter_list:
            if self.mode == Display.BEGIN_IN_SYNC or max_steps <= letter.steps_to_rotate(
            ):
                letter.task()

        for letter in self.letter_list:
            letter.step()

    def num_letters(self):
        return len(self.letter_list)

    def is_all_stopped(self):
        return all(map(lambda x: x.is_stopped(), self.letter_list))

    def get_max_steps(self):
        return max(map(lambda x: x.steps_to_rotate(), self.letter_list))

    def get_status(self):
        return ''.join(map(lambda x: x.get_status(), self.letter_list))

    def set_rpm(self, rpm):
        # 1 / (15 max_rpm / 60 sec * 2048 steps)= ~1953ms
        self.step_interval_us = math.floor(
            (1 / (min(Display.MAX_RPM, rpm) / 60 * 2048)) * 1000000)

    def set_offsets(self, offsets):
        for letter, offset in zip(self.letter_list, offsets):
            letter.set_offset(offset)

    def set_letters(self, string, mode=BEGIN_IN_SYNC):
        self.mode = mode
        for letter, char in zip(self.letter_list, string):
            letter.set_letter(
                char,
                rotate_always=(mode == Display.ROTATE_ALWAYS_END_IN_SYNC))

    def rotate_until_stopped(self, max_steps):
        self.display_led.value(True)

        while True:
            next_us = time.ticks_us() + self.step_interval_us

            self.__task(max_steps)
            max_steps -= 1

            if max_steps <= 0 and self.is_all_stopped():
                break

            now_us = time.ticks_us()
            if time.ticks_diff(next_us, now_us) > 0:
                time.sleep_us(time.ticks_diff(next_us, now_us))

        self.display_led.value(False)
