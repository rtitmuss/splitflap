import select

from micropython import const

from Display import Display
from typing import Union

import socket

from Message import Message, LETTERS
from Source import Source


_RESPONSE_200 = const("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_400 = const("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_404 = const("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")

def decode_encoded_str(s):
    i = 0
    result = []
    while i < len(s):
        if s[i] == '+':
            result.append(' ')
            i += 1
        elif s[i] == '%':
            try:
                hex_value = int(s[i + 1:i + 3], 16)
                result.append(chr(hex_value))
                i += 3
            except ValueError:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def decode_url_encoded(url_encoded):
    data = {}
    pairs = url_encoded.split('&')

    for pair in pairs:
        key_value = pair.split('=')
        if len(key_value) == 2:
            key, value = key_value
            data[decode_encoded_str(key)] = decode_encoded_str(value)

    return data


class SourceHttpd(Source):
    def __init__(self, display: Display, port: int = 0):
        self.display = display
        self.queue = []

        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if port:
            server_socket.bind(('0.0.0.0', port))

        server_socket.listen(5)
        self.server_socket = server_socket

        self.poll = select.poll()
        self.poll.register(server_socket, select.POLLIN)

    def process_post_display(self, request: str):
        body = request.decode('utf-8').split('\r\n\r\n', 1)[1]
        form_data = decode_url_encoded(body)

        if 'text' in form_data:
            form_word = form_data['text']
            clean_word = ''.join(char for char in form_word.upper() if char in LETTERS)
            word = self.display.adjust_word(clean_word)

            rpm = int(form_data.get('rpm', 15))

            print('word: \'{}\' rpm: {}'.format(word, rpm))
            message = Message.word_start_in_sync(rpm, word)

            self.queue.append(self.display.virtual_to_physical(message))

    def process_http_request(self, request: str) -> str:
        url = request.split()[1].decode('utf-8')

        if request.startswith("POST /display"):
            self.process_post_display(request)
            return _RESPONSE_200.encode('utf-8')

        elif request.startswith("GET /"):
            file_path = "www/index.html" if url == "/" else "www/" + url
            try:
                with open(file_path, "rb") as file:
                    file_contents = file.read()
                    return _RESPONSE_200.encode('utf-8') + file_contents
            except OSError:
                print('not found:', url)
                return _RESPONSE_404.encode('utf-8')

        return _RESPONSE_400.encode('utf-8')

    def load_message(self, is_stopped: bool, physical_motor_position: [int]) -> Union[Message, None]:
        events = self.poll.poll(1000 if is_stopped else 0)

        for socket, event in events:
            if socket == self.server_socket:
                client_socket, client_address = self.server_socket.accept()
                self.poll.register(client_socket, select.POLLIN)
            elif event & select.POLLIN:
                request = socket.recv(1024)
                if request:
                    response = self.process_http_request(request)
                    socket.send(response)
                socket.close()
                self.poll.unregister(socket)

        if is_stopped and self.queue:
            return self.queue.pop(0)
