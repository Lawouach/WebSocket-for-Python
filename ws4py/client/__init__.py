# -*- coding: utf-8 -*-
from base64 import b64encode, b64encode
import os
from hashlib import sha1
import socket
from urlparse import urlsplit
import threading
import types

from ws4py.streaming import Stream
from ws4py.exc import HandshakeError

__all__ = ['WebSocketClient', 'WebSocketBaseClient']

WS_KEY = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class WebSocketBaseClient(object):
    def __init__(self, url, protocols=None, version='8'):
        self.stream = Stream()
        self.url = url
        self.protocols = protocols
        self.version = version
        self.key = b64encode(os.urandom(16))
        
        self._client_terminated = False
        self._server_terminated = False
        
    @property
    def handshake_headers(self):
        parts = urlsplit(self.url)
        host = parts.netloc
        if ':' in host:
            host, port = parts.netloc.split(':')
            
        headers = [
            ('Host', host),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', self.key),
            ('Sec-WebSocket-Origin', self.url),
            ('Sec-WebSocket-Version', self.version)
            ]
        
        if self.protocols:
            headers.append(('Sec-WebSocket-Protocol', ','.join(self.protocols)))

        return headers

    @property
    def handshake_request(self):
        parts = urlsplit(self.url)
        
        headers = self.handshake_headers
        request = ["GET %s HTTP/1.1" % parts.path]
        for header, value in headers:
            request.append("%s: %s" % (header, value))
        request.append('\r\n')

        return '\r\n'.join(request)

    def process_response_line(self, response_line):
        protocol, code, status = response_line.split(' ', 2)
        if code != '101':
            raise HandshakeError("Invalid response status: %s %s" % (code, status))

    def process_handshake_header(self, headers):
        protocols = []
        extensions = []

        headers = headers.strip()
        
        for header_line in headers.split('\r\n'):
            header, value = header_line.split(':')
            header = header.strip().lower()
            value = value.strip().lower()
            
            if header == 'upgrade' and value != 'websocket':
                raise HandshakeError("Invalid Upgrade header: %s" % value)

            elif header == 'connection' and value != 'upgrade':
                raise HandshakeError("Invalid Connection header: %s" % value)

            elif header == 'sec-websocket-accept':
                match = b64encode(sha1(self.key + WS_KEY).digest())
                if value != match.lower():
                    raise HandshakeError("Invalid challenge response: %s" % value)

            elif header == 'sec-websocket-protocol':
                protocols = ','.join(value)

            elif header == 'sec-websocket-extensions':
                extensions = ','.join(value)

        return protocols, extensions

    @property
    def terminated(self):
        return self._client_terminated is True and self._server_terminated is True

    def close(self, reason=''):
        if not self._client_terminated:
            self._client_terminated = True
            self._write_to_connection(self.stream.close(reason=reason))

    def connect(self):
        raise NotImplemented()

    def _write_to_connection(self, bytes):
        raise NotImplemented()

    def _read_from_connection(self, amount):
        raise NotImplemented()

    def _close_connection(self):
        raise NotImplemented()
               
    def send(self, payload, binary=False):
        if isinstance(payload, basestring):
            if not binary:
                self._write_to_connection(self.stream.text_message(payload).single())
            else:
                self._write_to_connection(self.stream.binary_message(payload).single())
                
        elif type(payload) == types.GeneratorType:
            bytes = payload.next()
            first = True
            for chunk in payload:
                if not binary:
                    self._write_to_connection(self.stream.text_message(bytes).fragment(first=first))
                else:
                    self._write_to_connection(self.stream.binary_message(payload).fragment(first=first))
                bytes = chunk
                first = False
            if not binary:
                self._write_to_connection(self.stream.text_message(bytes).fragment(last=True))
            else:
                self._write_to_connection(self.stream.text_message(bytes).fragment(last=True))

    def received_message(self, m):
        pass
        
    def opened(self, protocols, extensions):
        pass

    def closed(self, code, reason):
        pass
        
class WebSocketClient(WebSocketBaseClient):
    def __init__(self, url, protocols=None, version='8'):
        WebSocketBaseClient.__init__(self, url, protocols=protocols, version=version)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.settimeout(3)

        self._th = threading.Thread(target=self._receive)
        self._lock = threading.Lock()

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
                    if not self._client_terminated:
                        next_size = 256
                        self.close()
                    else:
                        self._server_terminated = True
                        self.sock.close()
                        self.closed(s.closing.code, s.closing.reason)

                if s.has_messages:
                    self.received_message(s.messages.pop())
            
    def _write_to_connection(self, bytes):
        return self.sock.sendall(bytes)

    def _read_from_connection(self, amount):
        return self.sock.recv(amount)
        
    def _close_connection(self):
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

if __name__ == '__main__':
    class MyClient(WebSocketClient):
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

    try:
        ws = MyClient('http://192.168.0.10:8888/', protocols=['http-only', 'chat'])
        ws.connect()
    except KeyboardInterrupt:
        ws.close()
