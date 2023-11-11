# ignore import errors with unit tests on laptop
try:
    import network
    import ntptime
except ImportError:
    pass

from secret import WIFI


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

                ntptime.settime()

                sta_if = network.WLAN(network.STA_IF)
                print("wifi connected {}".format(sta_if.ifconfig()[0]))

        else:
            status = self.wlan.status()
            if status != network.STAT_CONNECTING:
                if self.is_connected:
                    self.is_connected = False
                    print("wifi disconnected")

                self.wlan.connect(WIFI["SSID"], WIFI["PASSWORD"])
