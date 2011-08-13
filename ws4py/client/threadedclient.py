# -*- coding: utf-8 -*-
import os
from urlparse import urlsplit
import socket
import threading

from ws4py.client import WebSocketBaseClient
from ws4py.handler.threadedhandler import WebSocketHandler
from ws4py.exc import HandshakeError

__all__ = ['WebSocketClient']

class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, sock=None, protocols=None, version='8'):
        WebSocketBaseClient.__init__(self, url, protocols=protocols, version=version)
        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.settimeout(3)
        self.sock = sock

        self._lock = threading.Lock()
        self._th = threading.Thread(target=self._receive)

    def write_to_connection(self, bytes):
        return self.sock.sendall(bytes)

    def read_from_connection(self, amount):
        return self.sock.recv(amount)
        
    def close_connection(self):
        self.sock.close()
        
    def connect(self):
        parts = urlsplit(self.url)
        host, port = parts.netloc, 80
        if ':' in host:
            host, port = parts.netloc.split(':')
        self.sock.connect((host, int(port)))
        
        self.sock.sendall(self.handshake_request)

        response = ''
        while True:
            bytes = self.sock.recv(128)
            if not bytes:
                break
            response += bytes
            if '\r\n\r\n' in response:
                break

        if not response:
            self.sock.close()
            raise HandshakeError("Invalid response")

        headers, _, body = response.partition('\r\n\r\n')
        response_line, _, headers = headers.partition('\r\n')

        self.__buffer = body

        try:
            self.process_response_line(response_line)
            protocols, extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.sock.close()
            raise
        
        self._th.start()
        self.opened(protocols, extensions)

    def _receive(self):
        next_size = 256
        while not self.terminated:
            try:
                bytes = self.sock.recv(next_size)
            except socket.timeout:
                continue

            with self._lock:
                s = self.stream
                next_size = s.parser.send(bytes)

                for ping in s.pings:
                    self.sock.sendall(s.pong(ping.data))
                s.pings = []

                if s.closing:
                    if not self.client_terminated:
                        next_size = 256
                        self.close()
                    else:
                        self.server_terminated = True
                        self.close_connection()
                        self.closed(s.closing.code, s.closing.reason)

                if s.has_messages:
                    self.received_message(s.messages.pop())
            

if __name__ == '__main__':
    import time
    
    class MyClient(WebSocketClient):
        def opened(self, protocols, extensions):
            WebSocketClient.opened(self, protocols, extensions)
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

    try:
        ws = MyClient('http://192.168.0.10:8888/', protocols=['http-only', 'chat'])
        ws.connect()
    except KeyboardInterrupt:
        ws.close()
