import time

from ProviderMotion import ProviderMotion
from typing import Union

from ProviderArt import ProviderArt
from ProviderClock import ProviderClock

from Display import Display
from Httpd import Httpd, decode_url_encoded
from Message import Message, LETTERS
from Source import Source


class SourceHttpd(Source):
    def __init__(self, display: Display, port: int = 0):
        self.display = display
        self.display_queue = []
        self.display_data = None
        self.scheduled_time = None

        self.providers = {
            "{CLOCK}": ProviderClock(),
            "{ART}": ProviderArt(),
            "{MOTION}": ProviderMotion(),
        }

        self.httpd = Httpd({
            "POST /display": lambda request: self.process_post_display(request)
        }, port)

    def process_post_display(self, request: str) -> int:
        body = request.decode('utf-8').split('\r\n\r\n', 1)[1]
        form_data = decode_url_encoded(body)

        if 'text' in form_data:
            self.display_queue.append(form_data)
            return 200, bytes()

        return 400, bytes()

    def display_data_to_message(self, display_data: {str: str}, physical_motor_position: [int]):
        motor_position = self.display.physical_to_virtual(physical_motor_position)

        display_word = display_data['text'].upper()
        rpm = int(display_data.get('rpm', 15))
        seq = display_data.get('seq', None)

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

            if seq == "random":
                message = Message.word_random(rpm, word, 2)
            elif seq == "sweep":
                message = Message.word_sweep(rpm, word, 2)
            elif seq == "diagonal_sweep":
                message = Message.word_diagonal_sweep(rpm, word, 2)
            elif seq == "end_in_sync":
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

        self.httpd.poll(1000 if is_stopped else 0)
