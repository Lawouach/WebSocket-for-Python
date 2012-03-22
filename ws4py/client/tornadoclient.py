# -*- coding: utf-8 -*-
import socket
from urlparse import urlsplit
import ssl

from tornado import iostream, escape
from ws4py.client import WebSocketBaseClient
from ws4py.exc import HandshakeError

__all__ = ['TornadoWebSocketClient']

class TornadoWebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, extensions=None, io_loop=None):
        WebSocketBaseClient.__init__(self, url, protocols, extensions)
        parts = urlsplit(self.url)
        if parts.scheme == "wss":
            self.sock = ssl.wrap_socket(self.sock,
                    do_handshake_on_connect=False)
            self.io = iostream.SSLIOStream(self.sock, io_loop)
        else:
            self.io = iostream.IOStream(self.sock, io_loop)
        self.sender = self.io.write
        self.io_loop = io_loop

    def connect(self):
        parts = urlsplit(self.url)
        host, port = parts.netloc, 80
        if ':' in host:
            host, port = parts.netloc.split(':')
        self.io.set_close_callback(self.__connection_refused)
        self.io.connect((host, int(port)), self.__send_handshake)

    def __connection_refused(self, *args, **kwargs):
        self.server_terminated = True
        self.closed(1005, 'Connection refused')

    def __send_handshake(self):
        self.io.set_close_callback(self.__connection_closed)
        self.io.write(escape.utf8(self.handshake_request),
                      self.__handshake_sent)

    def __connection_closed(self, *args, **kwargs):
        self.server_terminated = True
        self.closed(1006, 'Connection closed during handshake')

    def __handshake_sent(self):
        self.io.read_until("\r\n\r\n", self.__handshake_completed)

    def __handshake_completed(self, data):
        self.io.set_close_callback(None)
        try:
            response_line, _, headers = data.partition('\r\n')
            self.process_response_line(response_line)
            protocols, extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.close_connection()
            raise

        self.opened()
        self.io.set_close_callback(self.__stream_closed)
        self.io.read_bytes(self.reading_buffer_size, self.__fetch_more)

    def __fetch_more(self, bytes):
        try:
            should_continue = self.process(bytes)
        except:
            should_continue = False

        if should_continue:
            self.io.read_bytes(self.reading_buffer_size, self.__fetch_more)
        else:
            self.__gracefully_terminate()

    def __gracefully_terminate(self):
        self.client_terminated = self.server_terminated = True

        try:
            if not self.stream.closing:
                self.closed(1006)
        finally:
            self.close_connection()

    def __stream_closed(self, *args, **kwargs):
        self.io.set_close_callback(None)
        code = 1006
        reason = None
        if self.stream.closing:
            code, reason = self.stream.closing.code, self.stream.closing.reason
        self.closed(code, reason)
        self._cleanup()

    def close_connection(self):
        self.io.close()

if __name__ == '__main__':
    from tornado import ioloop

    class MyClient(TornadoWebSocketClient):
        def opened(self):
            def data_provider():
                for i in range(1, 200, 25):
                    yield "#" * i

            self.send(data_provider())

            for i in range(0, 200, 25):
                self.send("*" * i)

        def received_message(self, m):
            print m, len(str(m))
            if len(str(m)) == 175:
                self.close()

        def closed(self, code, reason=None):
            ioloop.IOLoop.instance().stop()

    ws = MyClient('http://localhost:9000/ws', protocols=['http-only', 'chat'])
    ws.connect()

    ioloop.IOLoop.instance().start()

