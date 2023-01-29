from machine import Pin, Timer, UART
import select

from Cluster import Cluster
from ModuleGpio import ModuleGpio

cluster = Cluster(
    Pin(3, Pin.OUT, value=0),
    [
        ModuleGpio(2, 28, 27, 26, 22, 1),
        #    ModuleGpio(14, 18, 19, 20, 21, 0),
        #ModuleGpio(1, 9, 8, 7, 6, 0),
        #    ModuleGpio(15, 10, 11, 12, 13, 1)
    ])

uart_input = UART(1,
                  baudrate=38400,
                  tx=Pin(4, Pin.IN, Pin.PULL_UP),
                  rx=Pin(5, Pin.OUT, Pin.PULL_UP))
uart_output = UART(0,
                   baudrate=38400,
                   tx=Pin(16, Pin.IN, Pin.PULL_UP),
                   rx=Pin(17, Pin.OUT, Pin.PULL_UP))

led = machine.Pin("LED", machine.Pin.OUT)


def blink(timer):
    led.toggle()


timer = Timer()
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

test_chars = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#") + list(
    reversed("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "))

test_words = [
    "in", "of", "to", "is", "it", "on", "no", "us", "at", "un", "go", "an",
    "my", "up", "me", "as", "he", "we", "so", "be", "by", "or", "do", "if ",
    "hi", "bi", "ex", "ok", "18", "21", "99"
]

#message = list(map(lambda s: s * num_modules, test_chars))
queue = 100 * test_words


def uart_read_line(uart):
    buf = bytearray()
    while True:
        c = uart.read(1)
        if c:
            buf = buf + c
            if c == b'\n':
                return buf.decode('ascii')


poller = select.poll()
poller.register(uart_input, select.POLLIN)

while True:
    for sock, event in poller.ipoll(1000):
        if event and select.POLLIN:
            if sock == uart_input:
                letters = uart_read_line(uart_input)
                queue.insert(0, letters)

    if not queue:
        continue

    letters = queue.pop(0).strip()
    letters_overflow = letters[cluster.num_modules():]

    print('letters: ', letters, letters_overflow)

    if letters_overflow:
        uart_output.write('{}\n'.format(letters_overflow))

    cluster.set_letters(letters)
    max_steps = cluster.steps_to_rotate()
    cluster.rotate_until_stopped(max_steps)

    if letters_overflow:
        uart_read_line(uart_output)

    uart_input.write('ok\n')
