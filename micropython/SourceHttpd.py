from typing import Union

from Display import Display
from Httpd import Httpd, decode_url_encoded
from Message import Message, LETTERS
from Source import Source


class SourceHttpd(Source):
    def __init__(self, display: Display, port: int = 0):
        self.display = display
        self.queue = []

        self.httpd = Httpd({
            "POST /display": lambda request: self.process_post_display(request)
        }, port)

    def process_post_display(self, request: str) -> int:
        body = request.decode('utf-8').split('\r\n\r\n', 1)[1]
        form_data = decode_url_encoded(body)

        if 'text' in form_data:
            self.queue.append(form_data)
            return 200, bytes()

        return 400, bytes()

    def form_data_to_message(self, form_data: {str: str}, physical_motor_position: [int]):
        motor_position = self.display.physical_to_virtual(physical_motor_position)

        form_word = form_data['text']
        clean_word = ''.join(char for char in form_word.upper() if char in LETTERS)
        word = self.display.adjust_word(clean_word)

        rpm = int(form_data.get('rpm', 15))
        seq = form_data.get('seq', None)

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

        return self.display.virtual_to_physical(message)

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        self.httpd.poll(1000 if is_stopped else 0)

        if is_stopped and self.queue:
            form_data = self.queue.pop(0)
            return self.form_data_to_message(form_data, physical_motor_position)
