import gc
from machine import Pin, Timer, UART
from neopixel import NeoPixel
import random
import select
import sys
from time import sleep, ticks_diff, ticks_ms

from Cluster import Cluster
from ModuleGpio import ModuleGpio
from UartProtocol import UartProtocol

# physical module order when displaying alphabet
#display_order = 'abcdefgh'
display_order = 'febahgdc'

display_indices = list(map(lambda x: ord(x) - ord('a'), display_order))

is_picow = True
try:
    import network
except ImportError:
    is_picow = False

cluster = Cluster(Pin(3, Pin.OUT, value=0), [
    ModuleGpio(2, 28, 27, 26, 22),
    ModuleGpio(14, 18, 19, 20, 21),
    ModuleGpio(1, 9, 8, 7, 6),
    ModuleGpio(15, 10, 11, 12, 13)
])


# invert neopixel data as a logic inverter is used to boost to 5v
class InvertedNeoPixel(NeoPixel):

    def write(self):
        for i in range(len(self.buf)):
            self.buf[i] = ~self.buf[i]
        super().write()
        self.pin.high()


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


def reorder_letters(letters, indices):
    reordered_letters = [' '] * len(indices)
    for i, index in enumerate(indices):
        if i < len(letters):
            reordered_letters[index] = letters[i]
    return ''.join(reordered_letters)


led = machine.Pin("LED", machine.Pin.OUT)


def blink(timer):
    led.toggle()


timer = Timer()
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

# todo: duplicate letters until I have printed more modules
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

queue = 100 * test_words if is_picow else []

poll = select.poll()
poll.register(uart_input.uart, select.POLLIN)

seq_in = 0
seq_out = 0

while True:
    try:
        gc.collect()

        if queue:
            sleep(2)
            letters = reorder_letters(queue.pop(0), display_indices)
            max_steps_in = 0  # Todo add to queue

        else:
            for sock, event in poll.ipoll():
                if event and select.POLLIN:
                    if sock == uart_input.uart:
                        frame = uart_input.uart_read(UartProtocol.CMD_SET)
                        if frame:
                            seq_in = frame.seq
                            letters = frame.letters.decode('ascii')
                            max_steps_in = frame.steps

        gc.collect()
        print('mem_free:', gc.mem_free())

        seq_out += 1

        letters_overflow = letters[cluster.num_modules():]
        print('letters:', letters[:cluster.num_modules()], letters_overflow)

        cluster.set_letters(letters)
        max_steps = max([cluster.get_max_steps(), max_steps_in])

        if letters_overflow:
            uart_output.uart_write(UartProtocol.CMD_SET, seq_out, max_steps,
                                   letters_overflow)

            frame = uart_output.uart_read(UartProtocol.CMD_ACK, seq_out,
                                          UART_FRAME_TIMEOUT_MS)
            if frame:
                max_steps = frame.steps

        uart_input.uart_write(UartProtocol.CMD_ACK, seq_in, max_steps, '')

        neopixel.fill((random.randint(0, 255), random.randint(0, 255),
                       random.randint(0, 255)))
        neopixel.write()

        cluster.rotate_until_stopped(max_steps)

        status = cluster.get_status()

        if letters_overflow:
            frame = uart_output.uart_read(UartProtocol.CMD_END, seq_out,
                                          UART_FRAME_TIMEOUT_MS)
            status = '{},{}'.format(status, frame.letters if frame else '?')

        print('status:', status)
        uart_input.uart_write(UartProtocol.CMD_END, seq_in, 0, status)
    except Exception as e:
        sys.print_exception(e)
