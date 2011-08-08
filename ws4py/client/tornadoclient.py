# -*- coding: utf-8 -*-
import socket
from urlparse import urlsplit

from tornado import iostream, escape

from ws4py.client import WebSocketBaseClient
from ws4py.exc import HandshakeError

__all__ = ['TornadoWebSocketClient']

class TornadoWebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, version='8'):
        WebSocketBaseClient.__init__(self, url, protocols=protocols, version=version)
        self.io = iostream.IOStream(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0))

    def connect(self):
        parts = urlsplit(self.url)
        host, port = parts.netloc, 80
        if ':' in host:
            host, port = parts.netloc.split(':')
        self.io.connect((host, int(port)), self.__send_handshake)

    def __send_handshake(self):
        self.io.write(escape.utf8(self.handshake_request),
                      self.__handshake_sent)
        
    def __handshake_sent(self):
        self.io.read_until("\r\n\r\n", self.__handshake_completed)

    def __handshake_completed(self, data):
        try:
            response_line, _, headers = data.partition('\r\n')
            self.process_response_line(response_line)
            protocols, extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.io.close()
            raise
        
        self.opened(protocols, extensions)
        self.io.read_bytes(1, self.__fetch_more)

    def __fetch_more(self, bytes):
        s = self.stream
        next_size = s.parser.send(bytes)
        
        for ping in s.pings:
            self.io.write(s.pong(ping.data))
        s.pings = []

        if s.closing:
            if not self._client_terminated:
                self.close()
            else:
                self._server_terminated = True
                self.io.close()
                self.closed(s.closing.code, s.closing.reason)
                return

        if s.has_messages:
            self.received_message(s.messages.pop())

        self.io.read_bytes(next_size, self.__fetch_more)
     
    def _write_to_connection(self, bytes):
        self.io.write(bytes)

    def _read_from_connection(self, amount):
        self.io.read_bytes(amount, self.__fetch_more)
        
    def _close_connection(self):
        self.io.close()

if __name__ == '__main__':
    from tornado import ioloop

    class MyClient(TornadoWebSocketClient):
        def opened(self, protocols, extensions):
            def data_provider():
                for i in range(1, 200, 25):
                    yield "#" * i

            self.send(data_provider())
            
            for i in range(0, 200, 25):
                self.send("*" * i)

        def received_message(self, m):
            print m, len(str(m))
            if len(str(m)) == 184:
                self.close()

        def closed(self, code, reason):
            ioloop.IOLoop.instance().stop()
                
    ws = MyClient('http://localhost:8888/', protocols=['http-only', 'chat'])
    ws.connect()
        
    ioloop.IOLoop.instance().start()

