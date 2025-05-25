from collections import OrderedDict

from typing import Callable, Tuple

from micropython import const
import select
import socket


_RESPONSE_200 = const("HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n")
_RESPONSE_400 = const("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_404 = const("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")
_RESPONSE_500 = const("HTTP/1.1 500 Server Error\r\nContent-Type: text/html\r\n\r\n")

_CONTENT_TYPE = {
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".ico": "image/vnd.microsoft.icon",
}

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


def parse_headers(header_bytes):
    header_text = header_bytes.decode()
    lines = header_text.split('\r\n')
    if not lines[0]:
        raise ValueError("Empty request line")
    request_line = lines[0]
    parts = request_line.split(' ')
    if len(parts) != 3:
        raise ValueError(f"Invalid request line: {request_line}")
    method, url, _ = parts
    headers = {}
    for line in lines[1:]:
        if ': ' in line:
            k, v = line.split(': ', 1)
            headers[k.lower()] = v
    return method, url, headers


def _process_http_get(url: str, body: bytes) -> Tuple[int, bytes, str]:
    # Ignore body for GET requests
    url_extension = url[url.rfind("."):]
    content_type = _CONTENT_TYPE.get(url_extension, "text/html")

    file_path = "www/index.html" if url == "/" else "www/" + url
    try:
        with open(file_path, "rb") as file:
            return 200, file.read(), content_type
    except OSError:
        print('not found:', url)
        return 404, b'', ''


class Httpd():
    def __init__(self, handlers: {str: Callable}, port: int = 0):
        self.handlers = OrderedDict(handlers)
        self.handlers["GET /"] = _process_http_get

        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if port:
            server_socket.bind(('0.0.0.0', port))

        server_socket.listen(5)
        self.server_socket = server_socket

        self.select_poll = select.poll()
        self.select_poll.register(server_socket, select.POLLIN)

    def process_http_request(self, method: str, url: str, body: bytes) -> bytes:
        handler_key = f"{method} {url}"
        for url_prefix, handler in self.handlers.items():
            if handler_key.startswith(url_prefix):
                status, body, content_type = handler(url, body)

                if status == 200:
                    return _RESPONSE_200.format(content_type or "text/html").encode('utf-8') + body
                elif status == 404:
                    return _RESPONSE_404.encode('utf-8')
                else:
                    return _RESPONSE_400.encode('utf-8')

        return _RESPONSE_400.encode('utf-8')

    def poll(self, timeout: int) -> None:
        events = self.select_poll.poll(timeout)

        for sock, event in events:
            if sock == self.server_socket:
                client_socket, client_address = self.server_socket.accept()
                self.select_poll.register(client_socket, select.POLLIN)
            elif event & select.POLLIN:
                try:
                    request_buffer = bytearray()
                    # Read headers
                    while True:
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        request_buffer.extend(chunk)

                        if b'\r\n\r\n' in request_buffer:
                            break

                    if request_buffer:
                        header_end = request_buffer.find(b'\r\n\r\n')
                        header_bytes = request_buffer[:header_end]
                        method, url, headers = parse_headers(header_bytes)

                        content_length = int(headers.get('content-length', '0'))
                        body_start = header_end + 4
                        body = request_buffer[body_start:]

                        # Read remaining body data if needed
                        remaining = content_length - len(body)
                        while remaining > 0:
                            chunk = sock.recv(min(1024, remaining))
                            if not chunk:
                                break
                            body.extend(chunk)
                            remaining -= len(chunk)

                        response = self.process_http_request(method, url, body)
                        sock.sendall(response)

                except Exception as e:
                    print(f"Error handling request: {e}")
                    try:
                        sock.sendall(_RESPONSE_500.encode('utf-8'))
                    except:
                        pass

                finally:
                    sock.close()
                    self.select_poll.unregister(sock)
