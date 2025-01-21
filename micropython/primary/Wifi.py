from typing import Callable
from time import sleep

# ignore import errors with unit tests on laptop
try:
    import network
    import ntptime
except ImportError:
    pass

from secret import WIFI


def with_backoff(f: Callable, max_retries=5, initial_delay=1, max_delay=60):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            f()
            return True
        except Exception as e:
            sleep(delay)
            delay = min(delay * 2, max_delay)


class Wifi:
    def __init__(self):
        self.is_connected = False

        network.hostname("splitflap")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self):
        if self.wlan.isconnected():
            if not self.is_connected:
                self.is_connected = True

                if not with_backoff(ntptime.settime):
                    print("ntp set time failed")

                sta_if = network.WLAN(network.STA_IF)
                print("wifi connected {}".format(sta_if.ifconfig()[0]))

        else:
            status = self.wlan.status()
            if status != network.STAT_CONNECTING:
                if self.is_connected:
                    self.is_connected = False
                    print("wifi disconnected")

                self.wlan.connect(WIFI["SSID"], WIFI["PASSWORD"])
