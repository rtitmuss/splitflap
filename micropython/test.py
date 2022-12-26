from machine import Pin
import math
from module import Module
import random
import time

MAX_RPM = 15 # (max rpm 15)

# 1 / (15 max_rpm / 60 sec * 2048 steps)= ~1953ms
STEP_INTERVAL_US = math.floor((1/(MAX_RPM / 60 * 2048)) * 1000000)

print('step_interval {}'.format(STEP_INTERVAL_US))

SENSOR_GPIO = Pin(0, Pin.IN, Pin.PULL_UP)
MOTOR_GPIO = list(map(lambda x: Pin(x, Pin.OUT, value=0), [2, 3, 4, 5]))


def task():
    module.set_home_pin(SENSOR_GPIO.value())
    
    module.task()
    
    motorPins = module.get_motor_pins()
    #print('pins {0:04b}'.format(motorPins))
    MOTOR_GPIO[0].value(motorPins & (1 << 0))
    MOTOR_GPIO[1].value(motorPins & (1 << 1))
    MOTOR_GPIO[2].value(motorPins & (1 << 2))
    MOTOR_GPIO[3].value(motorPins & (1 << 3))


module = Module()

message = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#") + list(reversed("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "))
message_idx = 0

while not module.is_panic():    
    next_us = time.ticks_us() + STEP_INTERVAL_US

    task()
    
    if module.is_stopped():
        time.sleep(1)

        print('rotate to {}'.format(message[message_idx]))
        module.rotate_to_letter(message[message_idx])
        message_idx = (message_idx + 1) % len(message)
    
    now_us = time.ticks_us()
    if time.ticks_diff(next_us, now_us) > 0:
        time.sleep_us(time.ticks_diff(next_us, now_us))
