import json
import time

from Wifi import Wifi
from typing import Union, Tuple, List, Dict

from Provider import Provider
from Display import Display
from Httpd import Httpd, decode_url_encoded
from Message import Message, LETTERS
from Source import Source


class SourceHttpd(Source):
    def __init__(self, wifi: Wifi, display: Display, providers: Dict[str, Provider], port: int = 0):
        self.wifi = wifi
        self.display = display
        self.providers = providers
        self.display_queue = []
        self.display_data = None
        self.scheduled_time = None

        self.httpd = Httpd({
            "POST /display": lambda request: self.process_post_display(request),
            "GET /presets": lambda request: self.process_get_presets(request),
        }, port)

    def process_post_display(self, request: str) -> Tuple[int, bytes]:
        body = request.decode('utf-8').split('\r\n\r\n', 1)[1]
        form_data = decode_url_encoded(body)

        if 'text' in form_data:
            self.display_queue.append(form_data)
            return 200, bytes()

        return 400, b''

    def process_get_presets(self, request: str) -> Tuple[int, bytes]:
        return 200, json.dumps(self.presets).encode('utf-8')

    def display_data_to_message(self, display_data: {str: str}, physical_motor_position: [int]):
        motor_position = self.display.physical_to_virtual(physical_motor_position)

        display_word = display_data['text'].upper()
        rpm = int(display_data.get('rpm', 15))
        order = display_data.get('order', None)

        provider = self.providers.get(display_word)
        if provider:
            word_or_message, interval_ms = provider.get_word_or_message(display_word, rpm, self.display, motor_position)
        else:
            # filter characters using LETTERS
            word_or_message = ''.join(char for char in display_word if char in LETTERS)
            interval_ms = None

        if isinstance(word_or_message, str):
            word = self.display.adjust_word(word_or_message)
            print('word: \'{}\' rpm: {}'.format(word, rpm))

            if order == "random":
                message = Message.word_random(rpm, word, 2)
            elif order == "sweep":
                message = Message.word_sweep(rpm, word, 2)
            elif order == "diagonal_sweep":
                message = Message.word_diagonal_sweep(rpm, word, 2)
            elif order == "end_in_sync":
                message = Message.word_end_in_sync(rpm, word, motor_position)
            else:
                message = Message.word_start_in_sync(rpm, word)
        else:
            message = word_or_message

        return self.display.virtual_to_physical(message), interval_ms

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        if is_stopped:
            if self.display_queue:
                self.display_data = self.display_queue.pop(0)
                self.scheduled_time = time.ticks_ms()

            if self.scheduled_time and time.ticks_diff(self.scheduled_time, time.ticks_ms()) <= 0:
                message, interval_ms = self.display_data_to_message(self.display_data, physical_motor_position)
                self.scheduled_time = time.ticks_add(time.ticks_ms(), interval_ms) if interval_ms else None
                return message

        self.wifi.connect()
        self.httpd.poll(1000 if is_stopped else 0)
