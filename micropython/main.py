from machine import Pin
import time

from Cluster import Cluster
from ModuleGpio import ModuleGpio

cluster = Cluster(
    Pin(3, Pin.OUT, value=0),
    [
        ModuleGpio(2, 28, 27, 26, 22, 1),
        #    ModuleGpio(14, 18, 19, 20, 21, 0),
        ModuleGpio(1, 9, 8, 7, 6, 0),
        #    ModuleGpio(15, 10, 11, 12, 13, 1)
    ])

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

while True:
    print('rotate to {}'.format(message[message_idx]))

    cluster.set_letters(message[message_idx])
    max_steps = cluster.steps_to_rotate()
    cluster.rotate_until_stopped(max_steps)

    message_idx = (message_idx + 1) % len(message)

    time.sleep(1)
