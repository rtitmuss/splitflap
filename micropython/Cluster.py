import math
import time


class Cluster:

    MAX_RPM = 15  # (max rpm 15)

    def __init__(self, module_led, modules_gpio_list):
        self.module_led = module_led
        self.module_list = modules_gpio_list
        self.set_rpm(Cluster.MAX_RPM)

    def __task(self, max_steps):
        for module in self.module_list:
            if max_steps <= module.steps_to_rotate():
                module.task()

        for module in self.module_list:
            module.step()

    def num_modules(self):
        return len(self.module_list)

    def is_all_stopped(self):
        return all(map(lambda x: x.is_stopped(), self.module_list))

    def get_max_steps(self):
        return max(map(lambda x: x.steps_to_rotate(), self.module_list))

    def get_status(self):
        return ''.join(map(lambda x: x.get_status(), self.module_list))

    def set_rpm(self, rpm):
        # 1 / (15 max_rpm / 60 sec * 2048 steps)= ~1953ms
        self.step_interval_us = math.floor(
            (1 / (min(Cluster.MAX_RPM, rpm) / 60 * 2048)) * 1000000)

    def set_letters(self, string):
        for module, letter in zip(self.module_list, string):
            module.rotate_to_letter(letter)

    def rotate_until_stopped(self, max_steps):
        self.module_led.value(True)

        while True:
            next_us = time.ticks_us() + self.step_interval_us

            self.__task(max_steps)
            max_steps -= 1

            if max_steps <= 0 and self.is_all_stopped():
                break

            now_us = time.ticks_us()
            if time.ticks_diff(next_us, now_us) > 0:
                time.sleep_us(time.ticks_diff(next_us, now_us))

        self.module_led.value(False)
