from machine import Pin, Timer, UART
import select
from time import ticks_diff, ticks_ms

from Cluster import Cluster
from ModuleGpio import ModuleGpio

picow = True
try:
    import network
except ImportError:
    picow = False

cluster = Cluster(Pin(3, Pin.OUT, value=0), [
    ModuleGpio(2, 28, 27, 26, 22, 1),
    ModuleGpio(14, 18, 19, 20, 21, 0),
    ModuleGpio(1, 9, 8, 7, 6, 0),
    ModuleGpio(15, 10, 11, 12, 13, 1)
])

uart_input = UART(0,
                  baudrate=38400,
                  tx=Pin(16, Pin.IN, Pin.PULL_UP),
                  rx=Pin(17, Pin.OUT),
                  timeout=1000,
                  timeout_char=100)
uart_output = UART(
    1,
    baudrate=38400,
    tx=Pin(4, Pin.IN, Pin.PULL_UP),
    rx=Pin(5, Pin.OUT),
    timeout=4000,  # allow for full rotation of a module
    timeout_char=100)

led = machine.Pin("LED", machine.Pin.OUT)


def blink(timer):
    led.toggle()


timer = Timer()
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

test_chars = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#") + list(
    reversed("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&# "))

# todo: duplicate letters until I have printed more modules
test_words = list(
    map(lambda x: ''.join([char * 4 for char in x]), [
        "in", "of", "to", "is", "it", "on", "no", "us", "at", "un", "go", "an",
        "my", "up", "me", "as", "he", "we", "so", "be", "by", "or", "do",
        "if ", "hi", "bi", "ex", "ok", "18", "21", "99"
    ]))

#message = list(map(lambda s: s * num_modules, test_chars))
queue = 100 * test_words if picow else []


def uart_readline(uart):
    line = uart.readline()
    if line:
        return line.decode('ascii').strip()
    return None


poller = select.poll()
poller.register(uart_input, select.POLLIN)

while True:
    try:
        for sock, event in poller.ipoll(1000):
            if event and select.POLLIN:
                if sock == uart_input:
                    letters = uart_readline(uart_input)
                    if letters:
                        queue.insert(0, letters)

        if not queue:
            continue

        letters = queue.pop(0)
        letters_overflow = letters[cluster.num_modules():]
        print('letters: ', letters, letters_overflow)

        if letters_overflow:
            uart_output.write('{}\n'.format(letters_overflow))

        cluster.set_letters(letters)
        max_steps = cluster.steps_to_rotate()

        cluster.rotate_until_stopped(max_steps)

        status = cluster.get_status()
        start = ticks_ms()

        if letters_overflow:
            status = '{},{}'.format(status, uart_readline(uart_output) or '?')

        print('status:', status, ticks_diff(ticks_ms(), start))
        uart_input.write('{}\n'.format(status))
    except Exception as e:
        print('Exception:', e)
