import math
import time


class Cluster:

    MAX_RPM = 15  # (max rpm 15)

    # 1 / (15 max_rpm / 60 sec * 2048 steps)= ~1953ms
    STEP_INTERVAL_US = math.floor((1 / (MAX_RPM / 60 * 2048)) * 1000000)

    print('step_interval {}'.format(STEP_INTERVAL_US))

    def __init__(self, module_led, modules_gpio_list):
        self.module_led = module_led
        self.module_list = modules_gpio_list

    def __task(self, max_steps):
        for module in self.module_list:
            if max_steps <= module.steps_to_rotate():
                module.task()

        for module in self.module_list:
            module.step()

    def is_any_panic(self):
        return any(map(lambda x: x.is_panic(), self.module_list))

    def is_all_stopped(self):
        return all(map(lambda x: x.is_stopped(), self.module_list))

    def steps_to_rotate(self):
        return max(map(lambda x: x.steps_to_rotate(), self.module_list))

    def set_letters(self, string):
        for module, letter in zip(self.module_list, string):
            module.rotate_to_letter(letter)

    def rotate_until_stopped(self, max_steps):
        self.module_led.value(True)

        while True:
            next_us = time.ticks_us() + Cluster.STEP_INTERVAL_US

            self.__task(max_steps)
            max_steps -= 1

            if self.is_all_stopped() or self.is_any_panic():
                break

            now_us = time.ticks_us()
            if time.ticks_diff(next_us, now_us) > 0:
                time.sleep_us(time.ticks_diff(next_us, now_us))

        self.module_led.value(False)
