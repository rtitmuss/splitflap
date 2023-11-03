from typing import Callable

from micropython import const
import select
import socket


_RESPONSE_200 = const("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_400 = const("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_404 = const("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_500 = const("HTTP/1.1 500 Server Error\r\nContent-Type: text/html\r\n\r\n")


def decode_encoded_str(s: str) -> str:
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


def decode_url_encoded(url_encoded: str) -> {str: str}:
    data = {}
    pairs = url_encoded.split('&')

    for pair in pairs:
        key_value = pair.split('=')
        if len(key_value) == 2:
            key, value = key_value
            data[decode_encoded_str(key)] = decode_encoded_str(value)

    return data


def _process_http_get(request: str) -> int:
    url = request.split()[1].decode('utf-8')

    file_path = "www/index.html" if url == "/" else "www/" + url
    try:
        with open(file_path, "rb") as file:
            return 200, file.read()
    except OSError:
        print('not found:', url)
        return 404, b''


class Httpd():
    def __init__(self, handlers: {str: Callable}, port: int = 0):
        self.handlers = handlers.copy()
        self.handlers["GET /"] = _process_http_get

        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if port:
            server_socket.bind(('0.0.0.0', port))

        server_socket.listen(5)
        self.server_socket = server_socket

        self.select_poll = select.poll()
        self.select_poll.register(server_socket, select.POLLIN)

    def process_http_request(self, request: str) -> str:
        for url_prefix, handler in self.handlers.items():
            if request.startswith(url_prefix):
                try:
                    status, body = handler(request)

                    if status == 200:
                        return _RESPONSE_200.encode('utf-8') + body
                    elif status == 404:
                        return _RESPONSE_404.encode('utf-8')
                    else:
                        return _RESPONSE_400.encode('utf-8')
                except Exception as e:
                    print(e)
                    return _RESPONSE_500.encode('utf-8')

        return _RESPONSE_400.encode('utf-8')

    def poll(self, timeout: int) -> None:
        events = self.select_poll.poll(timeout)

        for socket, event in events:
            if socket == self.server_socket:
                client_socket, client_address = self.server_socket.accept()
                self.select_poll.register(client_socket, select.POLLIN)
            elif event & select.POLLIN:
                request = socket.recv(1024)
                if request:
                    response = self.process_http_request(request)
                    socket.send(response)
                socket.close()
                self.select_poll.unregister(socket)
