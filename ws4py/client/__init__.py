# -*- coding: utf-8 -*-
from base64 import b64encode, b64encode
from hashlib import sha1
import os
import socket
import ssl
import types
from urlparse import urlsplit
import json

from ws4py import WS_KEY, WS_VERSION
from ws4py.exc import HandshakeError
from ws4py.websocket import WebSocket

__all__ = ['WebSocketBaseClient']

class WebSocketBaseClient(WebSocket):
    def __init__(self, url, protocols, extensions):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        WebSocket.__init__(self, sock, protocols=protocols, extensions=extensions)
        self.stream.always_mask = True
        self.stream.expect_masking = False
        self.key = b64encode(os.urandom(16))
        self.url = url
        
    def close(self, code=1000, reason=''):
        if not self.client_terminated:
            self.client_terminated = True
            self.sender(self.stream.close(code=code, reason=reason).single(mask=True))

    def connect(self):
        #self.sock.settimeout(3)
        parts = urlsplit(self.url)
        host, port = parts.netloc, 80
        if parts.scheme == "wss":
            # default port is now 443; upgrade self.sender to send ssl
            self.sock = ssl.wrap_socket(self.sock)
            port = 443
            self.sender = self.sock.sendall
        if ':' in host:
            host, port = parts.netloc.split(':')
        self.sock.connect((host, int(port)))
        
        self.sender(self.handshake_request)


        response = ''
        while True:
            bytes = self.sock.recv(128)
            if not bytes:
                break
            response += bytes
            if '\r\n\r\n' in response:
                break

        if not response:
            self.close_connection()
            raise HandshakeError("Invalid response")

        headers, _, body = response.partition('\r\n\r\n')
        response_line, _, headers = headers.partition('\r\n')

        self.__buffer = body

        try:
            self.process_response_line(response_line)
            self.protocols, self.extensions = self.process_handshake_header(headers)
        except HandshakeError:
            self.close_connection()
            raise

        self.handshake_ok()

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
            ('Sec-WebSocket-Version', str(max(WS_VERSION)))
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
            header, value = header_line.split(':', 1)
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
