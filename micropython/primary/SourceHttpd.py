import time
import json

from typing import Union, Tuple, Dict

from Message import Message
from Source import Source
from provider.Provider import Provider
from primary.Crontab import find_matching_crontab
from primary.Display import Display
from primary.Httpd import Httpd, decode_url_encoded
from primary.Wifi import Wifi


SOURCE_CRONTAB = "CRONTAB"
SOURCE_OVERRIDE = "OVERRIDE"


class SourceHttpd(Source):
    def __init__(self, wifi: Wifi, display: Display, providers: Dict[str, Provider], port: int = 0):
        self.wifi = wifi
        self.display = display
        self.providers = providers
        self.default_provider = Provider()

        # Trackers for what to display
        self.current_data = None
        self.current_source = SOURCE_CRONTAB
        self.scheduled_time = None

        # Crontab
        self.last_crontab_data = None
        self.crontab = self.load_crontab()

        # Override
        self.override_message = None
        self.override_expiry = None
        self.override_duration_ms = 30_000  # 30 seconds

        # HTTP server
        self.httpd = Httpd({
            "POST /display": lambda req: self.process_post_display(req),
        }, port)

    def load_crontab(self) -> list:
        try:
            with open('crontab.txt', 'r') as f:
                return [line.rstrip('\n') for line in f.readlines()]
        except OSError:
            return []

    def process_post_display(self, request: str) -> Tuple[int, bytes, str]:
        body = request.decode('utf-8').split('\r\n\r\n', 1)[1]
        form_data = decode_url_encoded(body)
        if 'text' in form_data:
            self.override_message = form_data
            print("[HTTP] Received override message:", form_data)
            return 200, b'', 'text/html'
        return 400, b'', 'text/html'

    def display_data_to_message(self, display_data: Dict[str, str], physical_motor_position: [int]) -> Tuple[Message, int]:
        motor_pos = self.display.physical_to_virtual(physical_motor_position)
        text = display_data['text'].upper()
        provider = self.providers.get(text, self.default_provider)
        message, interval_ms = provider.get_message(text, display_data, self.display, motor_pos)
        return self.display.virtual_to_physical(message), interval_ms

    def load_crontab_message(self):
        current_time = time.localtime()
        time_tuple = (current_time[4], current_time[3], current_time[2], current_time[1], current_time[6])
        crontab_data = find_matching_crontab(time_tuple, self.crontab)

        if crontab_data and crontab_data != self.last_crontab_data:
            try:
                self.current_source = SOURCE_CRONTAB
                self.current_data = json.loads(crontab_data)
                self.scheduled_time = time.ticks_ms()
                self.last_crontab_data = crontab_data
                print("[CRONTAB] New crontab data:", self.current_data)
            except ValueError as e:
                print("[CRONTAB] Invalid JSON:", e)

    def start_override(self):
        if self.override_message:
            self.current_source = SOURCE_OVERRIDE
            self.current_data = self.override_message
            self.scheduled_time = time.ticks_ms()
            self.override_message = None
            print("[OVERRIDE] Starting new override:", self.current_data)

    def check_override_expiry(self):
        if self.current_source == SOURCE_OVERRIDE and self.override_expiry:
            if time.ticks_diff(self.override_expiry, time.ticks_ms()) <= 0:
                self.current_source = SOURCE_CRONTAB
                self.current_data = None
                self.scheduled_time = None
                self.last_crontab_data = None
                self.override_expiry = None
                print("[OVERRIDE] Override expired")

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        self.wifi.connect()
        self.httpd.poll(1000 if is_stopped else 0)

        if not is_stopped:
            return None

        self.check_override_expiry()

        if self.override_message:
            self.start_override()

        if self.current_source == SOURCE_CRONTAB:
            self.load_crontab_message()

        if self.current_data and self.scheduled_time and time.ticks_diff(time.ticks_ms(), self.scheduled_time) >= 0:
            message, interval = self.display_data_to_message(self.current_data, physical_motor_position)
            print(f"[{self.current_source}] Text: {self.current_data['text']}, Next in: {interval or 0}ms")
            self.scheduled_time = time.ticks_add(time.ticks_ms(), interval) if interval else None

            if self.current_source == SOURCE_OVERRIDE:
                self.override_expiry = time.ticks_add(time.ticks_ms(), self.override_duration_ms)

            return message

        return None
