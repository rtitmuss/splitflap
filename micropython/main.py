import gc
import math
import time

from array import array
from random import randint

import machine
import micropython
from machine import Pin, Timer, UART
from micropython import const

from Display import Display
from ElementGpio import ElementGpio
from ElementUart import ElementUart
from InvertedNeoPixel import InvertedNeoPixel
from Panel import Panel
from Source import Source
from SourceHttpd import SourceHttpd
from SourceUart import SourceUart
from SourceWords import SourceWords
from UartFrame import UartFrame
from UartMessage import UartMessage
from Wifi import wifi_connect

import Config

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

uart_upstream = UartMessage(
    UartFrame(
        UART(0,
             baudrate=UART_BAUD_RATE,
             tx=Pin(16, Pin.IN, Pin.PULL_UP),
             rx=Pin(17, Pin.OUT, Pin.PULL_UP),
             timeout=UART_CHAR_TIMEOUT_MS)))

uart_downstream = UartMessage(
    UartFrame(
        UART(1,
             baudrate=UART_BAUD_RATE,
             tx=Pin(4, Pin.IN, Pin.PULL_UP),
             rx=Pin(5, Pin.OUT, Pin.PULL_UP),
             timeout=UART_CHAR_TIMEOUT_MS)))

# panel and element
panel = Panel([
    ElementGpio(2, 28, 27, 26, 22),
    ElementGpio(14, 18, 19, 20, 21),
    ElementGpio(1, 9, 8, 7, 6),
    ElementGpio(15, 10, 11, 12, 13),
    ElementUart(uart_downstream)
])


def downstream_machine_reset():
    seq = uart_downstream.next_seq()
    uart_downstream.send_machine_reset(seq)
    # TODO wait for ack


@micropython.native
def main_loop(source: Source):
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

        message = source.load_message(is_stopped, panel.get_motor_position())
        if message:
            if message == UartMessage.MACHINE_RESET_MESSAGE:
                downstream_machine_reset()
                print("machine reset")
                time.sleep_ms(500)
                machine.reset()

            panel.set_message(message)

            # loop metrics
            loop_average_time = sum(loop_buffer) / loop_buffer_size
            loop_variance = sum((x - loop_average_time) ** 2 for x in loop_buffer) / (loop_buffer_size - 1)
            loop_std_deviation = math.sqrt(loop_variance)
            print("loop: {:.2f}us +/-{:.2f}; interval {}us".format(loop_average_time, loop_std_deviation, interval_us))

            neopixel.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
            neopixel.write()

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


if is_picow:
    wifi_connect()
    downstream_machine_reset()
    time.sleep_ms(1000)

    display = Display(Config.display_order, Config.display_offsets)
    # board_source = SourceWords(Config.test_words, Display(Config.display_order, Config.display_offsets))
    board_source = SourceHttpd(display, Config.providers, 80)
else:
    board_source = SourceUart(uart_upstream)

main_loop(board_source)
