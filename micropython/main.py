import gc
from machine import Pin, Timer, UART
import random
import select
import sys
from time import localtime, sleep, ticks_diff, ticks_ms

from Display import Display
from InvertedNeoPixel import InvertedNeoPixel
from ModuleGpio import ModuleGpio
from UartProtocol import UartFrame, UartProtocol

# START CONFIGURATION

# module order when displaying alphabet
#display_order = 'abcdefgh'
display_order = 'febahgdc'

# flap offsets in module order
display_offsets = [0] * len(display_order)

# END CONFIGURATION

is_picow = True
try:
    import network
except ImportError:
    is_picow = False

display = Display(Pin(3, Pin.OUT, value=0), [
    ModuleGpio(2, 28, 27, 26, 22),
    ModuleGpio(14, 18, 19, 20, 21),
    ModuleGpio(1, 9, 8, 7, 6),
    ModuleGpio(15, 10, 11, 12, 13)
])

neopixel = InvertedNeoPixel(Pin(0), 2)

UART_BAUDRATE = const(19200)
UART_CHAR_TIMEOUT_MS = const(10)
UART_FRAME_TIMEOUT_MS = const(200)

uart_input = UartProtocol(
    UART(0,
         baudrate=UART_BAUDRATE,
         tx=Pin(16, Pin.IN, Pin.PULL_UP),
         rx=Pin(17, Pin.OUT, Pin.PULL_UP),
         timeout=UART_CHAR_TIMEOUT_MS))
uart_output = UartProtocol(
    UART(1,
         baudrate=UART_BAUDRATE,
         tx=Pin(4, Pin.IN, Pin.PULL_UP),
         rx=Pin(5, Pin.OUT, Pin.PULL_UP),
         timeout=UART_CHAR_TIMEOUT_MS))


def reorder(data, default, indices):
    reordered_data = [default] * len(indices)
    for i, index in enumerate(indices):
        if i < len(data):
            reordered_data[index] = data[i]
    return reordered_data


display_indices = list(map(lambda x: ord(x) - ord('a'), display_order))
display_offsets = reorder(display_offsets, 0, display_indices)

#led = machine.Pin("LED", machine.Pin.OUT)

#def blink(timer):
#    led.toggle()

#timer = Timer()
#timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

test_words = list([
    "abcdefgh", "Hi", "$#& ", "Hello", "World", "Spirit", "Purple", "Marvel",
    "Garden", "Elephant", "Football", "Birthday", "Rainbow", "Keyboard",
    "Necklace", "Positive", "Mountain", "Campaign", "Hospital", "Orbit",
    "Pepper", "874512", "365498", "720156", "935827", "$$$$$$", "$#$#$#",
    "&&&&&&"
])

test_chars = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#") + list(
    reversed("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "))
#test_words = list(map(lambda s: s * len(display_order), test_chars))

queue = 100 * test_words


def read_queued_frame():
    sleep(2)

    rpm = random.randint(5, 15)
    display_mode = random.randint(0, 2)
    letters = queue.pop(0)
    print("display", letters, "rpm", rpm, "display_mode", display_mode)

    return UartFrame(UartProtocol.CMD_SET,
                     0,
                     rpm=rpm,
                     display_mode=display_mode,
                     letters=''.join(reorder(letters, ' ', display_indices)),
                     offsets=display_offsets)


def read_time_frame():
    (year, month, mday, hour, minute, second, weekday, yearday) = localtime()
    print("second", second)
    sleep(60 - second)

    (year, month, mday, hour, minute, second, weekday, yearday) = localtime()
    letters = "{:02d}: {:02d}".format(hour, minute)

    return UartFrame(UartProtocol.CMD_SET,
                     0,
                     rpm=12,
                     display_mode=Display.BEGIN_IN_SYNC,
                     letters=''.join(reorder(letters, ' ', display_indices)),
                     offsets=display_offsets)


next_frame = read_time_frame if is_picow else None
#next_frame = read_queued_frame if is_picow else None

poll = select.poll()
poll.register(uart_input.uart, select.POLLIN)

seq_in = 0
seq_out = 0

while True:
    try:
        gc.collect()

        if next_frame:
            frame = next_frame()

        else:
            for sock, event in poll.ipoll():
                if event and select.POLLIN:
                    if sock == uart_input.uart:
                        frame = uart_input.uart_read(UartProtocol.CMD_SET)

        gc.collect()
        print('mem_free:', gc.mem_free())

        seq_in = frame.seq
        seq_out += 1

        letters = frame.letters[:display.num_modules()]
        offsets = frame.offsets[:display.num_modules()]
        letters_overflow = frame.letters[display.num_modules():]
        offsets_overflow = frame.offsets[display.num_modules():]
        print('letters:', letters, letters_overflow)

        display.set_rpm(frame.rpm)
        display.set_offsets(offsets)
        display.set_letters(letters, frame.display_mode)
        max_steps = max([display.get_max_steps(), frame.steps])

        if letters_overflow:
            uart_output.uart_write(
                UartFrame(UartProtocol.CMD_SET,
                          seq_out,
                          steps=max_steps,
                          rpm=frame.rpm,
                          display_mode=frame.display_mode,
                          letters=letters_overflow,
                          offsets=offsets_overflow))

            frame = uart_output.uart_read(UartProtocol.CMD_ACK, seq_out,
                                          UART_FRAME_TIMEOUT_MS)
            if frame:
                max_steps = frame.steps

        uart_input.uart_write(
            UartFrame(UartProtocol.CMD_ACK, seq_in, steps=max_steps))

        neopixel.fill((random.randint(0, 255), random.randint(0, 255),
                       random.randint(0, 255)))
        neopixel.write()

        display.rotate_until_stopped(max_steps)

        status = display.get_status()

        if letters_overflow:
            frame = uart_output.uart_read(UartProtocol.CMD_END, seq_out,
                                          UART_FRAME_TIMEOUT_MS)
            status = '{},{}'.format(status, frame.letters if frame else '?')

        print('status:', status)
        uart_input.uart_write(
            UartFrame(UartProtocol.CMD_END, seq_in, letters=status))

    except Exception as e:
        sys.print_exception(e)
