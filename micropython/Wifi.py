import network
import ntptime

import secret

def wifi_connect():
    network.hostname("splitflap")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secret.WIFI_SSID, secret.WIFI_PASSWORD)

    ntptime.settime()

    sta_if = network.WLAN(network.STA_IF)
    print("listening on {}:80".format(sta_if.ifconfig()[0]))
