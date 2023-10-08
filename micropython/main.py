import gc
import math
import time

from array import array

import micropython
from machine import Pin, Timer, UART
from micropython import const

from ElementGpio import ElementGpio
from Message import Message
from InvertedNeoPixel import InvertedNeoPixel
from Panel import Panel
from UartProtocol import UartProtocol
from typing import Union

# primary or downstream panel
is_picow: bool = True
try:
    import network
except ImportError:
    is_picow = False

# leds
rp2040_led = Pin("LED", Pin.OUT)
timer = Timer(period=2000, mode=Timer.PERIODIC, callback=lambda t: rp2040_led.toggle())

panel_led = Pin(3, Pin.OUT, value=0)
neopixel = InvertedNeoPixel(Pin(0), 2)

# uart
UART_BAUD_RATE = const(19200)
UART_CHAR_TIMEOUT_MS = const(10)
UART_FRAME_TIMEOUT_MS = const(200)

uart_upstream = UartProtocol(
    UART(0,
         baudrate=UART_BAUD_RATE,
         tx=Pin(16, Pin.IN, Pin.PULL_UP),
         rx=Pin(17, Pin.OUT, Pin.PULL_UP),
         timeout=UART_CHAR_TIMEOUT_MS))

uart_downstream = UartProtocol(
    UART(1,
         baudrate=UART_BAUD_RATE,
         tx=Pin(4, Pin.IN, Pin.PULL_UP),
         rx=Pin(5, Pin.OUT, Pin.PULL_UP),
         timeout=UART_CHAR_TIMEOUT_MS))

# panel and element
panel = Panel([
    ElementGpio(2, 28, 27, 26, 22),
    ElementGpio(14, 18, 19, 20, 21),
    ElementGpio(1, 9, 8, 7, 6),
    ElementGpio(15, 10, 11, 12, 13)
])

# todo move this ...

test_i = 0
test_words = list([
        "abcdefghijkl", "Hello  World", "Spirit", "Purple",
        "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
        "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital",
        "Orbit", "Pepper", "874512", "365498", "720156", "935827", "$$$$$$",
        "$#$#$#", "&&&&&&"
    ])

# return frame from queue or UART depending if this is a primary or secondary module
def load_message(is_stopped: bool, status: str) -> Union[Message, None]:
    if not is_stopped:
        return

    time.sleep(2)

    global test_i
    word = test_words[test_i % len(test_words)]
    test_i += 1

    return Message.word_starting_in_sync(15, word)


@micropython.native
def main_loop():
    # loop metrics
    loop_buffer_size = 1000
    loop_buffer = array('i', [0] * loop_buffer_size)
    loop_buffer_index = 0

    interval_us = 0

    gc.collect()

    while True:
        t0_us = time.ticks_us()

        is_stopped = panel.is_stopped()
        panel_led.value(not is_stopped)

        message = load_message(is_stopped, panel.get_motor_position())
        if message:
            panel.set_message(message)

            # loop metrics
            loop_average_time = sum(loop_buffer) / loop_buffer_size
            loop_variance = sum((x - loop_average_time) ** 2 for x in loop_buffer) / (loop_buffer_size - 1)
            loop_std_deviation = math.sqrt(loop_variance)
            print("loop: {:.2f}us +/-{:.2f}; interval {}us".format(loop_average_time, loop_std_deviation, interval_us))

            gc.collect()
            print('mem_free:', gc.mem_free())

        interval_us = panel.step()

        t1_us = time.ticks_us()
        elapsed_us = time.ticks_diff(t1_us, t0_us)
        delay_us = interval_us - elapsed_us

        if delay_us > 0:
            time.sleep_us(delay_us)

        loop_buffer[loop_buffer_index] = elapsed_us
        loop_buffer_index = (loop_buffer_index + 1) % loop_buffer_size


main_loop()
