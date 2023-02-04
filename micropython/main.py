import gc
from machine import Pin, Timer, UART
import select
from time import ticks_diff, ticks_ms

from Cluster import Cluster
from ModuleGpio import ModuleGpio
from UartProtocol import UartProtocol

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
                  timeout=100)
uart_output = UART(1,
                   baudrate=38400,
                   tx=Pin(4, Pin.IN, Pin.PULL_UP),
                   rx=Pin(5, Pin.OUT),
                   timeout=100)

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
        "my", "up", "me", "as", "he", "we", "so", "be", "by", "or", "do", "if",
        "hi", "bi", "ex", "ok", "18", "21", "99", "$$", "&&", "##"
    ]))

#message = list(map(lambda s: s * num_modules, test_chars))
queue = 100 * test_words if picow else []

uart_protocol = UartProtocol()

poll = select.poll()
poll.register(uart_input, select.POLLIN)

poll_uart_output = select.poll()
poll_uart_output.register(uart_output, select.POLLIN)

seq_in = 0
seq_out = 0

while True:
    try:
        gc.collect()

        for sock, event in poll.ipoll(1000):
            if event and select.POLLIN:
                if sock == uart_input:
                    frame = uart_protocol.uart_read(uart_input,
                                                    UartProtocol.CMD_SET)
                    if frame:
                        seq_in = frame.seq
                        queue = [frame.letters.decode('ascii')]

        if not queue:
            continue

        letters = queue.pop(0)
        letters_overflow = letters[cluster.num_modules():]
        print('letters: ', letters, letters_overflow)

        if letters_overflow:
            uart_protocol.uart_write(uart_output, UartProtocol.CMD_SET,
                                     seq_out, letters_overflow)

        cluster.set_letters(letters)
        max_steps = cluster.steps_to_rotate()

        cluster.rotate_until_stopped(max_steps)

        status = cluster.get_status()
        start = ticks_ms()

        if letters_overflow:
            # timeout 4s to allow for full rotation of a module
            if poll_uart_output.poll(4000):
                frame = uart_protocol.uart_read(uart_output,
                                                UartProtocol.CMD_END, seq_out)
                status = '{},{}'.format(status,
                                        frame.letters if frame else '?')
            else:
                status = '{},!'.format(status)

        print('status:', status, 'mem_free:', gc.mem_free(), 'ticks',
              ticks_diff(ticks_ms(), start))
        uart_protocol.uart_write(uart_input, UartProtocol.CMD_END, seq_in,
                                 status)
        seq_out += 1
    except Exception as e:
        print('Exception:', e)
