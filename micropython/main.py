from machine import Pin
import math
from module import Module
import random
import time
from ucollections import namedtuple

MAX_RPM = 15  # (max rpm 15)

# 1 / (15 max_rpm / 60 sec * 2048 steps)= ~1953ms
STEP_INTERVAL_US = math.floor((1 / (MAX_RPM / 60 * 2048)) * 1000000)

print('step_interval {}'.format(STEP_INTERVAL_US))

module_led = Pin(3, Pin.OUT, value=0)

ModulePins = namedtuple("ModulePins", ("state", "sensor_pin", "motor_pin"))


class ModulePins:

    def __init__(self, sensor, motor_a, motor_b, motor_c, motor_d,
                 sensor_active):
        self.state = Module(home_pin_active=sensor_active)
        self.sensor_pin = Pin(sensor, Pin.IN, Pin.PULL_UP)
        self.motor_pin = list(
            map(lambda x: Pin(x, Pin.OUT, value=0),
                [motor_a, motor_b, motor_c, motor_d]))


def task():
    for module in module_list:
        module.state.set_home_pin(module.sensor_pin.value())
        module.state.task()

    for module in module_list:
        motor_state = module.state.get_motor_pins()
        #print('pins {0:04b}'.format(motorPins))
        module.motor_pin[0].value(motor_state & (1 << 0))
        module.motor_pin[1].value(motor_state & (1 << 1))
        module.motor_pin[2].value(motor_state & (1 << 2))
        module.motor_pin[3].value(motor_state & (1 << 3))


def is_any_panic():
    #    return any(map(lambda x: x.state.is_panic(), module_list))
    # TODO all panic during bring up
    return all(map(lambda x: x.state.is_panic(), module_list))


def is_all_stopped():
    return all(map(lambda x: x.state.is_stopped(), module_list))


def rotate_to(string):
    for module, char in zip(module_list, string):
        module.state.rotate_to_letter(char)


module_list = [
    ModulePins(2, 28, 27, 26, 22, 1),
    #    ModulePins(14, 18, 19, 20, 21, 0),
    ModulePins(1, 9, 8, 7, 6, 0),
    #    ModulePins(15, 10, 11, 12, 13, 1)
]

num_modules = len(module_list)

test_chars = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#") + list(
    reversed("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "))

test_words = [
    "in", "of", "to", "is", "it", "on", "no", "us", "at", "un", "go", "an",
    "my", "up", "me", "as", "he", "we", "so", "be", "by", "or", "do", "if ",
    "hi", "bi", "ex", "ok", "18", "21", "99"
]

#message = list(map(lambda s: s * num_modules, test_chars))
message = test_words
message_idx = 0

while not is_any_panic():
    next_us = time.ticks_us() + STEP_INTERVAL_US

    task()

    module_led.value(not is_all_stopped())

    if is_all_stopped():
        time.sleep(1)

        print('rotate to {}'.format(message[message_idx]))
        rotate_to(message[message_idx])
        message_idx = (message_idx + 1) % len(message)

    now_us = time.ticks_us()
    if time.ticks_diff(next_us, now_us) > 0:
        time.sleep_us(time.ticks_diff(next_us, now_us))
